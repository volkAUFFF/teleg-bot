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
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@AsartiaCasino")
ADMIN_ID = int(os.getenv("ADMIN_ID", 767154085))  # Ваш ID в Telegram

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




class BetStates(StatesGroup):
    crypto_bet = State()
    star_bet = State()
    choose_prediction = State()


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


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    username = message.from_user.full_name
    username1 = message.from_user.username
    hrefka = f't.me/{username1}'
    user_id = message.from_user.id

    chat_member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)

    kb = InlineKeyboardBuilder()
    kb.button(text="⚡ Играть", callback_data="make_bet")
    kb.button(text="💼 Профиль", callback_data="profile")
    kb.button(text='❓Помощь', url='https://telegra.ph/')
    kb.button(text="⚡ Администрция", url="https://t.me/AsartiaCasino/137")
    kb.button(text="❓ Как сделать ставку", url="t.me/AsartiaCasino/40")
    kb.adjust(2)  

    if chat_member.status not in ['member', 'administrator', 'creator']:
            channel = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎰 Перейти в канал", url=f"t.me/AsartiaCasino")]
            ])
            await message.answer(
                "<b>❗ Вы не подписаны на канал @AsartiaCasino. Пожалуйста, подпишитесь, чтобы продолжить. Когда подпишитесь, снова напишите /start</b>",
                reply_markup=channel, parse_mode='html'
            )
    else:

        await message.answer(
        f'<b>💎 <a href="{hrefka}">{username}</a>, добро пожаловать в бота "Asartia Casino"\n\n<pre>Ставь легко, выигрывай быстро, твой шанс сорвать куш уже здесь!</pre>\n\n — Выбери опцию:</b>',
        reply_markup=kb.as_markup(),
        disable_web_page_preview=True,
        parse_mode='html'
    )


@dp.callback_query(F.data == "profile")
async def choose_bet_type(callback: types.CallbackQuery):
    await callback.message.delete()

    username = callback.message.from_user.full_name\

    href = 't.me/AsartiaCasino'
    kb = InlineKeyboardBuilder()
    kb.button(text="💵 Сделать ставку", callback_data="make_bet")
    kb.button(text="⚡ Администрция", url="https://t.me/AsartiaCasino/137")
    kb.button(text="❓ Как сделать ставку", url="t.me/AsartiaCasino/40")
    kb.adjust(2)
   

    await callback.message.answer(
        f'<i>💥 Ваш профиль:</i>\n<pre><b>  Ник: <u>{username}</u>\n  Айди: <u>{callback.message.from_user.id}</u></b></pre>\n\n<b><a href="t.me/AsartiaCasino">⚡ Канал с новостями</a> | <a href="https://t.me/AsartiaCasino/40"> Как сделать ставку</a></b>',
        reply_markup=kb.as_markup(),
        parse_mode='html',
        disable_web_page_preview=True
    )


@dp.callback_query(F.data == "make_bet")
async def choose_bet_type(callback: types.CallbackQuery):
    await callback.message.delete()

    kb = InlineKeyboardBuilder()
    kb.button(text="💸 Ставка // крипто бот", callback_data="crypto_bet")
    kb.button(text="💫 Ставка // звезды", callback_data="star_bet")
    kb.button(text="⚡ Администрция", url="https://t.me/AsartiaCasino/137")
    kb.button(text="❓ Как сделать ставку", url="t.me/AsartiaCasino/40")
    kb.adjust(2)  

    await callback.message.answer(
        "<pre>😋 Выбери опцию ниже:</pre>",
        reply_markup=kb.as_markup(),
        parse_mode='html'
    )

@dp.callback_query(F.data == "crypto_bet")
async def crypto_bet(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        "<pre>💵 Введи сумму ставки в цыфрах:</pre>\n<b>❗ Минимальная сумма ставки — <u>0.1 $</u></b>",
        parse_mode='html'
    )
    await state.set_state(BetStates.crypto_bet)


