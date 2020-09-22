import aioredis
import asyncio

from aiogram import types
from aiogram.types.chat import ChatActions
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from load_all import bot, dp
from config.config import ADMIN_ID, POSTGRES_CONFIG, REDIS_CONFIG
from states.state import SetMaxRequestPerDay, LoadCsv, EditSystemMessages, AddAdmin, DeleteAdmin, \
    SetNewCountRequestToUser, Mailing, ClearDatabase
from utils.database_api.database_main import db
from utils.admin_keyboard import keyboard as kb


@dp.message_handler(lambda message: str(message.from_user.id) in ADMIN_ID, commands=['admin'])
async def send_admin_keyboard(message: types.Message):
    await message.answer(await db.get_message(id=7), reply_markup=kb.kbAdminStart)


@dp.message_handler(lambda message: str(message.from_user.id) in ADMIN_ID and message.text == 'Установить макс. '
                                                                                              'количество запросов в '
                                                                                              'день')
async def test(message: types.Message):
    await message.answer(await db.get_message(id=9))

    await SetMaxRequestPerDay.wait_for_request_int.set()


@dp.message_handler(lambda message: str(message.from_user.id) in ADMIN_ID,
                    state=SetMaxRequestPerDay.wait_for_request_int)
async def test2(message: types.Message, state: FSMContext):
    redis = await aioredis.create_redis_pool(**REDIS_CONFIG)
    await redis.set('max_request_per_day', int(message.text))
    redis.close()
    await redis.wait_closed()
    await message.answer(await db.get_message(id=8))
    await state.finish()


@dp.message_handler(lambda message: str(message.from_user.id) in ADMIN_ID and message.text == 'Загрузить CSV-файл')
async def wait_for_csv(message: types.Message):
    await message.answer(await db.get_message(id=10))

    markup = InlineKeyboardMarkup()

    import os
    for filename in os.listdir('./csv'):
        if filename.endswith('.csv'):
            markup.add(InlineKeyboardButton(text=filename, callback_data=filename))

    await message.answer("В папке с таблицами были найдены следующие файлы. Выберите тот, который хотите загрузить в "
                         "базу данных. Для загрузки файла в папку перейдите по адресу: <a>http://185.119.59.193</a>",
                         parse_mode='HTML', reply_markup=markup)

    await LoadCsv.wait_for_csv.set()


