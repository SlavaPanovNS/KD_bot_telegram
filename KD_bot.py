from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

import tokenKD
import time

import sqlite3
from sqlite3 import Error

import random
from datetime import date

# Сегодняшняя дата
today = date.today()

# SQL запросы
# Создание соединения
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print('Connection to SQLite DB successful.')
    except Error as e:
        print(f'The error "{e}" occured.')

    return connection

# Внесение изменений
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print('Query executed succesfully.')
    except Error as e:
        print(f'The error "{e}" occured.')

# Внесение значений с "?"
def cursor_insert(connection, query, val):
    cursor = connection.cursor()
    try:
        cursor.execute(query, val)
        connection.commit()
        print('Query executed succesfully.')
    except Error as e:
        print(f'The error "{e}" occured.')

# Извлечение из таблицы
def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f'The error "{e}" occured.')


connection =  create_connection('D:\SQL\db\kd.db')

create_chats_table = """
CREATE TABLE IF NOT EXISTS chats (
    chat_id INTEGER PRIMARY KEY,
    date DATE);
"""
create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    chat_id INTEGER,
    user_id INTEGER,
    username TEXT NOT NULL,
    score INTEGER NOT NULL);
"""
select_users_for_stat = 'SELECT username, score FROM users'
select_chats = 'SELECT chat_id FROM chats'

insert_chats = """
INSERT or IGNORE INTO chats 
(chat_id, date) VALUES (?,?);
"""
insert_users = """
INSERT or IGNORE INTO users 
(chat_id, user_id, username, score) VALUES (?,?,?,?);
"""

# Создание таблиц
execute_query(connection, create_chats_table)
execute_query(connection, create_users_table)

#users = execute_read_query(connection, select_users_for_stat)

# Строка для вывода статистики
#statkd = ''
#for i in users:
#    statkd += f'@{i[0]} : {i[1]}\n'


bot = Bot(token=tokenKD.tok)
dp = Dispatcher(bot)

# --------------------------------------------------Команды ------------------------------------------------------
@dp.message_handler(commands=['start'])
async def start_command(message : types.Message):
    username = message.from_user.username
    await message.answer('Привет! @' + username + ', теперь необходимо добавить меня в группу, в которой мы будем проводить игру.')

@dp.message_handler(commands=['help'])
async def start_command(message : types.Message):
    username = message.from_user.username
    await message.answer('Игра "Красавчик Дня". Каждый день наш бот по вашей команде будет определять\
красавчика дня в вашей группе.\n/join - чтобы вступить в игру\n/end - чтобы покинуть\n\
/run - чтобы начать\n/stat - узнать статистику побед\n/soup - узнать супчик дня.')

@dp.message_handler(commands=['run'])
async def run_command(message : types.Message):
    await message.answer('Бесплатная лотерея запущена.')
    time.sleep(1)
    await message.answer('Слушаем что шепчут улицы.')
    time.sleep(1)
    await message.answer('Гадаем на картах Таро')
    time.sleep(1)
    await message.answer('Подсматриваем в лунный календарь.')
    time.sleep(1)
    await message.answer('Ты не поверишь!')
    time.sleep(1)
    await message.answer('Похоже, что...')
    time.sleep(1)
    await message.answer('Красавчик дня: ')

@dp.message_handler(commands=['join'])
async def join_command(message : types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username
    for_users = (chat_id, user_id, username, 0)
    for_chats = (chat_id, today)
    all_chats = execute_read_query(connection, select_chats)
    chats = [x[0] for x in all_chats]

    if chat_id in chats:
        cursor = connection.cursor()
        cursor.execute(f'SELECT username FROM users WHERE chat_id = {chat_id}')
        all_users = cursor.fetchall()
        game = [x[0] for x in all_users]

        if username in game:
            await message.answer('@' + username + ' ты уже в игре')
        else:
            cursor_insert(connection, insert_users, for_users)
            await message.answer('Теперь ты в игре')
    else:
        cursor_insert(connection, insert_chats, for_chats)
        cursor_insert(connection, insert_users, for_users)
        await message.answer('Теперь ты в игре')

@dp.message_handler(commands=['stat'])
async def join_command(message : types.Message):
    await message.answer('пук')



executor.start_polling(dp, skip_updates=True)