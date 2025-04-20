from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN
from stock_fetcher import get_price, get_stock_code
from news_crawler import get_stock_news
from stock_chart import fetch_daily_price, draw_candle_chart

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("안녕하세요! 📈 최신 주식 정보를 제공하는 봇입니다 ")


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("종목 코드를 입력해 주세요. 예: /price 005930")
        return

    stock_code = context.args[0].strip()
    result = get_price(stock_code)

    df = fetch_daily_price(stock_code)
    chart = draw_candle_chart(df, title="최근 주가 추이")
    await update.message.reply_text(result)
    await update.message.reply_photo(photo=chart)

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("종목 코드를 입력해 주세요 예: /news 005930")
        return

    stock_code = context.args[0].strip()
    news_list = get_stock_news(stock_code)
    await update.message.reply_text("\n\n".join(news_list))

async def getcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("종목 명을 입력해 주세요")
        return

    query = " ".join(context.args).strip()
    result = get_stock_code(query)
    await update.message.reply_text(result)

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("getcode", getcode))

    print("봇 실행 중 ...")
    app.run_polling()


if __name__ == "__main__":
    main()
