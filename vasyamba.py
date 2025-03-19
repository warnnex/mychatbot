from flask import Flask, request
from telegram import Bot

app = Flask(__name__)

# Замените на токен вашего Telegram-бота
TOKEN = "7819571229:AAHbUZh8NjLj2Cbbp4B5xhUS2q278xARbsg"
CREATOR_ID = 7630523828  # Ваш Telegram ID
bot = Bot(token=TOKEN)

@app.route('/start', methods=['POST'])
def handle_start():
    data = request.get_json()  # Получаем JSON-запрос от Telegram
    
    if data and 'message' in data:
        user = data['message']['from']
        username = user.get('username', 'Без ника')  # Получаем username пользователя
        username = f"@{username}" if username != "Без ника" else username
        chat_id = data['message']['chat']['id']

        # Отправляем сообщение создателю
        bot.send_message(chat_id=CREATOR_ID, text=f"Новый юзер: {username}")
        
        # Отправляем ответ пользователю
        bot.send_message(chat_id=chat_id, text="Добро пожаловать!")
    
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
