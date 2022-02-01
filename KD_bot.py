from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

import tokenKD

bot = Bot(token=tokenKD.tok)
dp = Dispatcher(bot)

@dp.message_handler(commands=['run'])
async def run_command(message : types.Message):
    await message.answer('Пошла игра.')

@dp.message_handler()
async def echo_send(message : types.Message):
    await message.answer(message.text)


executor.start_polling(dp, skip_updates=True)