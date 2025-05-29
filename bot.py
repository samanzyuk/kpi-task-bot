import os
import logging
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import openai

TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_KEY

logging.basicConfig(level=logging.INFO)
bot = telegram.Bot(token=TOKEN)

def start(update, context):
    update.message.reply_text(
        "Вітаю, Сергію.\nЯ — твій бот. Без зайвих слів.\n\n"
        "/add — завдання\n"
        "/list — переглянути\n"
        "/ai — думати разом\n\n"
        "Працюємо."
    )

tasks = []

def add_task(update, context):
    task_text = ' '.join(context.args)
    if task_text:
        tasks.append(task_text)
        update.message.reply_text(f"✅ Додано: {task_text}")
    else:
        update.message.reply_text("❗ Введи текст завдання після команди /add")

def list_tasks(update, context):
    if tasks:
        text = "\n".join([f"{i+1}. {task}" for i, task in enumerate(tasks)])
        update.message.reply_text(f"📋 Завдання:\n{text}")
    else:
        update.message.reply_text("📭 Завдань поки немає.")

def ai(update, context):
    prompt = update.message.text.replace('/ai', '').strip()
    if not prompt:
        update.message.reply_text("Напиши запит після /ai")
        return
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response['choices'][0]['message']['content']
        update.message.reply_text(answer)
    except Exception as e:
        update.message.reply_text("❌ Помилка GPT. Перевір ключ.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add_task))
    dp.add_handler(CommandHandler("list", list_tasks))
    dp.add_handler(CommandHandler("ai", ai))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
