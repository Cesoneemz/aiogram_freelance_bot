import aioredis

from aiogram import types
from aiogram.dispatcher import FSMContext

from load_all import dp, bot
from config.config import REDIS_CONFIG
from utils.database_api.database_main import db
from utils.user_keyboard import kbUserMain

from states.state import IdOrURl


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    if await db.get_user(user_id=message.from_user.id) is None:
        redis = await aioredis.create_redis_pool(**REDIS_CONFIG)
        max = await redis.get('max_request_per_day')
        await db.add_user(user_id=message.from_user.id, username=message.from_user.username,
                          max_requests=int(max))
        redis.close()
        await redis.wait_closed()

    await message.answer(await db.get_message(id=22), parse_mode='HTML', reply_markup=kbUserMain)


@dp.message_handler(lambda msg: msg.text == 'Отправить запрос')
async def send_request(message: types.Message):

    if int(await db.get_user_max_request(user_id=message.from_user.id)) <= 0:
        await message.answer(await db.get_message(id=6), parse_mode='HTML', reply_markup=kbUserMain)
        await db.reduce_number_of_requests(user_id=message.from_user.id)
        return


    import os
    from openpyxl import Workbook

    wb = Workbook()
    sheet = wb.active
    sheet.title = 'info'

    fio = await db.get_message(id=16)
    phone = await db.get_message(id=17)
    city = await db.get_message(id=18)

    row = 1
    sheet['A' + str(row)] = fio
    sheet['B' + str(row)] = phone
    sheet['C' + str(row)] = city

    redis = await aioredis.create_redis_pool(**REDIS_CONFIG)
    limit = await redis.get('rows_limit')

    info = await db.send_random_rows(limit=int(limit))

    redis.close()
    await redis.wait_closed()

    for item in info:
        row += 1
        sheet['A' + str(row)] = item[0][0]
        sheet['B' + str(row)] = item[0][1]
        sheet['C' + str(row)] = item[0][2]

    filename = f'data-{message.from_user.id}.xlsx'
    wb.save(filename=filename)

    with open(filename, 'rb') as f:
        await bot.send_document(chat_id=message.from_user.id, document=f)
        os.remove(filename)


@dp.message_handler(lambda msg: msg.text == 'Наши услуги')
async def send_our_services(message: types.Message):
    await message.answer(await db.get_message(id=20))


@dp.message_handler(lambda msg: msg.text == 'О боте')
async def send_our_services(message: types.Message):
    await message.answer(await db.get_message(id=21))