async def check_payment(invoice_url: str, message: Message, user_id):
    user = message.from_user
    username = user.full_name
    username1 = user.username or user.id
    hrefka = f't.me/{username1}'
    playy = random.randint(1, 300)

    try:
        while True:
            invoices = await send_client.get_invoices()
            for invoice in invoices:
                if invoice.bot_invoice_url == invoice_url and invoice.status == "paid":
                    inv = invoice.amount  
                    win = inv * 1.5
                    sent_msg = await message.answer(f"""<b><pre>💥 Ставка по криптоботу успешно принята!</pre></b>
<i>Игрок: <u><a href="{hrefka}">{username}</a></u>
Сумма: <u>{invoice.amount} $</u></i>""", parse_mode='html', disable_web_page_preview=True)

                    await bot.send_message(
    chat_id='@AsartiaCasino',
    text=f"""<b><pre>💥 Ставка по криптоботу успешно принята!</pre></b>
<i>Игрок: <u><a href="{hrefka}">{username}</a></u>
Сумма: <u>{invoice.amount} $</u></i>""",
    parse_mode='html',
    disable_web_page_preview=True
)


                    await asyncio.sleep(0.5)
                    await bot.send_dice(chat_id=message.chat.id, emoji="🎲")

                    await bot.send_dice(chat_id='@AsartiaCasino', emoji="🎲")
                    await asyncio.sleep(1)
                    if playy == 1:
                        print(f"playy после броска: {playy}")
                        check = await send_client.create_check(
            asset="USDT",
            amount=win,
            pin_to_user_id=user_id
                    )
                        builder3 = InlineKeyboardBuilder()
                        builder3.button(text="💰 Забрать чек", url=check.bot_check_url)
                        win_markup = builder3.as_markup()
                        await bot.send_message(chat_id=message.chat.id, text=f"""<b>━━━━━━━━━━━━━━━
🏆 <a href="{hrefka}">{username}</a>, Вы выиграли!</b>
💵 Сумма выигрыша: <u>{win}</u>

<pre>Фортуна на твоей стороне, возвращайся за новым выигрышем. Ваш выигрыш в личных сообщениях!</pre>

<b><a href="https://t.me/AsartiaCasino">⚡ Канал с новостями</a> | <a href="https://t.me/AsartiaCasino/40">Как сделать ставку</a></b>
""", 
                                               reply_to_message_id=sent_msg.message_id, 
                                               parse_mode='html', 
                                               disable_web_page_preview=True,
                                               reply_markup=win_markup)
                        
                        
                        

                        
                        await bot.send_message(
    chat_id='@AsartiaCasino',
    text=f"""<b>━━━━━━━━━━━━━━━
🏆 <a href="{hrefka}">{username}</a>, Вы выиграли!</b>
💵 Сумма выигрыша: <u>{win}</u>

<pre>Фортуна на твоей стороне, возвращайся за новым выигрышем. Ваш выигрыш в личных сообщениях!</pre>

<b><a href="https://t.me/AsartiaCasino">⚡ Канал с новостями</a> | <a href="https://t.me/AsartiaCasino/40">Как сделать ставку</a></b>
""",
    parse_mode='html',
    disable_web_page_preview=True
)

                    else:
                        print(f"playy после броска: {playy}")
                        await bot.send_message(chat_id=message.chat.id, text=f"""━━━━━━━━━━━━━━━
<b>❌ <a href="{hrefka}">{username}</a>, Вы проиграли!</b>

<pre>Желаем удачи в следующих играх, не опускайте руки!</pre>

<b><a href="t.me/AsartiaCasino">⚡ Канал с новостями</a> | <a href="https://t.me/AsartiaCasino/40">Как сделать ставку</a></b>
""", reply_to_message_id=sent_msg.message_id,
parse_mode='html',
disable_web_page_preview=True)
                        
                
                        
                        
                        await bot.send_message(chat_id='@AsartiaCasino', 
                        text=f"""━━━━━━━━━━━━━━━
<b>❌ <a href="{hrefka}">{username}</a>, Вы проиграли!</b>

<pre>Желаем удачи в следующих играх, не опускайте руки!</pre>

<b><a href="t.me/AsartiaCasino">⚡ Канал с новостями</a> | <a href="https://t.me/AsartiaCasino/40">Как сделать ставку</a></b>
""", 
                        parse_mode='html', 
                        disable_web_page_preview=True)



                    return
            await asyncio.sleep(5)
    except Exception as e:
        logging.error(f"Ошибка при проверке платежа: {e}")




