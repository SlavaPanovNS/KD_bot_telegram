from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup

import tokenKD
import time

import sqlite3
from sqlite3 import Error

import random
from datetime import date, timedelta

storage = MemoryStorage()

# Сегодняшняя дата
def get_today():
    today = date.today()
    return today

# Список супов
soup_list = ['Борщик', 'Свежие Щи', 'Гороховый', 'Уха', 'Кислые Щи', 'Рассольник', 'Суп с Галушками',
             'Харчо', 'Томатный', 'Суп с фрикадельками','Куриный с лапшой', 'Диетический', 'Грибной',
             'Шурпа', 'Молочный', 'Щавелевый', 'Фо Бо', 'Гороховый',
             'Тыквенный', 'Сегодня без супа дня. Просто дошика покушаем']

# Функция создание соединения к БД
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print('Connection to SQLite DB successful.')
    except Error as e:
        print(f'The error "{e}" occured.')

    return connection

# Функция внесение изменений
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print('Query executed succesfully.')
    except Error as e:
        print(f'The error "{e}" occured.')

# Функция внесение изменений с "?"
def cursor_insert(connection, query, val):
    cursor = connection.cursor()
    try:
        cursor.execute(query, val)
        connection.commit()
        print('Query executed succesfully.')
    except Error as e:
        print(f'The error "{e}" occured.')

# Функция извлечения из таблицы
def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f'The error "{e}" occured.')

