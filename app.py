import asyncio
import aioredis

from aiogram import executor

from config.config import ADMIN_ID, REDIS_CONFIG
from load_all import bot
from utils.database_api.database_main import db


async def zero_out_requests():
    while True:
        await asyncio.sleep(86400)
        redis = await aioredis.create_redis_pool(**REDIS_CONFIG)
        max = await redis.get('max_request_per_day')
        await db.set_max_request_per_day(max=int(max))
        redis.close()
        await redis.wait_closed()

        users_ids = await db.get_all_user_ids()
        for id in users_ids:
            try:
                await bot.send_message(chat_id=id['user_id'], text="Количество запросов было обновлено! Вы снова "
                                                                   "можете пользоваться ботом.")

                await asyncio.sleep(0.3)
            except Exception:
                pass


async def on_startup(dp):
    for id in ADMIN_ID:
        await bot.send_message(id, 'Bot has been started')
    redis = await aioredis.create_redis_pool(**REDIS_CONFIG)
    if await redis.get('max_request_per_day') is None:
        await redis.set('max_request_per_day', 5)
    if await redis.get('rows_limit') is None:
        await redis.set('rows_limit', 50)
    try:
        await db.create_all_tables()
    except:
        pass


async def on_shutdown(dp):
    await bot.close()


if __name__ == '__main__':
    from handlers.handlers import dp

    loop = asyncio.get_event_loop()

    loop.create_task(zero_out_requests())
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, loop=loop)
