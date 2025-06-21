import os
import sys
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from aiogram.types import InputMediaPhoto
import re
import random
import asyncio
from aiosend import CryptoPay, MAINNET
import sqlite3
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import pytz
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, Message
from aiogram.utils.keyboard import  InlineKeyboardBuilder
from aiosend import CryptoPay
from aiogram import F
import asyncio
import logging
import aiohttp
import sys
import asyncio
from contextlib import suppress
import logging
import sys
import os
from os import getenv
import sqlite3
import random
import re
import datetime
import time
from aiogram.exceptions import TelegramBadRequest
from typing import Any
from aiogram import types
from aiogram import Router
from aiogram import Bot, Dispatcher, F   
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.types import PreCheckoutQuery, LabeledPrice
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton , InlineKeyboardMarkup , InlineKeyboardButton , CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from datetime import datetime, timedelta
from aiogram.types import ChatPermissions
from aiogram.enums import ChatType
from aiogram.methods.send_gift import SendGift
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application



# ===== НАСТРОЙКА ЛОГИРОВАНИЯ =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

# ===== КОНФИГУРАЦИЯ (ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ) =====
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Обязательно!
SEND_API_KEY = os.getenv("SEND_API_KEY")  # Обязательно!
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@LunaBetChannel")
ADMIN_ID = int(os.getenv("ADMIN_ID", 767154085))  # Ваш ID в Telegram
logger = logging.getLogger(__name__)
connect = sqlite3.connect('lunab3t.db')
cursor = connect.cursor()

# ===== ПРОВЕРКА НАЛИЧИЯ КЛЮЧЕВЫХ ПЕРЕМЕННЫХ =====
if not BOT_TOKEN:
    logging.error("❌ ОШИБКА: Не указан BOT_TOKEN в переменных окружения!")
    sys.exit(1)

if not SEND_API_KEY:
    logging.error("❌ ОШИБКА: Не указан SEND_API_KEY в переменных окружения!")
    sys.exit(1)

WEB_SERVER_HOST = "0.0.0.0"  
WEB_SERVER_PORT = int(os.getenv("PORT", 8080)) 
WEBHOOK_PATH = "/webhook"
BASE_WEBHOOK_URL = os.getenv("WEBHOOK_URL")  

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
send_client = CryptoPay(token=SEND_API_KEY)




# ===== ОСНОВНЫЕ ФУНКЦИИ =====
async def on_startup():
    """Действия при запуске бота"""
    try:
        if BASE_WEBHOOK_URL:
            await bot.set_webhook(
                f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}",
                drop_pending_updates=True
            )
        await bot.send_message(ADMIN_ID, "🤖 Бот успешно запущен!")
    except Exception as e:
        logging.error(f"🚨 Ошибка при запуске: {e}")
        raise

async def on_shutdown():
    """Действия при выключении бота"""
    try:
        if BASE_WEBHOOK_URL:
            await bot.delete_webhook()
        await bot.send_message(ADMIN_ID, "⚠️ Бот выключается...")
        await bot.session.close()
    except Exception as e:
        logging.error(f"🚨 Ошибка при выключении: {e}")

async def keep_alive():
    """Регулярные запросы, чтобы Render не усыплял бота"""
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BASE_WEBHOOK_URL or 'http://localhost'}/ping") as resp:
                    logging.info(f"🔁 Keep-alive ping: {resp.status}")
        except Exception as e:
            logging.error(f"🚨 Keep-alive error: {e}")
        await asyncio.sleep(300)

async def ping_handler(request: web.Request):
    """Endpoint для проверки работы бота"""
    return web.Response(text="✅ Bot is alive")

async def setup_webhook():
    """Настройка вебхука"""
    app = web.Application()
    app.router.add_get("/ping", ping_handler)
    
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    
    return app




LOGS_CHANNEL_ID = -1002644395732
SUPPORT_ADMIN_ID = 767154085 
class SupportStates(StatesGroup):
    waiting_for_message = State()




cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER,
    username TEXT,
    plays INTEGER,
    wins INTEGER,
    loses INTEGER,
    reg_date TEXT
)
""")
connect.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS promocodes(
    name TEXT PRIMARY KEY,
    max_uses INTEGER,
    used INTEGER DEFAULT 0
)
""")
connect.commit()




menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💼 Профиль"), KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="❗ Поддержка")]
    ], 
    resize_keyboard=True
)



# ========= BOT =========


@dp.message(Command('start'))
async def start_cmd(message: types.Message, state: FSMContext = None):
    username = message.from_user.username
    user_id = message.from_user.id
    name = message.from_user.full_name
    fullname = f'<a href="t.me/{username}">{name}</a>'
    moscow_time = datetime.now(pytz.timezone('Europe/Moscow')).strftime("%d.%m.%Y %H:%M")

    # === Проверка подписки ===
    try:
        member = await bot.get_chat_member('@LunaBetChannel', user_id)
        if member.status == 'left':
            await message.answer(
                f"<b>👋 {fullname}, чтобы пользоваться ботом, сначала подпишитесь на наш канал: @LunaBetChannel\n</b>"
                f"После этого снова введите /start.",
                parse_mode='HTML'
            )
            return
        
    except Exception as e:
        logging.error(f"Ошибка при проверке подписки: {e}")
        await message.answer("⚠️ Не удалось проверить подписку. Попробуйте позже.", parse_mode='html')
        return

    # === Продолжение если подписан ===
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    exists = cursor.fetchone()
    if state:
        await state.clear()

    if not exists:
        cursor.execute(
            "INSERT INTO users (user_id, username, plays, wins, loses, reg_date) VALUES (?, ?, 0, 0, 0, ?)",
            (user_id, username, moscow_time)
        )
        connect.commit()

    photo_url = "https://i.postimg.cc/3rDnXD22/image.jpg"
    cursor.execute("SELECT reg_date FROM users WHERE user_id = ?", (user_id,))
    reg_date = cursor.fetchone()[0]

    this = f'<a href="https://t.me/LunaBetChannel/3">это</a>'
    await message.answer_photo(
        photo=photo_url,
        caption=f"""
<b>⚡ {fullname}, добро пожаловать в <u>Luna Bet</u></b>

<blockquote>«Каждое мгновение — это ставка. Вопрос в том, играешь ты или просто ждёшь.» — Харуки Мураками</blockquote>

<i>Чтобы сделать ставку, ОБЯЗАТЕЛЬНО прочти <b>{this}</b></i>
""",
        parse_mode="HTML",
        reply_markup=menu
    )