create_chats_table = """
CREATE TABLE IF NOT EXISTS chats (
    chat_id INTEGER PRIMARY KEY,
    date DATE,
    winner TEXT);
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

def select_user_id(chat_id):
    return f'SELECT user_id FROM users WHERE chat_id = {chat_id}'

# Функция проверки чатов на наличие в БД
def check_chats(chat_id):
    all_chats = execute_read_query(connection, select_chats)
    chats = [x[0] for x in all_chats]
    if chat_id in chats:
        return True
    return False

# Функция проверки юзеров на наличие в БД
def check_user_id(chat_id, user_id):
    selected_user_ids = select_user_id(chat_id)
    all_users = execute_read_query(connection, selected_user_ids)
    game = [x[0] for x in all_users]
    if user_id in game:
        return True
    return False

# Функция проверки необходимой даты
def check_date(chat_id):
    today = get_today()
    cursor = connection.cursor()
    cursor.execute(f'SELECT date FROM chats WHERE chat_id = {chat_id}')
    game_date = cursor.fetchall()
    if game_date[0][0] != str(today):
        return True
    return False

# Функция выбора победителя
def get_winner(chat_id):
    cursor = connection.cursor()
    cursor.execute(f'SELECT username FROM users WHERE chat_id = {chat_id}')
    all_users = cursor.fetchall()
    game = [x[0] for x in all_users]
    winner = random.choice(game)
    return str(winner)

# Функция получения статистики
def get_stat(chat_id):
    cursor = connection.cursor()
    cursor.execute(f'SELECT username, score FROM users WHERE chat_id = {chat_id} ORDER BY score DESC')
    all_stats = cursor.fetchall()
    statkd = '🏆Статистика побед:\n'
    index = 1
    for i in all_stats:
        statkd += f'{index}.{i[0]} : {i[1]}\n'
        index += 1
    return statkd

# Функция удаления пользователя
def delete_user(chat_id, user_id):
    cursor = connection.cursor()
    cursor.execute(f"DELETE FROM users WHERE chat_id = {chat_id} AND user_id = '{user_id}'")
    connection.commit()

# Функция обновления score и date
def update_score_and_date(chat_id, winner):
    today = get_today()
    cursor = connection.cursor()
    cursor.execute(f"UPDATE users SET score = score+1 WHERE chat_id = {chat_id} AND username = '{winner}'")
    connection.commit()
    cursor.execute(f"UPDATE chats SET date = '{today}' WHERE chat_id = {chat_id}")
    connection.commit()
    cursor.execute(f"UPDATE chats SET winner = '{winner}' WHERE chat_id = {chat_id}")
    connection.commit()

# Функция смены имени
def change_name(user_id, new_name):
    cursor = connection.cursor()
    cursor.execute(f"UPDATE users SET username = '{new_name}' WHERE user_id = '{user_id}'")
    connection.commit()

# Функция проверки победителя
def get_today_winner(chat_id):
    cursor = connection.cursor()
    cursor.execute(f'SELECT winner FROM chats WHERE chat_id = {chat_id}')
    winner = cursor.fetchall()
    return winner[0][0]

# Создание соединения
connection =  create_connection('D:\SQL\db\kd.db')

# Создание таблиц
execute_query(connection, create_chats_table)
execute_query(connection, create_users_table)

# Создание Бота и Диспетчера
bot = Bot(token=tokenKD.tok)
dp = Dispatcher(bot, storage=storage)

class Form(StatesGroup):
    name = State()

# --------------------------------------------------Команды ------------------------------------------------------
@dp.message_handler(commands=['start'])
async def start_command(message : types.Message):
    username = message.from_user.username
    if username == None:
        await message.reply('Привет! Теперь необходимо добавить меня в группу, в которой мы будем проводить игру.')
    else:
        await message.answer('Привет! @' + username + ', теперь необходимо добавить меня в группу, в которой мы будем проводить игру.')

@dp.message_handler(commands=['help'])
async def start_command(message : types.Message):
    await message.answer('Игра "Красавчик Дня". Каждый день наш бот по вашей команде будет определять\
красавчика дня в вашей группе.\n/join - чтобы вступить в игру\n/end - чтобы покинуть\n\
/run - чтобы начать\n/stat - узнать статистику побед\n/soup - узнать супчик дня.')

@dp.message_handler(commands=['soup'])
async def start_command(message : types.Message):
    await message.answer('Готовимся к готовке 🧅🧄🥕🥔🔪')
    time.sleep(1)
    await message.answer('Проверяем холодильник.')
    time.sleep(1)
    await message.answer('Супчик дня:...')
    time.sleep(1)
    await message.answer(random.choice(soup_list))

@dp.message_handler(commands=['run'])
async def run_command(message : types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if check_chats(chat_id):
        if check_user_id(chat_id, user_id):
            if check_date(chat_id):
                await message.answer('Бесплатная лотерея запущена.')
                time.sleep(1)
                await message.answer('Слушаем что шепчут улицы.')
                time.sleep(1)
                await message.answer('Гадаем на картах Таро.')
                time.sleep(1)
                await message.answer('Подсматриваем в лунный календарь.')
                time.sleep(1)
                await message.answer('Ты не поверишь!')
                time.sleep(1)
                await message.answer('Похоже, что...')
                time.sleep(1)
                await message.answer('🌝')
                time.sleep(1)
                winner = get_winner(chat_id)
                await message.answer('🏆 Красавчик дня: ' + winner)
                update_score_and_date(chat_id, winner)
            else:
                today_winner = get_today_winner(chat_id)
                await message.answer(f'Игра уже была сегодня!\nВыиграл {today_winner}\nНажми /stat , чтобы узнать статистику.')
        else:
            await message.reply('сначала нажми /join')
    else:
        await message.reply('сначала нажми /join')
    

@dp.message_handler(commands=['join'])
async def join_command(message : types.Message):
    today = get_today()
    yesterday = today - timedelta(days=1)
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username
    if username == None:
        await message.reply(f'Похоже, что у тебя не заполнена графа:\nИмя Пользователя\nв настройках Telegram. Пока что твоё имя в турнирной таблице будет твоим номером \
id: {user_id}. Чтобы изменить своё имя для этой игры нажми /name .')
        username = user_id
    else:
        username = '@' + message.from_user.username
    for_users = (chat_id, user_id, username, 0)
    for_chats = (chat_id, yesterday)
    if check_chats(chat_id):
        if check_user_id(chat_id, user_id):
            await message.answer(username + ' ты уже в игре')
        else:
            cursor_insert(connection, insert_users, for_users)
            await message.reply('Теперь ты в игре')
    else:
        cursor_insert(connection, insert_chats, for_chats)
        cursor_insert(connection, insert_users, for_users)
        await message.reply('Теперь ты в игре')

@dp.message_handler(commands=['stat'])
async def join_command(message : types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if check_chats(chat_id):
        if check_user_id(chat_id, user_id):
            statkd = get_stat(chat_id)            
            await message.answer(statkd)
        else:
            await message.reply('Сначала нажми /join')
    else:
        await message.reply('Сначала нажми /join')

@dp.message_handler(commands=['name'])
async def run_command(message : types.Message):
    await Form.name.set()
    await message.reply('Напиши своё новое имя:')

@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    new_name = message.text
    change_name(user_id, new_name)
    await message.reply('Теперь тебя зовут ' + new_name)


@dp.message_handler(commands=['end'])
async def join_command(message : types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if check_chats(chat_id):
        if check_user_id(chat_id, user_id):
            delete_user(chat_id, user_id)
            await message.reply('Ты покинул игру')
        else:
            await message.reply('Сначала надо вступить в игру.')
    else:
        await message.reply('Сначала надо вступить в игру.')


executor.start_polling(dp, skip_updates=True)