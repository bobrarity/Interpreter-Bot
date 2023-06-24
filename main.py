from aiogram import Dispatcher, executor, Bot
from aiogram.types import Message, ReplyKeyboardRemove

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from configs import *
import os
from dotenv import load_dotenv
from keyboards import generate_languages
import sqlite3
from googletrans import Translator

load_dotenv()

TOKEN = os.getenv('TOKEN')

storage = MemoryStorage()
bot = Bot(token=TOKEN)

dp = Dispatcher(bot, storage=storage)


class Questions(StatesGroup):
    src = State()
    dest = State()
    text = State()


@dp.message_handler(commands=['start', 'help', 'about', 'history'])
async def command_start(message: Message):
    if message.text == '/start':
        await message.answer('Hello, welcome to the bot translator')
        await start_questions(message)
    elif message.text == '/help':
        await message.answer('If you have any problems or suggestions, write here: @bobrarity')
    elif message.text == '/about':
        await message.answer('This bot was created to translate the text you need from one language to another')
    elif message.text == '/history':
        await get_history(message)


async def get_history(message: Message):
    chat_id = message.chat.id

    database = sqlite3.connect('bot.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT src, dest, original_text, translated_text FROM history
    WHERE telegram_id = ?;
    ''', (chat_id, ))
    history = cursor.fetchall()
    history = history[::-1]
    for src, dest, original_text, translated_text in history[:10]:
        await bot.send_message(chat_id, f'''You have translated:
From: {src}
To: {dest}
Your text: {original_text}
Translation: {translated_text}''')



async def start_questions(message: Message):
    await Questions.src.set()
    await message.answer('What language would you like to translate from? ', reply_markup=generate_languages())


@dp.message_handler(content_types=['text'], state=Questions.src)
async def confirm_src_ask_dest(message: Message, state: FSMContext):
    if message.text in ['/start', '/help', '/about', '/history']:
        await state.finish()
        await command_start(message)
    else:
        async with state.proxy() as data:
            data['src'] = message.text


        await Questions.next()
        await message.answer(f'You have chosen {message.text}\nSelect which language to translate into',
                             reply_markup=generate_languages())


@dp.message_handler(content_types=['text'], state=Questions.dest)
async def confirm_dest_ask_text(message: Message, state: FSMContext):
    if message.text in ['/start', '/help', '/about', '/history']:
        await state.finish()
        await command_start(message)
    else:
        async with state.proxy() as data:
            data['dest'] = message.text

        await Questions.next()
        await message.answer('Type in the text you want to translate', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(content_types=['text'], state=Questions.text)
async def confirm_text_translate(message: Message, state: FSMContext):
    if message.text in ['/start', '/help', '/about', '/history']:
        await state.finish()
        await command_start(message)

    else:
        async with state.proxy() as data:
            data['text'] = message.text
        src = data['src']
        dest = data['dest']
        text = data['text']
        translator = Translator()
        trans_text = translator.translate(text=text, src=get_key(src), dest=get_key(dest)).text
        database = sqlite3.connect('bot.db')
        cursor = database.cursor()
        chat_id = message.chat.id

        cursor.execute('''
        INSERT INTO history(telegram_id, src, dest, original_text, translated_text)
        VALUES (?,?,?,?,?)
    
        ''', (chat_id, src, dest, text, trans_text))
        database.commit()
        database.close()


        await state.finish()
        await message.answer(trans_text)
        await start_questions(message)


executor.start_polling(dp)