import os
import sys
import threading
import telebot
from http.server import HTTPServer, BaseHTTPRequestHandler

# ======== НАСТРОЙКИ ========
TOKEN = "7948953181:AAGZMCSzF7pJq_6EmgCx9VW5QS6ZTJqu-zA"
ADMIN_ID = 8310408786
# ===========================

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Вітаємо!\n\nЩоб швидко отримати відповіді на всі запитання про роботу на біржі, перегляньте, будь ласка, цю сторінку:\nhttps://best-expert.com.ua/freelance/\n\nЦе заощадить ваш час і допоможе швидше розпочати роботу.")
    bot.send_message(ADMIN_ID, f"🆕 Новий користувач: @{message.from_user.username} (ID: {message.from_user.id})")

@bot.message_handler(func=lambda message: message.chat.id != ADMIN_ID)
def forward_to_admin(message):
    try:
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        bot.send_message(ADMIN_ID, f"✉️ Від {message.from_user.first_name} (@{message.from_user.username}):\n{message.text}")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Помилка при пересиланні: {e}")

@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.reply_to_message)
def reply_to_user(message):
    try:
        if message.reply_to_message.forward_from:
            user_id = message.reply_to_message.forward_from.id
            bot.send_message(user_id, f"✉️ Відповідь від підтримки:\n{message.text}")
            bot.reply_to(message, "✅ Відповідь надіслано!")
        else:
            bot.reply_to(message, "❌ Не можу визначити користувача")
    except Exception as e:
        bot.reply_to(message, f"❌ Помилка: {e}")

# Функція запуску бота
def run_bot():
    try:
        print("✅ Бот запускається...")
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Помилка бота: {e}")

# ========== ВЕБ-СЕРВЕР ДЛЯ RENDER ==========
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    
    def log_message(self, format, *args):
        return  # Вимкнути логи веб-сервера

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"🌐 Веб-сервер запущено на порту {port}")
    server.serve_forever()

# Запускаємо бота у фоновому потоці
threading.Thread(target=run_bot, daemon=True).start()

# Запускаємо веб-сервер (головний потік)
if __name__ == "__main__":
    run_http_server()
