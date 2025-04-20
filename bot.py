import logging
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
from telegram.ext import JobQueue
from config import TELEGRAM_BOT_TOKEN
from stock_fetcher import get_price, get_stock_code
from news_crawler import get_stock_news, get_main_news
from stock_chart import fetch_daily_price, draw_candle_chart
from pytz import timezone
from datetime import datetime, time

active_chat_ids = set()
GROUP_CHAT_FILE = "group_chat_ids.txt"

def save_group_chat_id(chat_id: int):
    # 이미 저장되어 있는지 확인
    try:
        with open(GROUP_CHAT_FILE, "r") as f:
            ids = {line.strip() for line in f}
    except FileNotFoundError:
        ids = set()

    if str(chat_id) not in ids:
        with open(GROUP_CHAT_FILE, "a") as f:
            f.write(str(chat_id) + "\n")

def load_group_chat_ids():
    try:
        with open(GROUP_CHAT_FILE, "r") as f:
            return [int(line.strip()) for line in f if line.strip()]
    except FileNotFoundError:
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type in ("group", "supergroup"):  # 그룹 채팅만 저장
        save_group_chat_id(chat.id)
    await update.message.reply_text("안녕하세요! 📈 최신 주식 정보를 제공하는 봇입니다 ")


async def send_daily_stock_news(context: ContextTypes.DEFAULT_TYPE):
    news_list = get_main_news()
    now = datetime.now(timezone("Asia/Seoul")).strftime("%Y-%m-%d %H:%M")
    text = f"\ud83d\uddfe\ufe0f [{now} 기준 주요 뉴스]\n\n" + "\n\n".join(news_list)
    safe_text = text.encode('utf-16', 'surrogatepass').decode('utf-16') #window환경 충돌 방지
    group_ids = load_group_chat_ids()
    for chat_id in group_ids:
        try:
            await context.bot.send_message(chat_id=chat_id, text=safe_text)
        except Exception as e:
            logging.warning(f"❌ 뉴스 전송 실패 (chat_id={chat_id}): {e}")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("종목 코드를 입력해 주세요. 예: /price 005930")
        return

    stock_code = context.args[0].strip()
    result = get_price(stock_code)

    df = fetch_daily_price(stock_code)
    chart = draw_candle_chart(df, title="최근 주가 추이")

    active_chat_ids.add(update.effective_chat.id)
    await update.message.reply_text(result)
    await update.message.reply_photo(photo=chart)

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("종목 코드를 입력해 주세요 예: /news 005930")
        return

    stock_code = context.args[0].strip()
    news_list = get_stock_news(stock_code)

    active_chat_ids.add(update.effective_chat.id)
    await update.message.reply_text("\n\n".join(news_list))

async def getcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("종목 명을 입력해 주세요")
        return

    query = " ".join(context.args).strip()
    result = get_stock_code(query)

    active_chat_ids.add(update.effective_chat.id)
    await update.message.reply_text(result)

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("getcode", getcode))

    # ⏰ 예약 메시지 전송 시작
    app.job_queue.run_daily(
        send_daily_stock_news,
        time=time(8, 30, tzinfo=timezone("Asia/Seoul"))
    )


    print("✅ 봇 실행 중...")
    app.run_polling()


if __name__ == "__main__":
    main()