import os, time
import pyotp
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()

TOKEN = os.getenv("TOKEN", 'okak')
SECRET = os.getenv("TOTP_SECRET", 'okak')
ALLOWED_USER_ID = int(os.getenv("USER_ID", 0))

if not TOKEN or not SECRET:
	print("Ошибка: не найден TOKEN или TOTP_SECRET в .env")
	exit(1)

totp = pyotp.TOTP(SECRET)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await update.message.reply_text("/totp for code generation\n/me for userid")

async def send_totp(update: Update, context: ContextTypes.DEFAULT_TYPE):
	user_id = update.effective_user.id
	if user_id != ALLOWED_USER_ID:
		return
	code = totp.now()
	time_remaining = totp.interval - (int(time.time()) % totp.interval)
	await update.message.reply_text(f"TOTP: `{code}`\nremains {time_remaining} sec", parse_mode=ParseMode.MARKDOWN_V2)

async def send_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
	user = update.effective_user
	await update.message.reply_text(f"{user}")

if __name__ == "__main__":
	app = ApplicationBuilder().token(TOKEN).build()
	app.add_handler(CommandHandler("start", start))
	app.add_handler(CommandHandler("totp", send_totp))
	app.add_handler(CommandHandler("me", send_user_info))

	print("Бот запущен...")
	app.run_polling()

