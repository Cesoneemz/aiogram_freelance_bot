import aioredis

from aiogram import types
from aiogram.dispatcher import FSMContext

from load_all import dp
from config.config import REDIS_CONFIG
from utils.database_api.database_main import db

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

    if int(await db.get_user_max_request(user_id=message.from_user.id)) <= 0:
        await message.answer(await db.get_message(id=6))
        await db.reduce_number_of_requests(user_id=message.from_user.id)
        return

    welcome_message = await db.get_message(id=1)

    await message.answer(welcome_message)

    await IdOrURl.wait_for_id_or_url.set()


@dp.message_handler(state=IdOrURl.wait_for_id_or_url)
async def get_info(message: types.Message, state: FSMContext):
    if message.text.startswith(('http', 'https')):
        info = await db.get_info_from_db(link=message.text)
    else:
        info = await db.get_info_from_db(id=int(message.text))

    if info is None:
        await message.answer(await db.get_message(id=5))
        await state.finish()
        return

    msg = f'Ссылка: <a>{info[0]}</a>\n\nПараметры: {info[1]}, {info[2]}, {info[3]}'

    await state.finish()

    await db.reduce_number_of_requests(user_id=message.from_user.id)

    await message.answer(msg, parse_mode='HTML')
