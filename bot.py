import logging
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

import db
#from config import TELEGRAM_BOT_TOKEN
from stock_fetcher import get_price, get_stock_code
from news_crawler import get_stock_news, get_main_news
from stock_chart import fetch_daily_price, draw_candle_chart
from pytz import timezone
from datetime import datetime, time
from db import init_db, save_group_chat_id,load_group_chat_ids

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
active_chat_ids = set()
GROUP_CHAT_FILE = "group_chat_ids.txt"

PERIOD_OPTIONS = ["1일", "1주", "1달", "1년", "5년"]
CANDLE_OPTIONS = ["일봉", "주봉", "월봉"]

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
    context.user_data['stock_code'] = stock_code # 콜백에서 사용
    context.user_data['period'] = "1달"
    context.user_data['candle_type'] = "일봉"

    result = get_price(stock_code)

    df = fetch_daily_price(stock_code, period="1달" , candle_type="일봉")
    chart = draw_candle_chart(df, title="최근 주가 추이")

    keyboard = [
        [InlineKeyboardButton(text=label, callback_data=f"기간:{label}") for label in PERIOD_OPTIONS],
        [InlineKeyboardButton(text=label, callback_data=f"봉:{label}") for label in CANDLE_OPTIONS]
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
    data = query.data

    if data.startswith("기간:"):
        context.user_data['period'] = data.replace("기간:", "")
    elif data.startswith("봉:"):
        context.user_data['candle_type'] = data.replace("봉:", "")

    stock_code = context.user_data.get("stock_code")
    period = context.user_data.get("period", "1달")
    candle_type = context.user_data.get("candle_type", "일봉")

    if not stock_code:
        await query.edit_message_text("❗ 먼저 /price [종목코드] 를 입력해 주세요.")
        return

    df = fetch_daily_price(stock_code, period=period, candle_type=candle_type)
    chart = draw_candle_chart(df, title=f"{period} {candle_type} 추이")

    chart_message_id = context.user_data.get("chart_message_id")
    chart_chat_id = context.user_data.get("chart_chat_id")

    if chart_message_id and chart_chat_id:
        await context.bot.edit_message_media(
            media=InputMediaPhoto(chart),
            chat_id=chart_chat_id,
            message_id=chart_message_id,
            reply_markup=query.message.reply_markup
        )
    else:
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=chart)


def main():
    logging.basicConfig(level=logging.INFO)

    db.init_db()
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
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()