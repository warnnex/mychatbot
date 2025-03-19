import asyncio
import logging
import random
import string

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# Твой токен и ID
TOKEN = "7556436194:AAEjr6eugXufrFjW3zQEZB388kOyOukzm9o"
ADMIN_ID = 7571837281  # Твой Telegram ID
ADMIN_PASSWORD = "Nazar2810"

bot = Bot(token=TOKEN)
dp = Dispatcher()

referrals = {}
admin_sessions = {}

# Генерация случайного реферального кода
def generate_ref_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

@dp.message(Command("start"))
async def start(message: Message):
    user_id = message.from_user.id
    ref_code = generate_ref_code()
    referrals[ref_code] = user_id
    bot_info = await bot.get_me()
    bot_username = bot_info.username

    await message.answer(
        f"Привет! Я бот WorldHack.\n\n"
        f"Твоя бесплатная реф. ссылка: https://t.me/{bot_username}?start={ref_code}\n"
        f"Когда кто-то перейдёт по ней, тебе придут его данные."
    )

@dp.message()
async def handle_referral(message: Message):
    if message.text.startswith("/start "):
        ref_code = message.text.split(" ")[1]
        if ref_code in referrals:
            referrer_id = referrals[ref_code]
            new_user = message.from_user

            # Кнопка для взаимодействия с ботом
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton("Написать боту", url=f"https://t.me/{(await bot.get_me()).username}")]
                ]
            )

            try:
                await bot.send_message(
                    referrer_id,
                    f"🔔 Новый реферал!\n"
                    f"👤 Имя: {new_user.full_name}\n"
                    f"📢 Юзернейм: @{new_user.username or 'Нет'}\n"
                    f"🆔 ID: {new_user.id}",
                    reply_markup=keyboard
                )
                logging.info(f"Сообщение отправлено {referrer_id} о пользователе {new_user.id}")
            except Exception as e:
                logging.error(f"Ошибка отправки сообщения рефереру: {e}")
                await message.answer("❌ Бот не может отправить сообщение пригласившему.")

        else:
            await message.answer("❌ Ошибка: реферальный код не найден.")

@dp.message(Command("give"))
async def give_access(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("У тебя нет доступа!")
    await message.answer("Введите пароль:")
    admin_sessions[message.from_user.id] = "waiting_password"

@dp.message()
async def handle_password(message: Message):
    user_id = message.from_user.id
    if user_id in admin_sessions and admin_sessions[user_id] == "waiting_password":
        if message.text == ADMIN_PASSWORD:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Выдать ссылку", callback_data="give_link")],
                    [InlineKeyboardButton(text="Выйти", callback_data="exit_admin")]
                ]
            )
            await message.answer("✅ Пароль верный.", reply_markup=keyboard)
            admin_sessions[user_id] = "admin_menu"
        else:
            await message.answer("❌ Неверный пароль!")

@dp.callback_query()
async def handle_admin_menu(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id in admin_sessions and admin_sessions[user_id] == "admin_menu":
        if callback_query.data == "give_link":
            await bot.send_message(user_id, "Введите юзернейм пользователя (@username):")
            admin_sessions[user_id] = "waiting_username"
        elif callback_query.data == "exit_admin":
            del admin_sessions[user_id]
            await bot.send_message(user_id, "Вы вышли из админ-меню.")

@dp.message()
async def handle_username(message: Message):
    user_id = message.from_user.id
    if user_id in admin_sessions and admin_sessions[user_id] == "waiting_username":
        target_username = message.text.replace("@", "")
        ref_code = generate_ref_code()
        referrals[ref_code] = "5_activations"
        bot_info = await bot.get_me()
        bot_username = bot_info.username

        try:
            await bot.send_message(
                message.chat.id,
                f"✅ Выдал ссылку для @{target_username}:\n"
                f"https://t.me/{bot_username}?start={ref_code} (5 активаций)"
            )
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
            logging.error(f"Ошибка: {e}")
        del admin_sessions[user_id]

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
