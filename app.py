import os
import json
import re
import random
import threading
import time
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, Response
from dotenv import load_dotenv
from core.database import db
from core.matching_engine import brain

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", os.urandom(24).hex())

# Security: Content Security Policy and HTTPS enforcement
# Allow FontAwesome and Google Fonts
csp = {
    'default-src': '\'self\'',
    'font-src': [
        '\'self\'',
        'fonts.gstatic.com',
        'cdnjs.cloudflare.com'
    ],
    'style-src': [
        '\'self\'',
        '\'unsafe-inline\'',
        'fonts.googleapis.com',
        'cdnjs.cloudflare.com'
    ],
    'script-src': [
        '\'self\'',
        '\'unsafe-inline\'',
        'cdnjs.cloudflare.com'
    ],
    'img-src': ['\'self\'', 'data:', 'https:']
}
talisman = Talisman(app, content_security_policy=csp, force_https=os.environ.get("FLASK_ENV") == "production")

# API Rate Limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Admin Auth check
def check_admin_auth(username, password):
    correct_user = os.environ.get("ADMIN_USERNAME", "admin")
    correct_pass = os.environ.get("ADMIN_PASSWORD")
    
    # SECURITY: In production, do not allow default password
    if os.environ.get("FLASK_ENV") == "production" and (not correct_pass or correct_pass == "changeme"):
        print("[CRITICAL SECURITY] Production password is not set or using default! Access blocked.")
        return False
        
    return username == correct_user and password == (correct_pass or "changeme")



def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_admin_auth(auth.username, auth.password):
            return Response(
                '접근 권한이 없습니다. 관리자 계정으로 로그인하세요.',
                401,
                {'WWW-Authenticate': 'Basic realm="DreamPocket Admin"'}
            )
        return f(*args, **kwargs)
    return decorated

# Routes

def render_home(preset_region="", preset_major="", seo_title=None, seo_desc=None, url_p=None):
    if not seo_title:
        seo_title = "드림포켓 | 대학생 맞춤 장학금 및 국가장학금 실시간 매칭 검색"
    if not seo_desc:
        seo_desc = "드림포켓에서 나에게 딱 맞는 대학생 맞춤 장학금을 찾아보세요. 국가장학금, 지자체 장학금, 전공별 장학금 혜택을 학점, 소득분위, 거주지로 3초 만에 무료 매칭해 드립니다."
        
    return render_template(
        "index.html", 
        seo_title=seo_title, 
        seo_desc=seo_desc,
        preset_region=preset_region,
        preset_major=preset_major,
        url_p=url_p
    )

@app.route("/")
def home():
    url_p = request.args.get("p")
    return render_home(url_p=url_p)

@app.route("/region/<region_name>")
def region_home(region_name):
    # e.g. 부산광역시
    seo_title = f"{region_name} 대학생 장학금 및 지원금 조회 - 드림포켓"
    seo_desc = f"{region_name} 거주 대학생을 위한 지역 지자체 장학금, 학자금 대출 이자 지원 등 숨은 혜택을 드림포켓에서 3초 만에 확인하세요."
    return render_home(preset_region=region_name, seo_title=seo_title, seo_desc=seo_desc)

@app.route("/major/<major_name>")
def major_home(major_name):
    # e.g. 컴퓨터공학과
    seo_title = f"{major_name} 대학생 전공 장학금 및 우수 혜택 조회 - 드림포켓"
    seo_desc = f"{major_name} 학생들을 위한 학과 맞춤형 전공 장학금, 이공계/인문계 우수 장학금을 실시간으로 매칭하고 추천해 드립니다."
    return render_home(preset_major=major_name, seo_title=seo_title, seo_desc=seo_desc)

@app.route("/robots.txt")
def robots_txt():
    host_url = request.url_root.rstrip('/')
    base_url = os.environ.get("BASE_URL")
    if not base_url:
        if "localhost" in host_url or "127.0.0.1" in host_url:
            base_url = host_url
        else:
            base_url = "https://dreampocket.onrender.com"
            
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {base_url}/sitemap.xml"
    ]
    return Response("\n".join(lines), mimetype="text/plain")

