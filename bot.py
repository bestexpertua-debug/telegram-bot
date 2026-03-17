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
        msg = message.reply_to_message
        user_id = None

        # Спосіб 1: переслане повідомлення
        if hasattr(msg, 'forward_from') and msg.forward_from:
            user_id = msg.forward_from.id

        # Спосіб 2: через forward_from_message
        elif hasattr(msg, 'forward_from_message') and msg.forward_from_message:
            if msg.forward_from_message.from_user:
                user_id = msg.forward_from_message.from_user.id

        # Спосіб 3: звичайне повідомлення (не переслане)
        elif msg.from_user and msg.from_user.id != ADMIN_ID:
            user_id = msg.from_user.id

        # Спосіб 4: forward_origin (новий формат Telegram)
        elif hasattr(msg, 'forward_origin') and msg.forward_origin:
            if hasattr(msg.forward_origin, 'sender_user') and msg.forward_origin.sender_user:
                user_id = msg.forward_origin.sender_user.id

        if user_id:
            bot.send_message(user_id, f"✉️ Відповідь від підтримки:\n{message.text}")
            bot.reply_to(message, "✅ Відповідь надіслано!")
        else:
            bot.reply_to(message, "❌ Не вдалося знайти користувача. Спробуй відповісти на оригінальне переслане повідомлення.")

    except Exception as e:
        bot.reply_to(message, f"❌ Помилка: {e}")

def run_bot():
    try:
        print("✅ Бот запускається...")
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Помилка бота: {e}")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    def log_message(self, format, *args):
        return

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"🌐 Веб-сервер запущено на порту {port}")
    server.serve_forever()

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    run_http_server()
