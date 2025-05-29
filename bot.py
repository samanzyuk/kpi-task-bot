import os
import openai
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
bot = Bot(token=TOKEN)

app = Flask(__name__)

openai.api_key = OPENAI_KEY

tasks = []

def start(update, context):
    update.message.reply_text(
        "Вітаю, Сергію.\nЯ — твій бот. Без зайвих слів.\n\n"
        "/add — завдання\n"
        "/list — переглянути\n"
        "/ai — думати разом\n\n"
        "Працюємо."
    )

def add(update, context):
    text = ' '.join(context.args)
    if text:
        tasks.append(text)
        update.message.reply_text(f"✅ Додано: {text}")
    else:
        update.message.reply_text("❗ Напиши завдання після /add")

def show_list(update, context):
    if tasks:
        update.message.reply_text('\n'.join([f"{i+1}. {t}" for i, t in enumerate(tasks)]))
    else:
        update.message.reply_text("📭 Завдань поки немає.")

def ai(update, context):
    prompt = update.message.text.replace('/ai', '').strip()
    if not prompt:
        update.message.reply_text("❗ Напиши запит після /ai")
        return
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response['choices'][0]['message']['content']
        update.message.reply_text(answer)
    except Exception as e:
        update.message.reply_text("❌ GPT помилка")

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dp = Dispatcher(bot, None, workers=0)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("list", show_list))
    dp.add_handler(CommandHandler("ai", ai))
    dp.process_update(update)
    return "ok"

@app.route("/", methods=["GET"])
def home():
    return "Bot is alive"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