@app.route("/sitemap.xml")
def sitemap_xml():
    host_url = request.url_root.rstrip('/')
    base_url = os.environ.get("BASE_URL")
    if not base_url:
        if "localhost" in host_url or "127.0.0.1" in host_url:
            base_url = host_url
        else:
            base_url = "https://dreampocket.onrender.com"
            
    urls = []
    
    # Base URL
    urls.append(f"<url><loc>{base_url}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>")
    
    # Regions
    regions = ["서울특별시", "경기도", "인천광역시", "부산광역시", "대구광역시", "광주광역시", "대전광역시", "울산광역시", "세종특별자치시", "강원특별자치도", "충청북도", "충청남도", "전라북도", "전라남도", "경상북도", "경상남도", "제주특별자치도"]
    for r in regions:
        urls.append(f"<url><loc>{base_url}/region/{r}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>")
        
    # Majors (Sample top majors)
    majors = ["컴퓨터공학과", "경영학과", "경제학과", "기계공학과", "전자공학과", "간호학과", "사회복지학과"]
    for m in majors:
        urls.append(f"<url><loc>{base_url}/major/{m}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>")
        
    # Individual Scholarships
    schs = db.get_all_scholarships()
    for sch in schs:
        urls.append(f"<url><loc>{base_url}/scholarship/{sch['id']}</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>")
        
    # Legal Pages
    urls.append(f"<url><loc>{base_url}/privacy</loc><changefreq>monthly</changefreq><priority>0.3</priority></url>")
    urls.append(f"<url><loc>{base_url}/terms</loc><changefreq>monthly</changefreq><priority>0.3</priority></url>")
        
    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>"
    return Response(xml, mimetype="application/xml")

@app.route("/scholarship/<int:sch_id>")
def scholarship_detail(sch_id):
    # Fetch scholarship by id
    cursor = db.conn.cursor()
    cursor.execute("SELECT id, category, title, period, status, source, collected_at FROM scholarships WHERE id = ?", (sch_id,))
    row = cursor.fetchone()
    if not row:
        return "존재하지 않거나 마감된 장학 공고입니다.", 404
        
    sch = {
        "id": row[0],
        "category": row[1],
        "title": row[2],
        "period": row[3],
        "status": row[4],
        "source": row[5],
        "collected_at": str(row[6]) if row[6] else ""
    }
    return render_template("scholarship_detail.html", sch=sch)


@app.route("/admin")
@admin_required
def admin():
    return render_template("admin.html")

