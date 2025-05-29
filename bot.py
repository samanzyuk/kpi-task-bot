import os
from flask import Flask, request
from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
import openai
from datetime import datetime, timedelta
import pytz

TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
bot = Bot(token=TOKEN)
openai.api_key = OPENAI_KEY
app = Flask(__name__)
scheduler = BackgroundScheduler(timezone='Europe/Kyiv')
scheduler.start()

tasks = []

def start(update, context):
    keyboard = [["/add", "/list"], ["/remindme", "/ai"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        "Вітаю, Сергію. Обери дію:",
        reply_markup=reply_markup
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

def remindme(update, context):
    args = context.args
    if len(args) < 2:
        update.message.reply_text("⏰ Приклад: /remindme 10:00 написати листа")
        return
    try:
        time_str = args[0]
        task_text = ' '.join(args[1:])
        now = datetime.now(pytz.timezone('Europe/Kyiv'))
        remind_time = datetime.strptime(time_str, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day, tzinfo=pytz.timezone('Europe/Kyiv')
        )
        if remind_time < now:
            remind_time += timedelta(days=1)

        def send_reminder():
            bot.send_message(chat_id=update.effective_chat.id, text=f"🔔 Нагадування: {task_text}")

        scheduler.add_job(send_reminder, trigger='date', run_date=remind_time)
        update.message.reply_text(f"⏰ Нагадування встановлено на {remind_time.strftime('%H:%M')} — {task_text}")
    except:
        update.message.reply_text("❌ Формат неправильний. Спробуй: /remindme 14:30 зустріч")

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dp = Dispatcher(bot, None, workers=0)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("list", show_list))
    dp.add_handler(CommandHandler("ai", ai))
    dp.add_handler(CommandHandler("remindme", remindme))
    dp.process_update(update)
    return "ok"

@app.route("/", methods=["GET"])
def home():
    return "Bot is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
