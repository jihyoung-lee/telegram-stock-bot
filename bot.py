import logging

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
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
    context.user_data['stock_code'] = stock_code  # 콜백에서 사용

    result = get_price(stock_code)

    df = fetch_daily_price(stock_code, period="1달")
    chart = draw_candle_chart(df, title="최근 주가 추이")

    keyboard = [
        [
            InlineKeyboardButton("1일", callback_data="1일"),
            InlineKeyboardButton("1주", callback_data="1주"),
            InlineKeyboardButton("1달", callback_data="1달"),
            InlineKeyboardButton("1년", callback_data="1년"),
            InlineKeyboardButton("5년", callback_data="5년")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    active_chat_ids.add(update.effective_chat.id)
    sent_message = await update.message.reply_photo(photo=chart, reply_markup=reply_markup)
    context.user_data['chart_message_id'] = sent_message.message_id
    context.user_data['chart_chat_id'] = sent_message.chat_id
    await update.message.reply_text(result)

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


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    period = query.data
    stock_code = context.user_data.get("stock_code")

    if not stock_code:
        await query.edit_message_text("❗ 먼저 /price [종목코드] 를 입력해 주세요.")
        return

        # 차트 새로 그림
    df = fetch_daily_price(stock_code, period=period)
    chart = draw_candle_chart(df, title=f"{period} 주가 추이")

    chart_message_id = context.user_data.get("chart_message_id")
    chart_chat_id = context.user_data.get("chart_chat_id")

    if chart_message_id and chart_chat_id:
        try:
            await context.bot.edit_message_media(
                media=InputMediaPhoto(media=chart),
                chat_id=chart_chat_id,
                message_id=chart_message_id,
                reply_markup=query.message.reply_markup  # 기존 버튼 유지
            )
        except telegram.error.BadRequest as e:
            if "Message is not modified" in str(e):
                # 같은 차트일 경우, 강제로 다시 전송
                await context.bot.send_photo(
                    chat_id=chart_chat_id,
                    photo=chart,
                    caption=f"{period} 차트입니다.",
                    reply_markup=query.message.reply_markup
                )
    else:
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=chart)
def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("getcode", getcode))

    app.add_handler(CallbackQueryHandler(button_callback))

    # ⏰ 예약 메시지 전송 시작
    app.job_queue.run_daily(
        send_daily_stock_news,
        time=time(8, 30, tzinfo=timezone("Asia/Seoul"))
    )


    print("✅ 봇 실행 중...")
    app.run_polling()


if __name__ == "__main__":
    main()