@app.route("/api/admin/refresh", methods=["POST"])
@admin_required
def trigger_refresh():
    import asyncio
    try:
        from core.agent_tools import refresh_scholarship_data
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        if loop.is_running():
            import threading
            result_container = {}
            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    result_container["result"] = new_loop.run_until_complete(refresh_scholarship_data())
                    result_container["success"] = True
                except Exception as e:
                    result_container["error"] = str(e)
                    result_container["success"] = False
                finally:
                    new_loop.close()
            t = threading.Thread(target=run_in_thread)
            t.start()
            t.join()
            if result_container.get("success"):
                return jsonify({"success": True, "message": result_container["result"]})
            else:
                return jsonify({"success": False, "error": result_container.get("error", "Unknown error")}), 500
        else:
            result = loop.run_until_complete(refresh_scholarship_data())
            return jsonify({"success": True, "message": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/api/health-check", methods=["GET"])
def health_check():
    import os
    import traceback
    try:
        all_schs = db.get_all_scholarships()
        count = len(all_schs)
        
        # If the database has 0 scholarships, trigger a background crawl thread immediately!
        triggered = False
        if count == 0:
            import threading
            import asyncio
            from core.agent_tools import refresh_scholarship_data
            
            def run_crawl_once():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    print("[Health Check Diagnostics] Force-triggering crawl since database is empty...")
                    new_loop.run_until_complete(refresh_scholarship_data())
                except Exception as e:
                    print(f"[Health Check Diagnostics] Error running force crawl: {e}")
                finally:
                    new_loop.close()
                    
            threading.Thread(target=run_crawl_once, daemon=True).start()
            triggered = True
            
        return jsonify({
            "status": "healthy",
            "database_file": "data/antigravity_bot.db",
            "database_exists": os.path.exists("data/antigravity_bot.db"),
            "scholarship_count": count,
            "crawling_triggered": triggered
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route("/api/stats", methods=["GET"])
def get_stats():
    # 1. Scholarship stats from DB
    all_schs = db.get_all_scholarships()
    total_count = len(all_schs)
    
    # Categorize
    categories = {}
    for s in all_schs:
        cat = s.get("category", "기타") or "기타"
        categories[cat] = categories.get(cat, 0) + 1
        
    # Last update time
    last_collected = "최근 업데이트 정보 없음"
    if all_schs:
        # Find the max collected_at
        times = [s.get("collected_at") for s in all_schs if s.get("collected_at")]
        if times:
            try:
                # Format or sort
                max_time = max(times)
                # It might be string or datetime
                if isinstance(max_time, str):
                    last_collected = max_time[:16] # up to minutes
                else:
                    last_collected = max_time.strftime("%Y-%m-%d %H:%M")
            except Exception:
                pass


    return jsonify({
        "scholarships": {
            "total": total_count,
            "categories": categories,
            "last_updated": last_collected
        }
    })

@app.route("/api/admin/refresh", methods=["POST"])
def admin_refresh():
    import threading
    import asyncio
    from core.agent_tools import refresh_scholarship_data
    
    def run_crawl_once():
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            print("[Admin Command] Force-triggering full crawl...")
            new_loop.run_until_complete(refresh_scholarship_data())
        except Exception as e:
            print(f"[Admin Command] Error running force crawl: {e}")
        finally:
            new_loop.close()
            
    threading.Thread(target=run_crawl_once, daemon=True).start()
    
    return jsonify({
        "success": True,
        "message": "백그라운드에서 크롤링(동기화) 작업이 시작되었습니다."
    })

@app.route("/api/match", methods=["POST"])
def match_scholarships():
    try:
        data = request.json or {}
        gpa = data.get("gpa", "0.0")
        income = data.get("income", "모름")
        location = data.get("location", "")
        major = data.get("major", "")

        clean_major = major.strip()
        for suffix in ["공학과", "학과", "학부", "과"]:
            if clean_major.endswith(suffix) and len(clean_major) > len(suffix):
                clean_major = clean_major[:-len(suffix)]
                break

        user_profile = {
            "user_id": "guest_user",
            "gpa": gpa,
            "income": income,
            "location": location,
            "major": clean_major
        }

        # Calculate scores against all scholarships via the brain
        result = brain.get_matches(user_profile)
        
        return jsonify({
            "success": True,
            "user_profile": user_profile,
            "results": {
                "success_matches": result["success_matches"],
                "gap_matches": result["gap_matches"],
                "total_potential_amount": result["total_potential_amount"]
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def run_auto_refresh():
    import time
    import asyncio
    # Initial delay of 10 seconds to let Flask boot smoothly
    time.sleep(10)
    while True:
        print("[Auto-Refresh Daemon] Starting background scholarship list crawl...")
        try:
            from core.agent_tools import refresh_scholarship_data
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(refresh_scholarship_data())
            print(f"[Auto-Refresh Daemon] SUCCESS: {result}")
            loop.close()
        except Exception as e:
            print(f"[Auto-Refresh Daemon] ERROR during background crawl: {e}")
        
        # Sleep for 12 hours (43200 seconds) before repeating
        time.sleep(43200)

# Ensure necessary directories exist
os.makedirs("data", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)

# Start auto-refresh daemon in background
daemon = threading.Thread(target=run_auto_refresh, daemon=True)
daemon.start()

import base64
from urllib.parse import unquote
from core.og_generator import generate_og_image

@app.route('/api/admin/clean', methods=['GET'])
def admin_clean_db():
    try:
        from scripts.clean_db import clean_database
        clean_database()
        return jsonify({"status": "success", "message": "Database cleaned successfully."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/og-image')
def og_image():
    p = request.args.get('p')
    if not p:
        # Return a static default OG image or a fallback
        return app.send_static_file('og-image.png')
        
    try:
        # Decode the payload (e.g. "?p=eyJncGEiOiIzLjUiLCJpbmNvbWUiOiIxIiwibG9jYXRpb24iOiLshJzsmrjsi5wiLCJtYWpvciI6IuqyveyYge2VmeqzvCJ9")
        decoded_json = base64.b64decode(unquote(p)).decode('utf-8')
        payload = json.loads(decoded_json)
        
        # Run matching to get total amount
        results = brain.match_scholarships(payload)
        successes = results.get("success_matches", [])
        
        # Filter out loan related
        LOAN_KEYWORDS = ['대출', '학자금대출', '생활비대출', '융자', '이자', '저금리', '금리', '상환', '보증', '담보']
        successes = [s for s in successes if not any(k in s['title'] for k in LOAN_KEYWORDS)]
        
        total_amount = 0
        for sch in successes:
            amt = sch.get('amount_est', 0)
            if amt > 0 and amt != 500000:
                total_amount += amt
                
        # Generate image
        img_bytes = generate_og_image(payload.get('major', ''), total_amount)
        return Response(img_bytes, mimetype='image/png')
        
    except Exception as e:
        print("OG Image Generation Error:", e)
        return app.send_static_file('og-image.png')

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    try:
        data = request.json
        phone = data.get("phone")
        gpa = data.get("gpa")
        income = data.get("income")
        location = data.get("location")
        major = data.get("major")
        
        if not phone:
            return jsonify({"success": False, "message": "휴대폰 번호는 필수입니다."}), 400
            
        subscription = {
            "phone": phone,
            "gpa": gpa,
            "income": income,
            "location": location,
            "major": major,
            "created_at": datetime.now().isoformat()
        }
        
        subs_file = "data/subscriptions.json"
        
        # Load existing subscriptions
        subs = []
        if os.path.exists(subs_file):
            with open(subs_file, "r", encoding="utf-8") as f:
                try:
                    subs = json.load(f)
                except json.JSONDecodeError:
                    subs = []
                    
        # Check for duplicates based on phone (simple approach)
        for s in subs:
            if s.get("phone") == phone:
                return jsonify({"success": True, "message": "이미 신청된 번호입니다. 조건이 갱신되었습니다."}), 200
                
        subs.append(subscription)
        
        with open(subs_file, "w", encoding="utf-8") as f:
            json.dump(subs, f, ensure_ascii=False, indent=4)
            
        return jsonify({"success": True, "message": "신청 완료"}), 200
    except Exception as e:
        print(f"Subscription Error: {e}")
        return jsonify({"success": False, "message": "서버 오류가 발생했습니다."}), 500

@app.route("/api/ai-check", methods=["POST"])
def ai_check():
    from core.ai_checker import generate_eligibility_questions
    data = request.json
    sch_id = data.get("id")
    if not sch_id:
        return jsonify({"error": "No scholarship ID provided"}), 400
        
    try:
        questions = generate_eligibility_questions(sch_id)
        return jsonify({"questions": questions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Determine environment
    is_production = os.environ.get("FLASK_ENV") == "production"
    port = int(os.environ.get("PORT", 5000))
    
    print(f"Starting DreamPocket on port {port} | Production={is_production}")
    app.run(host="0.0.0.0", port=port, debug=not is_production)