@dp.message(BetStates.crypto_bet)
async def handle_crypto_bet(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
        if amount < 0.1:
            await message.answer("<b>❗Минимальная сумма ставки — <u>0.1 $</u></b>", parse_mode='html')
            return
        elif amount > 0.9:
            await message.answer("<b>❗Максимальная сумма ставки — <u>0.9 $</u></b>", parse_mode='html')
            return

        await state.update_data(bet_amount=amount)

        kb = InlineKeyboardBuilder()
        kb.button(text="🎯 Больше (4-6)", callback_data="prediction_high")
        kb.button(text="🎯 Меньше (1-3)", callback_data="prediction_low")
        kb.adjust(2)

        await message.answer(
            "<pre>🔮 Выберите, что выпадет на кубике:</pre>",
            reply_markup=kb.as_markup(),
            parse_mode='html'
        )
        await state.set_state(BetStates.choose_prediction)

    except ValueError:
        await message.answer("<b>❗Введите корректную сумму</b>", parse_mode='html')


async def check_random_payment(invoice_url: str, message: Message, user_id: int, prediction: str):
    user = message.from_user
    username = user.full_name
    username1 = user.username or str(user.id)
    hrefka = f't.me/{username1}'

    try:
        while True:
            invoices = await send_client.get_invoices()
            for invoice in invoices:
                if invoice.bot_invoice_url == invoice_url and invoice.status == "paid":
                    amount = invoice.amount
                    win_amount = amount * 1.5

                    await message.answer(
    f"<pre>💥 Ставка по криптоботу успешно принята!</pre>\n<i>Игрок: <a href=\"{hrefka}\">{username}</a>\n Сумма: <u>{amount} $</u></i>\n<i>Выбор: {'Больше' if prediction == 'high' else 'Меньше'}</i>",
    parse_mode='html', disable_web_page_preview=True
)

                    await asyncio.sleep(1)
                    dice = await bot.send_dice(chat_id=message.chat.id, emoji="🎲")
                    await asyncio.sleep(3)

                    outcome = random.choice(["win", "lose"])

                    if outcome == "win":
                        check = await send_client.create_check(
                            asset="USDT",
                            amount=win_amount,
                            pin_to_user_id=user_id
                        )
                        win_kb = InlineKeyboardBuilder()
                        win_kb.button(text="💰 Забрать выигрыш", url=check.bot_check_url)

                        await bot.send_message(
    chat_id=message.chat.id,
    text=f'<b>━━━━━━━━━━━━━━━\n🏆 <a href="{hrefka}">{username}</a>, Вы выиграли!\nСумма выигрыша: <u>{win_amount:.2f} $</u>\n<pre><i>Фортуна на твоей стороне, возвращайся за новым выигрышем!</i></pre></i></pre>\n\n<a href="t.me/AsartiaCasino">⚡ Канал с новостями</a> | <a href="https://t.me/AsartiaCasino/40"> Как сделать ставку</a></b>',
    reply_markup=win_kb.as_markup(),
    parse_mode='html',
    disable_web_page_preview=True
)

                        await bot.send_message(
    chat_id=message.chat.id,
    text=f'<b>━━━━━━━━━━━━━━━\n🏆 <a href="{hrefka}">{username}</a>, Вы выиграли!\nСумма выигрыша: <u>{win_amount:.2f} $</u>\n<pre><i>Фортуна на твоей стороне, возвращайся за новым выигрышем. Выигрыш отправил тебе в личные сообщения!</i></pre></i></pre>\n\n<a href="t.me/AsartiaCasino">⚡ Канал с новостями</a> | <a href="https://t.me/AsartiaCasino/40"> Как сделать ставку</a></b>',
    parse_mode='html',
    disable_web_page_preview=True
)

                    
                    else:
                        await bot.send_message(
                            chat_id=message.chat.id,
                            text=f'━━━━━━━━━━━━━━━\n<b>❌ <a href="{hrefka}">{username}</a>, Вы проиграли!</b>\n<i><pre>Желаем удачи в следующих играх, не опускайте руки!</pre></i>\n\n<b><a href="t.me/AsartiaCasino">⚡ Канал с новостями</a> | <a href="https://t.me/AsartiaCasino/40"> Как сделать ставку</a></b>',
                            parse_mode='html',
                            disable_web_page_preview=True
                        )
                        await bot.send_message(
                            chat_id='@AsartiaCasino',
                            text=f'━━━━━━━━━━━━━━━\n<b>❌ <a href="{hrefka}">{username}</a>, Вы проиграли!</b>\n<i><pre>Желаем удачи в следующих играх, не опускайте руки!</pre></i>\n\n<b><a href="t.me/AsartiaCasino">⚡ Канал с новостями</a> | <a href="https://t.me/AsartiaCasino/40"> Как сделать ставку</a></b>',
                            parse_mode='html',
                            disable_web_page_preview=True
                        )
                    return
            await asyncio.sleep(5)
    except Exception as e:
        logging.error(f"[❗] Ошибка в check_random_payment: {e}")



@dp.callback_query(F.data.startswith("prediction_"))
async def handle_prediction(callback: CallbackQuery, state: FSMContext):
    prediction = callback.data.split("_")[1]  
    data = await state.get_data()
    amount = data['bet_amount']

    invoice = await send_client.create_invoice(
        amount=amount,
        asset="USDT",
        description=f"Ставка на {'Больше' if prediction == 'high' else 'Меньше'}",
        payload=str(callback.from_user.id),
        allow_anonymous=False
    )

    invoice_url = invoice.bot_invoice_url

    kb = InlineKeyboardBuilder()
    kb.button(text="💵 Оплатить ставку", url=invoice_url)
    kb.adjust(1)

    await callback.message.answer(
        f"<i>💰 Оплатите ставку на сумму <u>{amount} $</u></i>",
        reply_markup=kb.as_markup(),
        parse_mode='html'
    )

    user_id = callback.from_user.id
    asyncio.create_task(check_random_payment(invoice_url, callback.message, user_id, prediction))

    await state.clear()
    await callback.message.delete()




@dp.callback_query(F.data == "star_bet")
async def star_bet(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer("<pre>✨ Введи сумму ставки в цыфрах:</pre>\n<b>❗ Минимальная сумма ставки — <u>15 звезд</u></b>", parse_mode='html')
    await state.set_state(BetStates.star_bet)


@dp.pre_checkout_query(lambda query: True)
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message(BetStates.star_bet)
async def handle_star_bet(message: Message, state: FSMContext):
    try:
        stars = int(message.text)
        if stars < 15:
            await message.answer("<b>❗Минимальная сумма ставки — <u>15 звезд</u></b>", parse_mode='html')
            return
        elif stars > 50: 
            await message.answer("<b>❗Максимальная сумма ставки — <u>50 звезд</u></b>", parse_mode='html')
            return
        prices = [LabeledPrice(label="Ставка", amount=stars)]
        payload = f"star_bet_{stars}"
        await bot.send_invoice(
            chat_id=message.chat.id,
            title="Ставка за звезды",
            description="Оплата ставки через телеграм звезды",
            payload=payload,
            currency="XTR",
            prices=prices
        )
        await state.clear()
    except ValueError:
        await message.answer(f"<b>❗Ошибка. Введите числовое значение</b>", parse_mode='html')

@dp.message(F.content_type == types.ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    payment = message.successful_payment
    amount = payment.total_amount

    play = random.randint(1,2)

    username = message.from_user.full_name
    username1 = message.from_user.username
    hrefka = f't.me/{username1}'
    user_id = message.from_user.id
    payment = message.successful_payment
    payload = payment.invoice_payload  


    if payload.startswith("star_bet_"):
        stars = int(payload.split("_")[2]) 
    else:
        stars = None  


    if payment.currency == "XTR":
        sent_msg = await message.answer(f"""<pre>💥 Ставка за звезды успешно принята!</pre>
<i>Игрок: <u><a href="{hrefka}">{username}</a></u>
Сумма: <u>{amount} звезд</u>
</i>""", parse_mode='html', disable_web_page_preview=True)

        sent_msg = await bot.send_message(
chat_id='@AsartiaCasino',
text = f"""<b><pre>✨ Ставка за звезды успешно принята!</pre></b>
<i>Игрок: <u><a href="{hrefka}">{username}</a></u></i>
<i>Сумма: <u>{amount} звезд</u></i>
""", 
parse_mode='html', 
disable_web_page_preview=True)
        await asyncio.sleep(0.5)
        await bot.send_dice(chat_id=message.chat.id, emoji="🎲")
        await bot.send_dice(chat_id='@AsartiaCasino', emoji="🎲")
        await asyncio.sleep(1)
        if play == 1:
            await bot.send_message(chat_id='@AsartiaCasino', text=f'<b>━━━━━━━━━━━━━━━━\n🏆 <a href="{hrefka}">{username}</a>, Вы выиграли!</b>\n<pre><i>Фортуна на твоей стороне, возвращайся за новым выигрышем. Подарок отправил тебе в личные сообщения</i></pre>\n\n<b><a href="t.me/AsartiaCasino">⚡ Канал с новостями</a> | <a href="https://t.me/AsartiaCasino/40"> Как сделать ставку</a></b>', parse_mode='html', disable_web_page_preview=True)
            await bot.send_message(chat_id=message.chat.id, text=f'<b>━━━━━━━━━━━━━━━━\n🏆 <a href="{hrefka}">{username}</a>, Вы выиграли!</b>\n<pre><i>Фортуна на твоей стороне, возвращайся за новым выигрышем.</i></pre>\n\n<b><a href="t.me/AsartiaCasino">⚡ Канал с новостями</a> | <a href="https://t.me/AsartiaCasino/40"> Как сделать ставку</a></b>', reply_to_message_id=sent_msg.message_id, parse_mode='html', disable_web_page_preview=True)
            if stars < 25:
                await bot(SendGift(
        gift_id=random.choice(['5170145012310081615', '5170233102089322756']),
        user_id=user_id,
        text="Поздравляю, ты выиграл! Спасибо за пользование ❤️"))
            elif stars < 50: 
                await bot(SendGift(
        gift_id=random.choice(['5168103777563050263', '5170250947678437525']),
        user_id=user_id,
        text="Поздравляю, ты выиграл! Спасибо за пользование ❤️"))
            else:
                await bot(SendGift(
        gift_id=random.choice(['5170144170496491616', '5170314324215857265', '5170564780938756245']),
        user_id=user_id,
        text="Поздравляю, ты выиграл! Спасибо за пользование ❤️"))

        else:
            await bot.send_message(chat_id=message.chat.id, text=f'━━━━━━━━━━━━━━━\n<b>💥 <a href="{hrefka}">{username}</a>, Вы проиграли!\n</b><pre><i>Желаем удачи в следующих играх, не опускайте руки!</i></pre>\n\n<b><a href="t.me/AsartiaCasino">⚡ Канал с новостями</a> | <a href="https://t.me/AsartiaCasino/40"> Как сделать ставку</a></b>', reply_to_message_id=sent_msg.message_id, parse_mode='html', disable_web_page_preview=True)

            await bot.send_message(chat_id='@AsartiaCasino', text=f'━━━━━━━━━━━━━━━\n<b>💥 <a href="{hrefka}">{username}</a>, Вы проиграли!\n</b><pre><i>Желаем удачи в следующих играх, не опускайте руки!</i></pre>\n\n<b><a href="t.me/AsartiaCasino">⚡ Канал с новостями</a> | <a href="https://t.me/AsartiaCasino/40"> Как сделать ставку</a></b>', parse_mode='html', disable_web_page_preview=True)
    else:
        pass







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
