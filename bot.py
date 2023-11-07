import asyncio
import logging
import json
import datetime
import requests
from bs4 import BeautifulSoup
import time
import re

from config import token, user_id
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hbold, hunderline, hcode, hlink, text
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from parser import check_news_update
from prsnSrc import counted_news, get_searched_news



#logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
# Диспетчер
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Form(StatesGroup):
    name = State()
    colvo = State()


# Хэндлер на команду /start
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    start_buttons = ["Все новости", "Последние 5 новостей", "Свежие новости", "Поиск статей"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer(
        "Hello!\nBelow you can find a list of available commands and a description of the functionality to work with me!")
    await message.answer("Лента новостей", reply_markup=keyboard)


@dp.message_handler(Text(equals="Поиск статей"))
async def news_search(message: types.Message):
    await Form.name.set()
    await message.answer("Привет! Чем ты интересуешься?")

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):

    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)

    await state.finish()

    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())
    await cmd_start()

@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['name'] = message.text

    if counted_news(message.text.strip().replace(' ', '%20')) == 0:
        await message.answer("Статей не найдено")
        await cancel_handler(Text('cancel'),)
    else:
        await message.answer(f'Найдено статей: {counted_news(message.text.strip().replace(" ", "%20"))}')

    await Form.next()
    await message.answer("Сколько статаей вы хотите увидеть?")


@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.colvo)
async def process_colvo_invalid(message: types.Message):
    """
    If age is invalid
    """
    return await message.reply("Количество должно быть числовым.\nСколько статей? (Только цифры)")

@dp.message_handler(lambda message: message.text.isdigit(), state=Form.colvo)
async def process_colvo(message: types.Message, state: FSMContext):
    # Update state and data
    await Form.next()
    await state.update_data(colvo=int(message.text))
    async with state.proxy() as data:
        for k, v in sorted(get_searched_news(counted_news(data['name'].strip().replace(' ', '%20')),data['colvo']).items()):
            news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
                   f"{hlink(v['article_title'], v['article_url'])}"

            await message.answer(news)
    await message.reply("What is your gender? - Helicopter? - Ha!")
    await state.finish()


@dp.message_handler(commands=["I_love_you"])
async def cmd_start(message: types.Message):
    await message.answer("<b>I love you too!</b>")


@dp.message_handler(Text(equals="Все новости"))
async def get_all_news(message: types.Message):
    with open('kotaku_news_async.json', encoding="UTF-8") as file:
        news_dict = json.load(file)

        for k, v in sorted(news_dict.items()):
            # разный тип вывода
            '''news=f"<em>{v['date']}</em>\n" \
                 f"<b>{v['author']}</b>\n" \
                 f"<h2>{v['title']}</h2>\n" \
                 f"{v['description']}\n" \
                 f"{v['href']}\n"'''

            news = f"{hbold(v['date'])}\n" \
                   f"{hlink(v['title'], v['href'])}"
            await message.answer(news)
        await message.answer("Did <b>u need something</b> else?")

@dp.message_handler(Text(equals="Последние 5 новостей"))
async def get_last_five_news(message: types.Message):
    with open('kotaku_news_async.json', encoding="UTF-8") as file:
        news_dict = json.load(file)

    for k, v in sorted(news_dict.items())[-5:]:
        news = f"{hbold(v['date'])}\n" \
               f"{hlink(v['title'], v['href'])}"

        await message.answer(news)


@dp.message_handler(Text(equals="Свежие новости"))
async def get_fresh_news(message: types.Message):
    fresh_news = check_news_update()
    if type(fresh_news)=='NoneType':
        print("Пока нет свежих новостей...")
    else:
        if len(fresh_news) >= 1:
            for k, v in sorted(fresh_news.items()):
                news = f"{hbold(v['date'])}\n" \
                       f"{hlink(v['title'], v['href'])}"

                await message.answer(news)

        else:
            await message.answer("Пока нет свежих новостей...")

async def news_every_minute():

    while True:
        fresh_news = check_news_update()

        if len(fresh_news) >= 1:
            for k, v in sorted(fresh_news.items()):
                news = f"{hbold(v['date'])}\n" \
                       f"{hlink(v['title'], v['href'])}"

                await bot.send_message(user_id, news, disable_notification=True)

        else:
            await bot.send_message(user_id, "Пока нет свежих новостей...", disable_notification=True)
        print("[INFO] News was updated")
        await asyncio.sleep(360)


@dp.message_handler(Text(equals="Свежие новости"))
async def get_fresh_news(message: types.Message):
    fresh_news = check_news_update()
    if type(fresh_news)=='NoneType':
        print("Пока нет свежих новостей...")
    else:
        if len(fresh_news) >= 1:
            for k, v in sorted(fresh_news.items()):
                news = f"{hbold(v['date'])}\n" \
                       f"{hlink(v['title'], v['href'])}"

                await message.answer(news)
        else:
            await message.answer("Пока нет свежих новостей...")

# id пользователя
@dp.message_handler(content_types="text")
async def newsTopics(message: types.Message):
    if message.text == "Люблю тебя!":
        await message.answer("Я тоже вас люблю")
        if message.text == "Хочу свой ID" or message.text == "хочу свой id":
            keyboard_markup = types.InlineKeyboardMarkup()
        user_id_btn = types.InlineKeyboardButton('Получить ID пользывателя из Inline кнопки', callback_data='user_id')
        keyboard_markup.row(user_id_btn)
        await message.answer(f"Ваш ID: {message.from_user.id}", reply_markup=keyboard_markup)
    if message.text == "Привет":
        await message.answer(
            'Hello!\nBelow you can find a list of available commands and a description of the functionality to work with me!"')
    print(message.text)


@dp.callback_query_handler(text='user_id')
async def user_id_inline_callback(callback_query: types.CallbackQuery):
    await callback_query.answer(f"Ваш ID: {callback_query.from_user.id}", True)


# Запуск процесса пуллинга новых апдейтов
async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    await dp.start_polling(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(news_every_minute())
    executor.start_polling(dp)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    loop = asyncio.get_event_loop()
    loop.create_task(news_every_minute())
    executor.start_polling(dp)
    asyncio.run(main())