@dp.callback_query_handler(lambda call: str(call.from_user.id) in ADMIN_ID, state=LoadCsv.wait_for_csv)
async def download_and_insert_csv(call: types.CallbackQuery, state: FSMContext):
    import os
    import csv
    import psycopg2

    filename = call.data

    await call.answer(await db.get_message(id=3))

    connect = psycopg2.connect(**POSTGRES_CONFIG)
    connect.autocommit = True
    cursor = connect.cursor()

    with open(os.path.join(os.getcwd(), 'csv', filename), 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 1:
                split_row = row[0].split(';')
            else:
                split_row = row
            if await db.get_info_by_id(id=int(split_row[0])) is None:
                try:
                    await db.insert_new_info(id=int(split_row[0]), link=split_row[1], param1=split_row[2],
                                             param2=split_row[3], param3=split_row[4], param4=split_row[5])
                except Exception as e:
                    await call.answer(str(e))
            else:
                try:
                    await db.update_info(id=int(split_row[0]), link=split_row[1], param1=split_row[2],
                                         param2=split_row[3], param3=split_row[4], param4=split_row[5])
                except Exception as e:
                    await call.answer(str(e))

    connect.commit()

    os.remove(os.path.join(os.getcwd(), 'csv', filename))

    await state.finish()

    await call.answer(await db.get_message(id=4))


@dp.message_handler(
    lambda message: str(message.from_user.id) in ADMIN_ID and message.text == 'Прислать csv-файл с пользователями')
async def send_csv_with_users(message: types.Message):
    import os
    import psycopg2

    filename = 'users.csv'
    path = os.path.join(os.getcwd(), 'csv', filename)
    connect = psycopg2.connect(**POSTGRES_CONFIG)
    connect.autocommit = True
    cursor = connect.cursor()

    with open(path, 'w') as f:
        sqlstr = "COPY public.users TO STDOUT DELIMITER ',' CSV ENCODING 'UTF-8'"
        cursor.copy_expert(sql=sqlstr, file=f)
    with open(path, 'rb') as f:
        await bot.send_chat_action(message.from_user.id, ChatActions.UPLOAD_DOCUMENT)
        await asyncio.sleep(1)
        await bot.send_document(chat_id=message.from_user.id, document=f)


@dp.message_handler(
    lambda message: str(message.from_user.id) in ADMIN_ID and message.text == 'Редактировать текстовые сообщения')
async def edit_system_messages_id(message: types.Message):
    messages = await db.get_all_messages_with_id()
    msg = ''
    for i in messages:
        msg += f'ID: {i[0]}   Сообщение: {i[1]}\n\n'
    await message.answer(msg)
    await message.answer(await db.get_message(id=11))
    await EditSystemMessages.wait_for_id.set()


@dp.message_handler(lambda message: str(message.from_user.id) in ADMIN_ID, state=EditSystemMessages.wait_for_id)
async def edit_system_message(message: types.Message, state: FSMContext):
    await state.update_data(id=int(message.text))
    await message.answer(await db.get_message(id=12))

    await EditSystemMessages.wait_fot_new_message.set()


@dp.message_handler(lambda message: str(message.from_user.id) in ADMIN_ID,
                    state=EditSystemMessages.wait_fot_new_message)
async def set_new_system_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    id = data.get('id')

    try:
        await db.set_new_message(id=id, message=message.text)

        await message.answer(await db.get_message(id=14))

        await state.finish()

    except:

        await message.answer(await db.get_message(id=13))
        await state.finish()


@dp.message_handler(lambda message: str(message.from_user.id) in ADMIN_ID and message.text == "Добавить админа")
async def add_admin_part_1(message: types.Message):
    await message.answer("Пожалуйста, введите ID нового админа")

    await AddAdmin.wait_for_admin_id.set()


@dp.message_handler(lambda message: str(message.from_user.id) in ADMIN_ID, state=AddAdmin.wait_for_admin_id)
async def add_admin_part2(message: types.Message, state: FSMContext):
    ADMIN_ID.append(message.text)
    await message.answer(f"ID {message.text} был добавлен к списку админов")

    await state.finish()


@dp.message_handler(lambda message: str(message.from_user.id) in ADMIN_ID and message.text == "Удалить админа")
async def add_admin_part_1(message: types.Message):
    await message.answer("Пожалуйста, введите ID админа, которого нужно удалить")

    await DeleteAdmin.wait_for_admin_id_delete.set()


@dp.message_handler(lambda message: str(message.from_user.id) in ADMIN_ID, state=DeleteAdmin.wait_for_admin_id_delete)
async def add_admin_part2(message: types.Message, state: FSMContext):
    if message.text in ADMIN_ID:
        ADMIN_ID.remove(message.text)
        await message.answer(f"Админ с ID {message.text} был удалён")
    else:
        await message.answer('Такого админа нет')

    await state.finish()


@dp.message_handler(lambda message: str(message.from_user.id) in ADMIN_ID and message.text == "Установить количество "
                                                                                              "подключений для юзера")
async def set_max_requests_to_user_part1(message: types.Message):
    await message.answer('Пожалуйста, введите username пользователя')

    await SetNewCountRequestToUser.wait_for_username.set()


@dp.message_handler(lambda message: str(message.from_user.id) in ADMIN_ID,
                    state=SetNewCountRequestToUser.wait_for_username)
async def set_max_requests_to_user_part2(message: types.Message, state: FSMContext):
    if not await db.get_user_by_username(username=message.text) is None:
        await state.update_data(username=message.text)
        await message.answer('Введите количество подключений для пользователя')

        await SetNewCountRequestToUser.wait_for_count.set()

    else:
        await message.answer('Такого пользователя не существует.')

        await state.finish()


@dp.message_handler(lambda message: str(message.from_user.id) in ADMIN_ID,
                    state=SetNewCountRequestToUser.wait_for_count)
async def set_max_requests_to_user_part3(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.get('username')

    try:
        await db.set_max_requests_to_user(username=username, count=int(message.text))
        await message.answer(f"Количество запросов пользователя {username} установлено на {message.text}")
        await state.finish()
    except:
        await message.answer("Неверное значение для количества подключений")
        await state.finish()


@dp.message_handler(lambda message: str(message.from_user.id) in ADMIN_ID and message.text == "Сделать рассылку")
async def mailing(message: types.Message):
    await message.answer("Пришлите текст рассылки")

    await Mailing.wait_for_text.set()


@dp.message_handler(lambda message: str(message.from_user.id) in ADMIN_ID, state=Mailing.wait_for_text)
async def send_mailing(message: types.Message, state: FSMContext):
    users_ids = await db.get_all_user_ids()
    for id in users_ids:
        try:
            await bot.send_message(chat_id=id['user_id'], text=message.text)

            await asyncio.sleep(0.3)
        except Exception:
            pass

    await state.finish()


@dp.message_handler(lambda message: str(message.from_user.id) in ADMIN_ID and message.text == "Очистить базу данных")
async def clear_info_database_yesno(message: types.Message):
    markup = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [InlineKeyboardButton(text="Да", callback_data="yes")],
            [InlineKeyboardButton(text="Нет", callback_data="no")],
        ]
    )
    await message.answer("Вы точно хотите очистить базу с информацией?", reply_markup=markup)

    await ClearDatabase.yesno_prompt.set()


@dp.callback_query_handler(lambda call: str(call.from_user.id) in ADMIN_ID, state=ClearDatabase.yesno_prompt)
async def clear_info_database(call: types.CallbackQuery, state: FSMContext):
    if call.data == "no":
        await state.finish()

        await bot.send_message(chat_id=call.from_user.id, text="Отменено.")

    else:

        await db.clear_database()
        await bot.send_message(chat_id=call.from_user.id, text="База данных была полностью очищена.")

        await state.finish()


@dp.message_handler(lambda message: str(message.from_user.id) in ADMIN_ID and message.text == "Получить список файлов")
async def get_full_list_dir(message: types.Message):
    import os
    for filename in os.listdir('./csv'):
        if filename.endswith('.csv'):
            await message.answer(filename)
#    await message.answer(str(os.listdir('./csv')))