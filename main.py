import asyncio
import logging
import sys
import time
import random
import string

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.client.session.aiohttp import AiohttpSession

import config

import google.generativeai as genai
genai.configure(api_key=config.GOOGLE_API_KEY)

session = AiohttpSession("http://proxy.server:3128")

dp = Dispatcher()
current_word = ''
current_hint = ''
start_time = 0
guessed_letters = set()
model = genai.GenerativeModel('gemini-pro')

async def start_new_game(message: types.Message):
    global current_word, current_hint, start_time, guessed_letters, game_active
    current_word = ''
    current_hint = ''
    start_time = 0
    guessed_letters = set()
    game_active = False
    await send_welcome(message)

game_active = False

@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    global current_word, current_hint, start_time, game_active
    game_active = True
    while True:
        response = model.generate_content("придумай слово на українській мові яке буде обозначати якийсь предмет і яке не буде мати нічого до росії і білорусі і буде мати 8 букв. напиши тільки слово і все")
        current_word = response.text.upper()
        break
    print(current_word)
    current_hint = '■ ' * len(current_word)
    start_time = time.time()
    await message.reply("Нова гра!\nВводьте по одній літері або відгадайте все слово цілком.\nЧас гри: 5 хвилин.\n\n" + current_hint)

@dp.message()
async def guess_letter_or_word(message: types.Message):
    global current_word, current_hint, start_time, guessed_letters, game_active
    if not game_active:
        pass
        return
    if time.time() - start_time > 300:
        await message.reply(f"На жаль гра була закінчена! Слово було: <b>{current_word}</b>\nВведіть /start щоб почати нову гру!")
        await start_new_game(message)
    else:
        guess = message.text.upper()
        if len(guess) == 1:
            if guess in guessed_letters:
                await message.reply(f"Буква <b>{message.text.upper()}</b> вже була названа.")
            elif guess in current_word:
                guessed_letters.add(guess)
                new_masked = list(current_hint)
                for i, letter in enumerate(current_word):
                    if guess == letter and new_masked[i*2] == "■":
                        new_masked[i*2] = letter
                current_hint = "".join(new_masked)
                if current_hint.replace(" ", "") == current_word:
                    await message.reply(f"Буква <b>{message.text.upper()}</b> є в слові!\nСлово було повністю розгадано!\n\n<b>{current_hint}</b>")
                    game_active = False
                else:
                    await message.reply(f"Буква <b>{message.text.upper()}</b> є в слові!\n\n{current_hint}")
            else:
                await message.reply(f"Буква <b>{message.text.upper()}</b> відсутня в слові.")
        elif guess == current_word:
            current_hint = current_word
            await message.reply(f"Вітаю {message.from_user.first_name}! Ви відгадали слово: <b>{current_word}</b>")
            game_active = False
        else:
            pass

async def main() -> None:
    bot = Bot(config.BOT_TOKEN, parse_mode=ParseMode.HTML, session=session)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
