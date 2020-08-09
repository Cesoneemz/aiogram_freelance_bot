import asyncio
import asyncpg

from config.config import POSTGRES_CONFIG


class DatabaseAPI(object):

    @classmethod
    async def connect_to_database(cls):
        self = DatabaseAPI()
        self.pool = await asyncpg.create_pool(**POSTGRES_CONFIG)
        return self

    def connect(func):
        async def decorator(self, *args, **kwargs):
            async with self.pool.acquire() as connect:
                async with connect.transaction():
                    return await func(self, connect=connect, *args, **kwargs)

        return decorator

    @connect
    async def create_all_tables(self, connect):
        await connect.execute('''
                            CREATE TABLE public.users(
                                id serial NOT NULL,
                                user_id integer NOT NULL,
                                username text NOT NULL,
                                max_request_per_day integer DEFAULT 5,
                                PRIMARY KEY(id))
                            '''
                              )

        await connect.execute('''
                            CREATE TABLE public.messages(
                                id serial NOT NULL,
                                message text NOT NULL,
                                PRIMARY KEY(id))
                            '''
                              )

        await connect.execute('''
                            CREATE TABLE public.info(
                                id integer NOT NULL,
                                link text NOT NULL,
                                param1 text NOT NULL,
                                param2 text NOT NULL,
                                param3 text NOT NULL,
                                param4 text NOT NULL,
                                PRIMARY KEY(id))
                            '''
                              )

        await connect.execute('INSERT INTO messages (message) VALUES ($1)', 'Пожалуйста, введите ID или ссылку')
        await connect.execute('INSERT INTO messages (message) VALUES ($1)', 'Полученная информация: ')
        await connect.execute('INSERT INTO messages (message) VALUES ($1)',
                              'Файл был успешно загружен в бота. Начинаю парсинг...')
        await connect.execute('INSERT INTO messages (message) VALUES ($1)', 'Все данные были загружены в базу данных.')
        await connect.execute('INSERT INTO messages (message) VALUES ($1)', 'Такой информации нет.')
        await connect.execute('INSERT INTO messages (message) VALUES ($1)', 'Ваш лимит запросов на сегодня исчерпан.')
        await connect.execute('INSERT INTO messages (message) VALUES ($1)', 'Присылаю админ панель.')
        await connect.execute('INSERT INTO messages (message) VALUES ($1)',
                              'Максимальное количество подключений в день успешно обновлено.')
        await connect.execute('INSERT INTO messages (message) VALUES ($1)',
                              'Введите количество максимальных продключений в день. Только число! По умолчанию: 5')
        await connect.execute('INSERT INTO messages (message) VALUES ($1)', 'Пожалуйста, пришлите csv-файл.')
        await connect.execute('INSERT INTO messages (message) VALUES ($1)',
                              'Пожалуйста, введите ID сообщения, которое вы хотите изменить.')
        await connect.execute('INSERT INTO messages (message) VALUES ($1)', 'Введите текст нового сообщения.')
        await connect.execute('INSERT INTO messages (message) VALUES ($1)',
                              'Что-то пошло не так, пожалуйста, попробуйте снова.')
        await connect.execute('INSERT INTO messages (message) VALUES ($1)', 'Сообщение успешно изменено.')
        await connect.execute('INSERT INTO messages (message) VALUES ($1)', 'Ссылка')
        await connect.execute('INSERT INTO messages (message) VALUES ($1)', 'Параметр 1')
        await connect.execute('INSERT INTO messages (message) VALUES ($1)', 'Параметр 2')
        await connect.execute('INSERT INTO messages (message) VALUES ($1)', 'Параметр 3')
        await connect.execute('INSERT INTO messages (message) VALUES ($1)', 'Параметр 4')

    @connect
    async def get_message(self, connect, id):
        return await connect.fetchval('SELECT message FROM messages WHERE id = $1', id)

    @connect
    async def get_user(self, connect, user_id):
        return await connect.fetchval('SELECT * FROM users WHERE user_id = $1', user_id)

    @connect
    async def get_user_by_username(self, connect, username):
        return await connect.fetchval('SELECT * FROM users WHERE username = $1', username)

    @connect
    async def add_user(self, connect, user_id, username, max_requests=5):
        return await connect.execute('''
                                    INSERT INTO users (user_id, username, max_request_per_day) VALUES ($1, $2, $3)
                                    ''',
                                     user_id, username, max_requests
                                     )

    @connect
    async def add_new_info(self, connect, *args):
        return await connect.execute('''
                                    INSERT INTO info (link, param1, param2, param3, param4) VALUES ($1, $2, $3, $4, $5)
                                    ''',
                                     *args)

    @connect
    async def get_info_from_db(self, connect, id='', link=''):
        try:
            if id == '':
                return await connect.fetchval("SELECT (link, param1, param2, param3, param4) FROM info WHERE link = $1",
                                              link)
            elif link == '':
                return await connect.fetchval("SELECT (link, param1, param2, param3, param4) FROM info WHERE id = $1", id)
        except:
            return None

    @connect
    async def set_max_request_per_day(self, connect, max):
        return await connect.execute('UPDATE users SET max_request_per_day = $1', max)

    @connect
    async def get_user_max_request(self, connect, user_id):
        return await connect.fetchval('SELECT max_request_per_day FROM users WHERE user_id = $1', user_id)

    @connect
    async def reduce_number_of_requests(self, connect, user_id):
        return await connect.execute(
            'UPDATE users SET max_request_per_day = max_request_per_day - 1 WHERE user_id = $1', user_id)

    @connect
    async def get_all_messages_with_id(self, connect):
        return await connect.fetch('SELECT * FROM messages')

    @connect
    async def set_new_message(self, connect, id, message):
        return await connect.execute('UPDATE messages SET message = $1 WHERE id = $2', message, id)

    @connect
    async def get_info_by_id(self, connect, id):
        return await connect.fetchval('SELECT * FROM info WHERE id = $1', id)

    @connect
    async def insert_new_info(self, connect, id, link, param1, param2, param3, param4):
        return await connect.execute(
            'INSERT INTO info (id, link, param1, param2, param3, param4) VALUES($1, $2, $3, $4, $5, $6)',
            id, link, param1, param2, param3, param4)

    @connect
    async def update_info(self, connect, id, link, param1, param2, param3, param4):
        return await connect.execute(
            'UPDATE info SET link = $1, param1 = $2, param2 = $3, param3 = $4, param4 = $5 WHERE id = $6',
            link, param1, param2, param3, param4, id)


    @connect
    async def set_max_requests_to_user(self, connect, username, count):
        try:
            return await connect.execute('UPDATE users SET max_request_per_day = $1 WHERE username = $2', count, username)
        except:
            return None


loop = asyncio.get_event_loop()
db = loop.run_until_complete(DatabaseAPI.connect_to_database())