from aiogram.types import InputMediaPhoto
@dp.message(lambda m: m.text == "📊 Статистика")
async def show_stats(message: types.Message):
    cursor.execute("SELECT user_id, username, plays, wins, loses FROM users ORDER BY plays DESC LIMIT 10")
    top_users = cursor.fetchall()
    chat_id = message.chat.id
    await bot.send_message(chat_id, "📊")
    await asyncio.sleep(0.3)
    if not top_users:
        await message.answer("📉 Пока нет данных о ставках.")
        return

        

    text = "<b>[📊] Топ-10 игроков Luna Bet:</b>\n\n"
    for i, (user_id, username, plays, wins, loses) in enumerate(top_users, start=1):
        try:
            member = await bot.get_chat(user_id)
            full_name = member.full_name
        except:
            full_name = "Неизвестный"

        if username:
            user_link = f'<a href="https://t.me/{username}">{full_name}</a>'
        else:
            user_link = f'<a href="tg://user?id={user_id}">{full_name}</a>'

        text += f"<i>— {i}. {user_link}: игры — {plays} | победы — {wins}\n</i>"

    new_photo_url = "https://i.postimg.cc/Vk9dz2G3/image.jpg" 
    media = InputMediaPhoto(media=new_photo_url, caption=text, parse_mode="HTML")

    try:
        
        await message.answer_photo(photo=new_photo_url, caption=text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")
        print(f"Ошибка при edit_media: {e}")

    

from aiogram.utils.keyboard import InlineKeyboardBuilder

@dp.message(lambda m: m.text == "💼 Профиль")
async def show_profile(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    name = message.from_user.full_name
    chat_id = message.chat.id
    cursor.execute("SELECT plays, wins, loses FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    cursor.execute("SELECT reg_date FROM users WHERE user_id = ?", (user_id,))
    reg_date = cursor.fetchone()[0]
    await bot.send_message(chat_id, "💼")
    await asyncio.sleep(0.3)


    money = InlineKeyboardBuilder()
    money.button(text="💸 Сделать ставку", url="https://t.me/send?start=IVrfxN9IrHq8")
    money.adjust(1)

    if row:
        plays, wins, loses = row
    else:
        plays = wins = loses = 0

    if username:
        fullname = f'<a href="https://t.me/{username}">{name}</a>'
    else:
        fullname = name

    text = (
        f"""<b>[💼] Ваш личный профиль:</b>

<i>✏️ Ник: {fullname}
🗓️ Дата регистрации: {reg_date} (МСК)

🕹 Всего ставок: {plays}</i>    
   ↳ 🏆 <i>Побед: {wins}</i>
   ↳ 💥 <i>Проигрышей: {loses}</i>""")

    new_photo_url = "https://i.postimg.cc/Nf3Hs6gr/image.jpg"  

    media = InputMediaPhoto(media=new_photo_url, caption=text, parse_mode="HTML")

    try:
        await message.answer_photo(photo=new_photo_url, caption=text, parse_mode="HTML", reply_markup=money.as_markup())
    except Exception as e:
        await message.answer(f"Ошибка: {e}")
        print(f"Error editing media: {e}")




@dp.message(F.text == 'инвойс')
async def main_hand(message: types.Message):
    cp = CryptoPay("417594:AAei8HxkjFN6D6GWKeB9f46mK6Q3dghVDAH", MAINNET)

    invoice = await cp.create_invoice(
        amount=0.8,  
        asset="USDT",   
        description="Пополнение баланса"
    )

    await message.answer(f"Ссылка на оплату: {invoice.bot_invoice_url}")






@dp.channel_post()
async def check_payments(post: types.Message):
    playing = random.randint(1, 2)

    PHOTO_WIN_URL = 'https://i.postimg.cc/0N7Ld6Rf/image.jpg'
    PHOTO_LOSE_URL = 'https://i.postimg.cc/T1NSYggR/image.jpg'

    play = InlineKeyboardBuilder()
    play.button(text="🕹️ Сделать ставку", url='t.me/send?start=IVrfxN9IrHq8')
    play_markup = play.as_markup()

    # Всегда выполняем обработку, независимо от канала с логами
    text_with_formatting = post.html_text or ""
    raw_lines = (post.text or "").splitlines()
    comment = "Без комментария"

    for line in raw_lines:
        if "💬" in line:
            comment = line.replace("💬", "").strip()
            break

    # Логируем весь текст, чтобы проверить, что приходит
    logging.info(f"Обработано сообщение: {post.text}")
    logging.info(f"Текст с форматированием: {text_with_formatting}")
    
    match = re.search(
        r'<a href="tg://user\?id=(\d+)">\s*(.*?)\s*</a>'
        r'\s*(?:<a[^>]*?>)?отправил\(а\)(?:</a>)?'
        r'.*?'
        r'(?:<b><tg-emoji[^>]*?>.*?<\/tg-emoji>)?'
        r'(?:<b>)?([\d.,]+)\sUSDT(?:</b>)?',
        text_with_formatting,
        re.IGNORECASE
    )

    # Если парсинг успешен
    if match:
        try:
            user_id = match.group(1)
            displayed_nick_raw = match.group(2)
            amount = float(match.group(3).replace(',', '.'))

            displayed_nick_clean = re.sub(r'<[^>]*?>', '', displayed_nick_raw).strip()
            user_profile_link = f'<a href="tg://user?id={user_id}">{displayed_nick_clean}</a>'

            cp = CryptoPay("417594:AAei8HxkjFN6D6GWKeB9f46mK6Q3dghVDAH", MAINNET)

            # Проверяем комментарий и устанавливаем множитель
            if comment in ['орел', 'решка']:
                multiplier = 1.8
            elif comment in ['больше', 'меньше']:
                multiplier = 1.5
            elif comment in ['чет', 'нечет']:
                multiplier = 1.5
            else:
                multiplier = 1

            win_amount = round(amount * multiplier, 2)

            cursor.execute("UPDATE users SET plays = plays + 1 WHERE user_id = ?", (user_id,))
            connect.commit()

            # Логируем, что ставка принята
            logging.info(f"Ставка принята от пользователя: {user_profile_link}, сумма: {amount}, комментарий: {comment}")

            # Отправляем сообщение об успешной ставке
            await bot.send_message(chat_id=int(-1002744283282), text=f"""<b>💸 Ставка успешно принята!</b>
            
<blockquote>| Игрок: {user_profile_link}</blockquote>

<blockquote>| Сумма ставки: {amount}$</blockquote>

<blockquote>| Исход ставки: {comment}</blockquote>
""", parse_mode='html')

            if playing == 1:
                check = await cp.create_check(amount=win_amount, asset="USDT", pin_to_user_id=int(user_id))

                cursor.execute("UPDATE users SET wins = wins + 1 WHERE user_id = ?", (user_id,))

                await bot.send_photo(
                    chat_id=int(-1002744283282),
                    photo=PHOTO_WIN_URL,
                    caption=f"""
[⚡️] <b>Победа! Выпало значение «{playing}».</b>

<blockquote>Сумма выигрыша: <b>{win_amount} $</b>
Ваш выигрыш был отправлен вам в личные сообщения! 🎉</blockquote>

<i>Поздравляем вас, желаем удачи в следующих успешных ставках</i>
""",
                    parse_mode="HTML",
                    reply_markup=play_markup
                )

                builder = InlineKeyboardBuilder()
                builder.button(text="💸 Забрать приз", url=check.bot_check_url)
                reply_markup = builder.as_markup()

                await bot.send_photo(
                    chat_id=user_id,
                    photo=PHOTO_WIN_URL,
                    caption=f"""<b>[⚡️] Поздравляем вас, вы выиграли! 💥</b>
<i>⚡ Ваш выигрыш ниже:</i>""",
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
            else:
                cursor.execute("UPDATE users SET loses = loses + 1 WHERE user_id = ?", (user_id,))

                await bot.send_photo(
                    chat_id=int(-1002744283282),
                    photo=PHOTO_LOSE_URL,
                    caption=f"""
<b>⚡️ Проигрыш — это не конец, а начало нового шанса. Вам выпало значение «{playing}»</b>

<blockquote>Не забывайте, даже лучшие спортсмены иногда падают.
Каждое поражение — это шаг к большой победе, которой стоит ждать.</blockquote>

<i>Вперёд, к новым вершинам! Ваша победа уже близка! 💥</i>
""",
                    parse_mode="HTML",
                    reply_markup=play_markup
                )

        except Exception as e:
            logging.error(f"Ошибка при обработке сообщения: {e}", exc_info=True)

    else:
        logging.warning("Не удалось распарсить сообщение для ставки.")






cp = CryptoPay("417594:AAei8HxkjFN6D6GWKeB9f46mK6Q3dghVDAH", MAINNET)


@dp.message(Command("чеки"))
async def list_checks(message: types.Message):
    try:
        checks = await cp.get_checks(count=100)  # получаем 10 последних чеков

        if not checks:
            await message.answer("❌ Чеки не найдены.")
            return

        text = "<b>📋 Последние 10 чеков:</b>\n\n"
        for check in checks:
            text += (
                f"🆔 <code>{check.check_id}</code>\n"
                f"📌 Статус: <b>{check.status}</b>\n"
                f"⏰ Активирован: {check.activated_at or '—'}\n"
                f"🔗 <a href='{check.bot_check_url}'>Открыть чек</a>\n\n"
            )

        await message.answer(text, parse_mode='html')

    except Exception as e:
        await message.answer(f"⚠️ Ошибка при получении чеков:\n<code>{e}</code>")


@dp.message(F.text == "❗ Поддержка")
async def support_entry(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Продолжить", callback_data="support_continue"),
                InlineKeyboardButton(text="🔙 Вернуться", callback_data="back_to_start")
            ]
        ]
    )
    chat_id = message.chat.id
    await bot.send_message(chat_id, "❗")
    await asyncio.sleep(0.3)

    photo_url = "https://i.postimg.cc/76JMnpJq/image.jpg"

    await message.answer_photo(
        photo=photo_url,
        caption=f"""<b>[❗] Добро пожаловать, это поддержка проекта Luna Bet</b>
<i>Чтобы продолжить диалог с поддержкой, нажмите на кнопку <b>«Продолжить»</b> ниже.

⚡ Мы всегда будем рады вам помочь!</i>""",
        parse_mode="HTML",
        reply_markup=keyboard 
    )


@dp.callback_query(F.data == "back_to_start")
async def back_to_start(callback: types.CallbackQuery):
    await start_cmd(callback.message)
    await callback.answer()

@dp.callback_query(F.data == "support_continue")
async def support_continue(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(SupportStates.waiting_for_message)
    await callback.message.answer(
    f"""<b>⚡ Вы продолжили диалог</b>
<i>Расскажите, с чем вы столкнулись — мы поможем. Опишите суть вопроса или проблемы, избегая мета вопросов. Четко опишите вашу проблему — что случилось. Не спамьте, и не дублируйте проблему по несколько раз.
После этого мы свяжемся с вами как можно скорее. Спасибо!</i>""",
    parse_mode="HTML"
)

    await callback.answer()

@dp.message(SupportStates.waiting_for_message)
async def receive_support_message(message: types.Message, state: FSMContext):
    user = message.from_user
    username = f"@{user.username}" if user.username else f"{user.full_name}"
    user_link = f'<a href="tg://user?id={user.id}">{username}</a>'

    await bot.send_message(
        SUPPORT_ADMIN_ID,
        f"📩 <b>Новый запрос в поддержку</b>\n\n"
        f"👤 Пользователь: {user_link}\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"💬 Сообщение: {message.text}",
        parse_mode="HTML"
    )

    await message.answer("<b>Ваш запрос был отправлен. Спасибо! 🩷</b>", parse_mode='html')
    await state.clear()


@dp.message(Command("test"))
async def test(message: types.Message):
    await message.answer("Бот работает!")




# ===== ЗАПУСК БОТА =====
async def main():
    try:
        # Настройка веб-сервера
        app = await setup_webhook()
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(
            runner,
            host=WEB_SERVER_HOST,
            port=WEB_SERVER_PORT,
            reuse_port=True
        )
        
        await site.start()
        logging.info(f"🌐 Сервер запущен на порту {WEB_SERVER_PORT}")
        
        # Инициализация бота
        await on_startup()
        asyncio.create_task(keep_alive())
        
        # Бесконечный цикл
        while True:
            await asyncio.sleep(3600)
            
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logging.critical(f"💥 Критическая ошибка: {e}")
    finally:
        await on_shutdown()
        if 'runner' in locals():
            await runner.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.critical(f"💥 Не удалось запустить бота: {e}")
        sys.exit(1)

