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
import sys
import asyncio
from contextlib import suppress
import logging
import sys
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



API_TOKEN = ("7701528122:AAG3Z0mR5naC3NMr-K1WNAboOE3ENW6M39U")
SEND_API_KEY = ("364087:AAllpmezSsFgoxEGZLXmxyYbG5zusS4Ptjb")
CHANNEL_USERNAME = '@AsartiaCasino'



bot = Bot(token=API_TOKEN)
dp = Dispatcher()
send_client = CryptoPay(token=SEND_API_KEY)




class BetStates(StatesGroup):
    crypto_bet = State()
    star_bet = State()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    username = message.from_user.full_name
    username1 = message.from_user.username
    hrefka = f't.me/{username1}'
    user_id = message.from_user.id

    chat_member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)

    kb = InlineKeyboardBuilder()
    kb.button(text="Сделать ставку", callback_data="make_bet")
    kb.button(text="Профиль", callback_data="profile")
    kb.adjust(2)  

    if chat_member.status not in ['member', 'administrator', 'creator']:
            channel = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎰 Перейти в канал", url=f"t.me/AsartiaCasino")]
            ])
            await message.answer(
                "<b>❗ Вы не подписаны на канал. Пожалуйста, подпишитесь, чтобы продолжить. Когда подпишитесь, снова напишите /start</b>",
                reply_markup=channel, parse_mode='html'
            )
    else:

        await message.answer(
        f'<b>💎 <a href="{hrefka}">{username}</a>, добро пожаловать в бота "Asartia Casino"\n\n<pre>Ставь легко, выигрывай быстро, твой шанс сорвать куш уже здесь!</pre></b>',
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
    kb.button(text="Сделать ставку", callback_data="make_bet") 

    await callback.message.answer(
        f'<i>😋 Ваш профиль:</i>\n<b>Ник: <u>{username}</u>\nАйди: <u>{callback.message.from_user.id}</u></b>\n\n<a href="{href}">❤️ Все новости о канале</a>',
        reply_markup=kb.as_markup(),
        parse_mode='html',
        disable_web_page_preview=True
    )


@dp.callback_query(F.data == "make_bet")
async def choose_bet_type(callback: types.CallbackQuery):
    await callback.message.delete()

    kb = InlineKeyboardBuilder()
    kb.button(text="💸 Ставка по крипто боту", callback_data="crypto_bet")
    kb.button(text="💫 Ставка за звезды", callback_data="star_bet")
    kb.adjust(2)  

    await callback.message.answer(
        "<i>😋 Выберите опцию ниже:</i>",
        reply_markup=kb.as_markup(),
        parse_mode='html'
    )

@dp.callback_query(F.data == "crypto_bet")
async def crypto_bet(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        "<i>💵 Введи сумму ставки в цыфрах:</i>\n<b>Минимальная сумма ставки — <u>0.1 $</u></b>",
        parse_mode='html'
    )
    await state.set_state(BetStates.crypto_bet)


async def check_payment(invoice_url: str, message: Message):
    user = message.from_user
    username = user.full_name
    username1 = user.username or user.id
    hrefka = f't.me/{username1}'
    playy = random.randint(1,3)

    try:
        while True:
            invoices = await send_client.get_invoices()
            for invoice in invoices:
                if invoice.bot_invoice_url == invoice_url and invoice.status == "paid":
                    mmm = invoice.amount  
                    win = mmm * 1.5
                    sent_msg = await message.answer(f"""<b><pre>✨ Ставка по криптоботу успешно принята!</pre></b>
<i>Игрок: <u><a href="{hrefka}">{username}</a></u>
Сумма: <u>{invoice.amount} $</u></i>""", parse_mode='html', disable_web_page_preview=True)

                    await bot.send_message(
    chat_id='@AsartiaCasino',
    text=f"""<b><pre>✨ Ставка по криптоботу успешно принята!</pre></b>
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
                        check = await send_client.create_check(
            asset="USDT",
            amount=win,
            telegram_user_id=user.id, 
            description=f"Чек для {username}"
                    )
                        await bot.send_message(chat_id=message.chat.id, text=f'<i>😄 <a href="{hrefka}">{username}</a>, вы выиграли <u>{win} $</u>, удачи в следующих играх!\n👉 <a href="{check.bot_check_url}">Нажмите сюда, чтобы активировать <u>приз</a></u></i>', reply_to_message_id=sent_msg.message_id, parse_mode='html', disable_web_page_preview=True)

                        await bot.send_message(
    chat_id='@AsartiaCasino',
    text=f'<i>😄 <a href="{hrefka}">{username}</a>, вы выиграли <u>{win} $</u>, удачи в следующих играх!\n👉 <a href="{check.bot_check_url}">Нажмите сюда, чтобы активировать <u>приз</a></u></i>',
    parse_mode='html',
    disable_web_page_preview=True
)

                    else:
                        await bot.send_message(chat_id=message.chat.id, text=f'<i>😕 <a href="{hrefka}">{username}</a>, вы проиграли. Желаем удачи в следующих играх, не опускайте руки!\n\n<a href="t.me/AsartiaCasino">❤️ Все новости о канале</a></i>', reply_to_message_id=sent_msg.message_id, parse_mode='html', disable_web_page_preview=True)

                        await bot.send_message(chat_id='@AsartiaCasino', 
                        text=f'<i>😕 <a href="{hrefka}">{username}</a>, вы проиграли. Желаем удачи в следующих играх, не опускайте руки!\n\n<a href="t.me/AsartiaCasino">❤️ Все новости о канале</a></i>', 
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
        elif amount > 0.7:
            await message.answer("<b>❗Максимальная сумма ставки — <u>0.7 $</u></b>", parse_mode='html')
            return
        invoice = await send_client.create_invoice(
            amount=amount,
            asset="USDT",
            description="Ставка по криптоботу",
            payload=str(message.from_user.id),
            allow_anonymous=False
        )

        invoice_url = invoice.bot_invoice_url  

        kb = InlineKeyboardBuilder()
        kb.button(text="Оплатить ставку", url=invoice_url)
        kb.adjust(1) 

        await message.answer(f"<i>💰 Оплатите счет ставки на сумму <u>{amount} $</u></i>", reply_markup=kb.as_markup(), parse_mode='html')

        asyncio.create_task(check_payment(invoice_url, message))

        await state.clear()
    except ValueError:
        await message.answer("<b>❗Введите корректную сумму</b>", parse_mode='html')



@dp.callback_query(F.data == "star_bet")
async def star_bet(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer("<i>✨ Введи сумму ставки в цыфрах:</i>\n<b>Минимальная сумма ставки — <u>20 звезд</u></b>", parse_mode='html')
    await state.set_state(BetStates.star_bet)


@dp.pre_checkout_query(lambda query: True)
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message(BetStates.star_bet)
async def handle_star_bet(message: Message, state: FSMContext):
    try:
        stars = int(message.text)
        if stars < 20:
            await message.answer("<b>❗Минимальная сумма ставки — <u>20 звезд</u></b>", parse_mode='html')
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

    play = random.randint(1,4)

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
        sent_msg = await message.answer(f"""<b><pre>✨ Ставка за звезды успешно принята!</pre></b>
<i>Игрок: <u><a href="{hrefka}">{username}</a></u>
Сумма: <u>{amount} звезд</u>
</i>""", parse_mode='html', disable_web_page_preview=True)

        sent_msg = await bot.send_message(
chat_id='@AsartiaCasino',
text = f"""<b><pre>✨ Ставка за звезды успешно принята!</pre></b>
<i>Игрок: <u><a href="{hrefka}">{username}</a></u>
Сумма: <u>{amount} звезд</u>
</i>""", 
parse_mode='html', 
disable_web_page_preview=True)
        await asyncio.sleep(0.5)
        await bot.send_dice(chat_id=message.chat.id, emoji="🎲")
        await bot.send_dice(chat_id='@AsartiaCasino', emoji="🎲")
        await asyncio.sleep(1)
        if play == 1:
            await bot.send_message(chat_id='@AsartiaCasino', text=f'<b>🏆 Победа! <a href="{hrefka}">{username}</a>, Вы выиграли уникальный приз. </b>\n<i>Фортуна на твоей стороне, возвращайся за новым выигрышем!</i>', parse_mode='html', disable_web_page_preview=True)
            await bot.send_message(chat_id=message.chat.id, text=f'<b>🏆 Победа! <a href="{hrefka}">{username}</a>, Вы выиграли уникальный приз. </b>\n<i>Фортуна на твоей стороне, возвращайся за новым выигрышем!</i>', reply_to_message_id=sent_msg.message_id, parse_mode='html', disable_web_page_preview=True)
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
            await bot.send_message(chat_id=message.chat.id, text=f'<b>❌ Проигрыш! <a href="{hrefka}">{username}</a>, Вы проиграли\n </b><i>Желаем удачи в следующих играх, не опускайте руки!<a href="t.me/AsartiaCasino">❤️ Все новости о канале</a></i>', reply_to_message_id=sent_msg.message_id, parse_mode='html', disable_web_page_preview=True)

            await bot.send_message(chat_id='@AsartiaCasino', text=f'<b>❌ Проигрыш! <a href="{hrefka}">{username}</a>, Вы проиграли\n </b><i>Желаем удачи в следующих играх, не опускайте руки!<a href="t.me/AsartiaCasino">❤️ Все новости о канале</a></i>', parse_mode='html', disable_web_page_preview=True)
    else:
        pass






async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot) 


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main()) 
