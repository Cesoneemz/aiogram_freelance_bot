import logging
from config.config import API_TOKEN

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)

storage = MemoryStorage()

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
