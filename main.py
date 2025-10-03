import os, time, json
import pyotp
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.helpers import escape_markdown

load_dotenv()

TOKEN = os.getenv("TOKEN")
ALLOWED_USER_ID = int(os.getenv("USER_ID", 0))
SECRETS_FILE = "secrets.json"

if os.path.exists(SECRETS_FILE):
    with open(SECRETS_FILE, "r") as f:
        secrets = json.load(f)
else:
    secrets = {}

def save_secrets():
    with open(SECRETS_FILE, "w") as f:
        json.dump(secrets, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Your ID:{update.effective_user.id}\n/totp <name> — get code\n/add <name> <secret> — add secret\n/list — totp list")

async def send_totp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return

    if context.args:
        name = context.args[0]
        if name not in secrets:
            await update.message.reply_text(f"No secrets like {escape_markdown(name)}", parse_mode=ParseMode.MARKDOWN_V2)
            return

        totp = pyotp.TOTP(secrets[name])
        code = totp.now()
        remain = totp.interval - (int(time.time()) % totp.interval)
        await update.message.reply_text(f"{escape_markdown(name)}: `{code}`\nRemains {remain} sec",
                                        parse_mode=ParseMode.MARKDOWN_V2)
        return

    if not secrets:
        await update.message.reply_text("No secrets.")
        return

    keyboard = [[InlineKeyboardButton(name, callback_data=f"show_{name}")] for name in secrets.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a secret:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("show_"):
        name = data[len("show_"):]
        if name not in secrets:
            await query.edit_message_text(f"No secret {name}")
            return

        totp = pyotp.TOTP(secrets[name])
        code = totp.now()
        remain = totp.interval - (int(time.time()) % totp.interval)
        keyboard = [[InlineKeyboardButton("Refresh", callback_data=f"show_{name}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try: await query.edit_message_text(f"{escape_markdown(name)}: `{code}`\nRemains {remain} sec",
                                      parse_mode=ParseMode.MARKDOWN_V2,
                                      reply_markup=reply_markup)
        except:
            pass

async def add_secret(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text("try: /add <name> <secret>")
        return

    name, secret = context.args[0], context.args[1]
    secrets[name] = secret
    save_secrets()
    await update.message.reply_text(f"Secret added: {escape_markdown(name)}")

async def send_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Totp_working!")

async def list_secrets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    if not secrets:
        await update.message.reply_text("No secrets.")
    else:
        await update.message.reply_text("Available: " + ", ".join(secrets.keys()))

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("totp", send_totp))
    app.add_handler(CommandHandler("add", add_secret))
    app.add_handler(CommandHandler("list", list_secrets))
    app.add_handler(CommandHandler("status", send_status))
    app.add_handler(CallbackQueryHandler(button_callback))
    print("Running...")
    app.run_polling()
