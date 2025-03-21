from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
)
import logging

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния
USER_ID, SENDING_MESSAGE = range(2)

# База пользователей (хранит Telegram ID)
users_db = {}

# Старт бота
async def start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    users_db[user_id] = {"id": user_id}
    await update.message.reply_text(
        f"Привет! Я - MyChat. Бот для анонимной пересылки сообщений.\n\n"
        f"Ваш ID - {user_id}\n\n"
        "Введите Telegram ID получателя (например: 123456789)"
    )
    return USER_ID

# Обработка ID получателя
async def handle_user_id(update: Update, context: CallbackContext) -> int:
    try:
        receiver_id = int(update.message.text.strip())
        if receiver_id not in users_db:
            await update.message.reply_text(
                "❌ Пользователь с таким ID не найден. Проверьте правильность ID."
            )
            return USER_ID

        context.user_data['receiver_id'] = receiver_id
        await update.message.reply_text(
            f"✅ Вы подключены к чату с пользователем {receiver_id}.\n"
            "Отправьте текстовое сообщение или фото.\n"
            "⚠ Голосовые, видео-кружки и стикеры не поддерживаются!"
        )
        return SENDING_MESSAGE

    except ValueError:
        await update.message.reply_text("❌ Введите корректный числовой ID.")
        return USER_ID

# Отправка сообщений
async def send_message(update: Update, context: CallbackContext) -> int:
    if update.message.voice or update.message.video_note or update.message.sticker:
        await update.message.reply_text("❌ Ошибка! Сообщения такого типа не поддерживаются.")
        return SENDING_MESSAGE

    receiver_id = context.user_data.get('receiver_id')
    if receiver_id:
        if update.message.text:
            await context.bot.send_message(receiver_id, f"📩 Новое анонимное сообщение:\n\n{update.message.text}")
        elif update.message.photo:
            caption = update.message.caption if update.message.caption else "Описание отсутствует."
            await context.bot.send_photo(
                receiver_id, 
                update.message.photo[-1].file_id, 
                caption=f"📩 Новое анонимное фото\n\n{caption}"
            )

        await update.message.reply_text("✅ Успешно отправлено!")
        return ConversationHandler.END

    return USER_ID

# Команда /send
async def send_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "🔁 Чтобы отправить сообщение, сначала введите ID через /start."
    )

# Отмена
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("🚫 Действие отменено.")
    return ConversationHandler.END

# Главная функция
def main():
    application = Application.builder().token("8167761012:AAEdL2As9eYz-zoCEZQZCDumB6O0A0zlPtA").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_id)],
            SENDING_MESSAGE: [MessageHandler(filters.TEXT | filters.PHOTO, send_message)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(CommandHandler('send', send_command))
    application.add_handler(conv_handler)

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
