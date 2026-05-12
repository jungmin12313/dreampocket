import os
import json
import re
import random
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, Response
from dotenv import load_dotenv
from database import db
from matching_engine import brain

# Load environment variables from .env (로컬 개발용)
load_dotenv()

app = Flask(__name__)

# --------------------------------------------------------
# Admin HTTP Basic Auth
# --------------------------------------------------------
def check_admin_auth(username, password):
    correct_user = os.environ.get("ADMIN_USERNAME", "admin")
    correct_pass = os.environ.get("ADMIN_PASSWORD", "changeme")
    return username == correct_user and password == correct_pass

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

# Simulated ad revenue persistence file
AD_STATS_FILE = "ad_stats.json"

def load_ad_stats():
    if os.path.exists(AD_STATS_FILE):
        try:
            with open(AD_STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"impressions": 0, "clicks": 0, "revenue": 0}

def save_ad_stats(stats):
    try:
        with open(AD_STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving ad stats: {e}")

# Routes

@app.route("/")
def home():
    return render_template("index.html")

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

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

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
                "gaps": analysis["gaps"]
            }

            # If eligible and score is high enough (at least 40 or category match)
            if analysis["is_eligible"] and analysis["score"] >= 40:
                success_matches.append(item)
            elif not analysis["is_eligible"] and analysis["is_potential"]:
                gap_matches.append(item)

        # Sort descending by score
        success_matches = sorted(success_matches, key=lambda x: x["score"], reverse=True)
        gap_matches = sorted(gap_matches, key=lambda x: x["score"], reverse=True)

        return jsonify({
            "success": True,
            "user_profile": user_profile,
            "results": {
                "success_matches": success_matches,
                "gap_matches": gap_matches
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
            from agent_tools import refresh_scholarship_data
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(refresh_scholarship_data())
            print(f"[Auto-Refresh Daemon] SUCCESS: {result}")
            loop.close()
        except Exception as e:
            print(f"[Auto-Refresh Daemon] ERROR during background crawl: {e}")
        
        # Sleep for 12 hours (43200 seconds) before repeating
        time.sleep(43200)

if __name__ == "__main__":
    # Ensure templates and static directories exist
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static/css", exist_ok=True)
    os.makedirs("static/js", exist_ok=True)
    
    # Determine environment
    is_production = os.environ.get("FLASK_ENV") == "production"
    port = int(os.environ.get("PORT", 5000))
    
    # Start auto-refresh daemon thread (only once - avoid double launch in debug mode)
    if not is_production and os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        import threading
        refresh_thread = threading.Thread(target=run_auto_refresh, daemon=True)
        refresh_thread.start()
        print("[Auto-Refresh Daemon] Background auto-crawler schedule initialized (Runs every 12 hours).")
    elif is_production:
        # In production (gunicorn), start daemon directly
        import threading
        refresh_thread = threading.Thread(target=run_auto_refresh, daemon=True)
        refresh_thread.start()
        print("[Auto-Refresh Daemon] Production auto-crawler initialized.")
    
    print(f"Starting DreamPocket on port {port} | Production={is_production}")
    app.run(host="0.0.0.0", port=port, debug=not is_production)
