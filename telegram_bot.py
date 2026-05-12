import os
import logging
import pytz
import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    filters, ConversationHandler, ContextTypes
)
from database import db
from matching_engine import brain

# Load environment variables from .env file
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

GPA, INCOME, LOCATION, MAJOR = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "안녕하세요! 장학금 AI 비서 Antigravity입니다.🚀\n"
        "개인 맞춤형 장학금 탐색을 위해 프로필을 등록하겠습니다.\n\n"
        "먼저, 직전 학기 GPA(성적)를 입력해주세요. (예: 2.75 또는 3.5)"
    )
    return GPA

async def get_gpa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['gpa'] = update.message.text
    await update.message.reply_text("학자금 지원구간(소득 분위 1~10)을 입력해주세요. (모르시면 '모름' 입력)")
    return INCOME

async def get_income(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['income'] = update.message.text
    await update.message.reply_text("거주 지역(시/도 단위)을 입력해주세요. (예: 광주광역시, 서울특별시, 부산광역시)")
    return LOCATION

async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['location'] = update.message.text
    await update.message.reply_text("전공 분야를 입력해주세요. (예: 경영학부, 컴퓨터공학, 화학과)")
    return MAJOR

async def get_major(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    user_data['major'] = update.message.text
    user_id = str(update.effective_user.id)
    
    # Save to SQLite database
    db.save_user_profile(user_id, user_data)
    
    await update.message.reply_text(
        "✅ 프로필 등록이 완료되었습니다!\n\n"
        "🌅 <b>매일 아침 9:00 오늘의 추천 장학금 배달(알림) 서비스</b>가 자동으로 켜졌습니다.\n"
        "알림 수신을 원치 않으시면 언제든지 `/unsubscribe`를 보내 알림을 끌 수 있습니다.\n\n"
        "지금 매칭 결과를 바로 보시려면 `/matches` 명령어를 입력해 보세요! 🎯",
        parse_mode="HTML"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "프로필 등록이 취소되었습니다. 대화를 다시 시작하려면 `/start`를 입력해 주세요.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def show_matches(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_profile = db.get_user_profile(user_id)
    
    if not user_profile:
        await update.message.reply_text(
            "⚠️ 등록된 프로필이 없습니다!\n"
            "먼저 `/start` 명령어를 입력하여 프로필을 간편하게 등록해 주세요. 🤖"
        )
        return

    await update.message.reply_text("🔍 회원님의 프로필을 기반으로 지능형 매칭 및 역량 보완점을 분석하는 중입니다...")
    
    # Run the matching engine
    res = brain.get_matches(user_id)
    success = res['success_matches']
    gaps = res['gap_matches']
    
    if not success and not gaps:
        await update.message.reply_text(
            f"📋 {user_profile['major']} 전공 및 거주지 {user_profile['location']} 조건에 일치하는 추천 장학금이 현재 목록에 없습니다.\n\n"
            "💡 채널 고도화 및 신규 공고가 상시 수집되고 있으니 발견 즉시 아침 알림으로 배달해 드릴게요!"
        )
        return
        
    response_msg = ""
    
    if success:
        response_msg += f"🏆 <b>맞춤 장학금 추천 목록 ({len(success)}건)</b>\n"
        response_msg += "<i>(회원님께서 즉시 신청 가능한 추천 목록입니다)</i>\n\n"
        for idx, match in enumerate(success):
            reasons_str = ", ".join(match['reasons'])
            response_msg += (
                f"<b>{idx+1}. {match['title']}</b>\n"
                f"  - 매칭 점수: {match['score']}점\n"
                f"  - 선발 조건: {reasons_str}\n"
                f"  - 신청 기간: {match['period']}\n"
                f"  - 상세 보기: <a href='{match['link']}'>공고 바로가기</a>\n\n"
            )
            
    if gaps:
        response_msg += f"🎯 <b>조금만 보완하면 신청 가능한 장학금 가이드 ({len(gaps)}건)</b>\n"
        response_msg += "<i>(조건이 아쉽게 미달된 우수 기회와 역량 보완 처방입니다)</i>\n\n"
        for idx, match in enumerate(gaps):
            response_msg += (
                f"<b>💡 {match['title']}</b>\n"
                f"  - 성장 분석 피드백:\n"
                f"    {match['gaps'][0]}\n"
                f"  - 신청 기간: {match['period']}\n"
                f"  - 상세 보기: <a href='{match['link']}'>공고 바로가기</a>\n\n"
            )
            
    await update.message.reply_text(response_msg, parse_mode="HTML", disable_web_page_preview=True)

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_profile = db.get_user_profile(user_id)
    
    if not user_profile:
        await update.message.reply_text(
            "⚠️ 등록된 프로필이 없습니다!\n"
            "알림 서비스를 가입하려면 먼저 `/start` 명령어로 프로필을 등록해 주세요. 🤖"
        )
        return
        
    db.set_subscription(user_id, True)
    await update.message.reply_text(
        "🌅 <b>매일 아침 9:00 맞춤 장학금 자동 알림이 활성화되었습니다!</b>\n"
        "이제 최신 공고 분석 및 스펙 가이드 뉴스를 매일 아침 메신저로 기분 좋게 배달해 드릴게요. 🔔",
        parse_mode="HTML"
    )

async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    db.set_subscription(user_id, False)
    await update.message.reply_text(
        "🔕 <b>매일 아침 맞춤 장학금 자동 알림이 중단되었습니다.</b>\n"
        "언제든지 다시 스펙 성장 가이드 알림을 구독하여 기회를 넓히시려면 `/subscribe` 명령어를 보내주세요!",
        parse_mode="HTML"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "💡 <b>장학금 비서 Antigravity 봇 사용법</b>\n\n"
        "• `/start` : 새로운 프로필 등록 (학점, 소득분위, 거주지, 전공)\n"
        "• `/matches` : 추천 장학금 및 미달 조건 보완 가이드 보기\n"
        "• `/subscribe` : 매일 아침 9시 자동 매칭 알림 켜기\n"
        "• `/unsubscribe` : 매일 아침 자동 알림 끄기\n"
        "• `/help` : 봇 사용 안내 확인",
        parse_mode="HTML"
    )

# Helper to parse deadline date from period string
def parse_deadline(period_str):
    import re
    # Look for dates like 2026.05.31 or 2026-05-31 or 2026/05/31
    matches = re.findall(r'(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})', period_str)
    if matches:
        last_match = matches[-1]
        try:
            return datetime.date(int(last_match[0]), int(last_match[1]), int(last_match[2]))
        except ValueError:
            return None
    return None

# Daily scheduled task function with smart fatigue control & D-3 alerts
async def send_daily_matches(context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Executing daily morning scholarship notification job with fatigue control...")
    
    # 1. Automatically refresh database with latest scraper info
    try:
        from agent_tools import refresh_scholarship_data
        await refresh_scholarship_data()
    except Exception as e:
        logger.error(f"Error refreshing scholarship data during daily job: {e}")
        
    # 2. Query all subscribed users
    subscribed_users = db.get_subscribed_users()
    logger.info(f"Found {len(subscribed_users)} subscribed users.")
    
    today = datetime.date.today()
    
    for user in subscribed_users:
        user_id = user['user_id']
        try:
            res = brain.get_matches(user_id)
            success = res['success_matches']
            gaps = res['gap_matches']
            
            new_success = []
            new_gaps = []
            closing_matches = []
            
            # Analyze Success Matches
            for match in success:
                is_notified = db.is_scholarship_notified(user_id, match['id'])
                if not is_notified:
                    new_success.append(match)
                else:
                    # Check for D-3 deadline reminder
                    deadline = parse_deadline(match['period'])
                    if deadline:
                        days_left = (deadline - today).days
                        if days_left == 3:
                            closing_matches.append((match, days_left))
                            
            # Analyze Gap (Close) Matches
            for match in gaps:
                is_notified = db.is_scholarship_notified(user_id, match['id'])
                if not is_notified:
                    new_gaps.append(match)
                else:
                    # Check for D-3 deadline reminder
                    deadline = parse_deadline(match['period'])
                    if deadline:
                        days_left = (deadline - today).days
                        if days_left == 3:
                            closing_matches.append((match, days_left))

            # Fatigue Control: If there are no new matches and no closing alerts, REMAIN SILENT!
            if not new_success and not new_gaps and not closing_matches:
                logger.info(f"User {user_id}: No new matching scholarships or urgent deadlines. Silent suppression.")
                continue
                
            response_msg = (
                f"🌅 <b>굿모닝! 장학금 비서 오늘의 업데이트 도착</b>\n"
                f"알림 피로를 줄이기 위해, 새 공고나 마감 임박 소식이 있을 때만 발송해 드립니다! 🔔\n\n"
            )
            
            if new_success:
                response_msg += f"🔥 <b>새로 발견된 맞춤 장학금 ({len(new_success)}건)</b>\n"
                for idx, match in enumerate(new_success):
                    reasons_str = ", ".join(match['reasons'])
                    response_msg += (
                        f"<b>{idx+1}. {match['title']}</b>\n"
                        f"  - 매칭 점수: {match['score']}점\n"
                        f"  - 선발 조건: {reasons_str}\n"
                        f"  - 신청 기간: {match['period']}\n"
                        f"  - 상세 보기: <a href='{match['link']}'>공고 바로가기</a>\n\n"
                    )
                    
            if new_gaps:
                response_msg += f"🎯 <b>새로 발견된 도전 가능 장학금 ({len(new_gaps)}건)</b>\n"
                response_msg += "<i>(조금만 조건을 보완하면 신청 가능한 우수 공고입니다)</i>\n\n"
                for idx, match in enumerate(new_gaps):
                    response_msg += (
                        f"<b>💡 {match['title']}</b>\n"
                        f"  - 성장 분석 피드백:\n"
                        f"    {match['gaps'][0]}\n"
                        f"  - 신청 기간: {match['period']}\n"
                        f"  - 상세 보기: <a href='{match['link']}'>공고 바로가기</a>\n\n"
                    )

            if closing_matches:
                response_msg += f"🚨 <b>신청 마감 임박 알림! 놓치지 마세요! ({len(closing_matches)}건)</b>\n"
                for idx, (match, days_left) in enumerate(closing_matches):
                    response_msg += (
                        f"<b>🏃 {match['title']}</b>\n"
                        f"  - <b>신청 마감까지 단 {days_left}일 남았습니다! (D-{days_left})</b>\n"
                        f"  - 신청 기간: {match['period']}\n"
                        f"  - 상세 보기: <a href='{match['link']}'>공고 바로가기</a>\n\n"
                    )
            
            await context.bot.send_message(
                chat_id=user_id,
                text=response_msg,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            
            # Mark all sent new scholarships as notified in database
            for match in new_success:
                db.mark_scholarship_notified(user_id, match['id'])
            for match in new_gaps:
                db.mark_scholarship_notified(user_id, match['id'])
                
            logger.info(f"Successfully sent smart updates to user {user_id}")
        except Exception as e:
            logger.error(f"Failed to send daily matches to user {user_id}: {e}")

def main() -> None:
    # Read token from environment variable or placeholder
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
    if not token or "YOUR_TELEGRAM_BOT_TOKEN" in token:
        print("[WARNING] TELEGRAM_BOT_TOKEN이 설정되지 않았습니다. .env 파일에 실제 토큰을 입력해주세요.")
        return

    # Enable job_queue in python-telegram-bot
    application = ApplicationBuilder().token(token).build()

    # Add conversation handler for registration
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GPA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gpa)],
            INCOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_income)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_location)],
            MAJOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_major)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("matches", show_matches))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    application.add_handler(CommandHandler("help", help_command))

    # Get job queue and schedule daily notification job
    jq = application.job_queue
    if jq:
        # 1. Schedule daily morning notifications at 9:00 AM Seoul Time
        tz = pytz.timezone('Asia/Seoul')
        notification_time = datetime.time(hour=9, minute=0, second=0, tzinfo=tz)
        jq.run_daily(send_daily_matches, time=notification_time)
        logger.info("Successfully scheduled daily morning notification at 9:00 AM (KST)")
        
        # 2. [TEST EXTREME PRO] Immediate test notification scheduled 10 seconds after bot starts
        jq.run_once(send_daily_matches, when=10)
        logger.info("Successfully scheduled end-to-end TEST notification in 10 seconds!")
    else:
        logger.warning("JobQueue is not initialized! Ensure python-telegram-bot[job-queue] is fully active.")

    print("장학금 비서 텔레그램 봇이 정상적으로 실행되었습니다. (Polling 중...)")
    application.run_polling()

if __name__ == "__main__":
    main()
