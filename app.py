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

# Simulated ad revenue persistence file
AD_STATS_FILE = "data/ad_stats.json"

def load_ad_stats():
    if os.path.exists(AD_STATS_FILE):
        try:
            with open(AD_STATS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure all keys exist
                for key in ["impressions", "clicks", "revenue"]:
                    if key not in data: data[key] = 0
                return data
        except Exception:
            pass
    return {"impressions": 0, "clicks": 0, "revenue": 0}

def save_ad_stats(stats):
    try:
        with open(AD_STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving ad stats: {e}")

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

def render_home(preset_region="", preset_major="", seo_title=None, seo_desc=None):
    if not seo_title:
        seo_title = "드림포켓 | 대학생 맞춤 장학금 실시간 매칭"
    if not seo_desc:
        seo_desc = "드림포켓에서 3초 만에 나에게 딱 맞는 대학생 맞춤 장학금을 찾아보세요! 학점, 소득분위, 거주지, 전공만 입력하면 실시간으로 분석하여 매칭해 드립니다."
        
    return render_template(
        "index.html", 
        seo_title=seo_title, 
        seo_desc=seo_desc,
        preset_region=preset_region,
        preset_major=preset_major
    )

@app.route("/")
def home():
    return render_home()

@app.route("/region/<region_name>")
def region_home(region_name):
    # e.g. 부산광역시
    seo_title = f"{region_name} 대학생 장학금 찾기 - 드림포켓"
    seo_desc = f"{region_name} 거주 대학생을 위한 지자체 장학금 및 지원 혜택을 드림포켓에서 3초 만에 확인하세요."
    return render_home(preset_region=region_name, seo_title=seo_title, seo_desc=seo_desc)

@app.route("/major/<major_name>")
def major_home(major_name):
    # e.g. 컴퓨터공학과
    seo_title = f"{major_name} 전공 대학생 장학금 찾기 - 드림포켓"
    seo_desc = f"{major_name} 학생들을 위한 학과 맞춤형 전공 장학금을 실시간으로 매칭해 드립니다."
    return render_home(preset_major=major_name, seo_title=seo_title, seo_desc=seo_desc)

@app.route("/robots.txt")
def robots_txt():
    lines = [
        "User-agent: *",
        "Allow: /",
        "Sitemap: https://dreampocket.onrender.com/sitemap.xml"
    ]
    return Response("\n".join(lines), mimetype="text/plain")

@app.route("/sitemap.xml")
def sitemap_xml():
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

    # 2. Simulated Ad Stats
    ad_stats = load_ad_stats()
    
    # Calculate CTR
    ctr = 0.0
    if ad_stats["impressions"] > 0:
        ctr = round((ad_stats["clicks"] / ad_stats["impressions"]) * 100, 2)
        
    # Calculate eCPM (Revenue per 1000 impressions)
    ecpm = 0.0
    if ad_stats["impressions"] > 0:
        ecpm = round((ad_stats["revenue"] / ad_stats["impressions"]) * 1000, 2)

    return jsonify({
        "scholarships": {
            "total": total_count,
            "categories": categories,
            "last_updated": last_collected
        },
        "ad_stats": {
            "impressions": ad_stats["impressions"],
            "clicks": ad_stats["clicks"],
            "revenue": ad_stats["revenue"],
            "ctr": ctr,
            "ecpm": ecpm
        }
    })

@app.route("/api/match", methods=["POST"])
def match_scholarships():
    try:
        data = request.json or {}
        gpa = data.get("gpa", "0.0")
        income = data.get("income", "모름")
        location = data.get("location", "")
        major = data.get("major", "")

        # Create virtual user profile
        user_profile = {
            "user_id": "guest_user",
            "gpa": gpa,
            "income": income,
            "location": location,
            "major": major
        }

        # Dynamic major parsing to boost matching rates
        # If user types "컴퓨터공학과", clean it to match with "컴퓨터" or "공학"
        clean_major = major.strip()
        for suffix in ["공학과", "학과", "학부", "과"]:
            if clean_major.endswith(suffix) and len(clean_major) > len(suffix):
                clean_major = clean_major[:-len(suffix)]
                break

        # Calculate scores against all scholarships
        all_scholarships = db.get_all_scholarships()
        success_matches = []
        gap_matches = []

        for sch in all_scholarships:
            # Skip closed, expired, or verified dead links
            if sch.get("status") in ["마감", "만료", "비활성"]:
                continue
                
            # We temporarily use a modified profile for the core matching engine matching
            # but preserve original for details if needed. Let's do a smart matching:
            # We inject the clean_major into the category check if applicable
            temp_profile = user_profile.copy()
            temp_profile["major"] = clean_major
            
            analysis = brain.calculate_score(temp_profile, sch)

            
            item = {
                "id": sch["id"],
                "category": sch["category"],
                "title": sch["title"],
                "score": analysis["score"],
                "reasons": analysis["reasons"],
                "link": sch["source"],
                "period": sch["period"],
                "gaps": analysis["gaps"],
                "confidence": analysis["confidence"],
                "analysis_status": analysis["analysis_status"],
                "is_verified": analysis["is_verified"]
            }

            # If eligible and score is high enough (at least 30 or category match)
            if analysis["is_eligible"] and analysis["score"] >= 30:
                success_matches.append(item)
            elif not analysis["is_eligible"] and analysis["is_potential"]:
                gap_matches.append(item)

        # Calculate total potential benefit amount
        total_potential_amount = 0
        for item in success_matches:
            # Simple amount estimation from title
            amount_est = 0
            amount_match = re.search(r'(\d+)만\s*원', item['title'])
            if amount_match:
                amount_est = int(amount_match.group(1)) * 10000
            elif '전액' in item['title']:
                amount_est = 3500000 # Avg tuition
            elif '생활비' in item['title']:
                amount_est = 1000000
            else:
                amount_est = 500000 # Default
            
            item['amount_est'] = amount_est
            total_potential_amount += amount_est

        # Sort descending by score
        success_matches = sorted(success_matches, key=lambda x: x["score"], reverse=True)
        gap_matches = sorted(gap_matches, key=lambda x: x["score"], reverse=True)

        return jsonify({
            "success": True,
            "user_profile": user_profile,
            "results": {
                "success_matches": success_matches,
                "gap_matches": gap_matches,
                "total_potential_amount": total_potential_amount
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/ad-impression", methods=["POST"])
def record_impression():
    stats = load_ad_stats()
    stats["impressions"] += 1
    # Add a microscopic CPM revenue (e.g. CPM = 15,000 KRW, meaning 15 KRW per impression)
    stats["revenue"] += 15
    save_ad_stats(stats)
    return jsonify({"success": True, "ad_stats": stats})

@app.route("/api/ad-click", methods=["POST"])
def record_click():
    stats = load_ad_stats()
    stats["clicks"] += 1
    # Random CPC revenue between 120 KRW and 350 KRW
    earnings = random.randint(120, 350)
    stats["revenue"] += earnings
    save_ad_stats(stats)
    return jsonify({
        "success": True, 
        "earnings": earnings,
        "ad_stats": stats
    })

@app.route("/api/ad-reset", methods=["POST"])
@admin_required
def reset_ad_stats():
    stats = {"impressions": 0, "clicks": 0, "revenue": 0}
    save_ad_stats(stats)
    return jsonify({"success": True, "ad_stats": stats})

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

if __name__ == "__main__":
    # Determine environment
    is_production = os.environ.get("FLASK_ENV") == "production"
    port = int(os.environ.get("PORT", 5000))
    
    print(f"Starting DreamPocket on port {port} | Production={is_production}")
    app.run(host="0.0.0.0", port=port, debug=not is_production)
