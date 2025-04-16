from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN
from stock_fetcher import get_price


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("안녕하세요! 📈 최신 주식 정보를 제공하는 봇입니다 ")


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("종목 코드를 입력해주세요. 예: /price 005930")
        return

    stock_code = context.args[0].strip()

    result = get_price(stock_code)
    await update.message.reply_text(result)


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))

    print("봇 실행 중 ...")
    app.run_polling()


if __name__ == "__main__":
    main()
