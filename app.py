from flask import Flask, request # type: ignore
from telegram import Update, Bot # type: ignore
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, Dispatcher # type: ignore
import random
import sqlite3

# Создание Flask приложения
app = Flask(__name__)

# Телеграм-бот токен (замените своим)
TOKEN = "8150044444:AAFAKUM_FeJZspJbN9ipCoHKa0ai4LQiRnQ"
bot = Bot(token=TOKEN)

# Список хобби
HOBBIES = [
    "Рисование", "Игра на гитаре", "Йога", "Программирование", "Чтение книг",
    "Фотография", "Кулинария", "Вышивание", "Путешествия", "Садоводство"
]

# Мотивационные сообщения
MOTIVATIONAL_QUOTES = [
    "Ты на правильном пути! Продолжай учиться!",
    "Каждый день — шаг к мастерству!",
    "Маленькие шаги ведут к большим результатам!",
    "Не бойся ошибок, они учат нас быть лучше.",
    "Твое хобби делает тебя уникальным!"
]

# Подключение базы данных для пользователей
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            hobby TEXT
        )
    """)
    conn.commit()
    conn.close()

def set_user_hobby(chat_id, hobby):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO users (chat_id, hobby) VALUES (?, ?)
    """, (chat_id, hobby))
    conn.commit()
    conn.close()

def get_user_hobby(chat_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT hobby FROM users WHERE chat_id = ?", (chat_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Команды бота
def start(update: Update, context):
    update.message.reply_text(
        "Привет! Я бот, который поможет тебе выбрать хобби и поддерживать тебя. "
        "Напиши /choose, чтобы выбрать хобби!"
    )

def choose_hobby(update: Update, context):
    chat_id = update.effective_chat.id
    hobby = random.choice(HOBBIES)
    set_user_hobby(chat_id, hobby)
    update.message.reply_text(f"Твое новое хобби: {hobby}! Готов начать?")

def motivate(update: Update, context):
    chat_id = update.effective_chat.id
    hobby = get_user_hobby(chat_id)
    if hobby:
        quote = random.choice(MOTIVATIONAL_QUOTES)
        update.message.reply_text(f"{quote} Как продвигается {hobby}?")
    else:
        update.message.reply_text("Сначала выбери хобби с помощью команды /choose!")

def help_command(update: Update, context):
    update.message.reply_text(
        "Вот, что я умею:\n"
        "/start — начать работу\n"
        "/choose — выбрать хобби\n"
        "/motivate — получить поддержку\n"
        "/help — список команд"
    )

# Flask endpoint для Telegram вебхуков
@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(), bot)
    dispatcher.process_update(update)
    return "OK"

# Настройка обработчиков
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("choose", choose_hobby))
dispatcher.add_handler(CommandHandler("motivate", motivate))
dispatcher.add_handler(CommandHandler("help", help_command))

# Инициализация базы данных
init_db()

if __name__ == "__main__":
    # Запуск Flask сервера
    app.run(port=5000)
