# Для использования асинхронных запросов к базе данных mssql вы можете использовать библиотеку `aiomssql`.
# Вот пример кода для переписывания запросов к базе данных на асинхронные с использованием `aiomssql`:

import aiocron
import aiomssql
from aiogram import Bot, Dispatcher, executor, types

bot = Bot(token='6129816762:AAHmIP75MdM9aM-M1LD1ckIx6UGIHKmzkik')
dp = Dispatcher(bot)

WATER_PRICE = 43


class Database:
    def __init__(self, server, database, username, password):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.pool = None

    async def connect(self):
        self.pool = await aiomssql.create_pool(
            server=self.server,
            database=self.database,
            user=self.username,
            password=self.password
        )

    async def register_user(self, user_id, first_name, last_name):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("INSERT INTO users (user_id, first_name, last_name) VALUES (?, ?, ?)", user_id,
                                     first_name, last_name)
                await conn.commit()

    async def register_device(self, user_id, device_name):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("INSERT INTO devices (user_id, device_name) VALUES (?, ?)", user_id, device_name)
                await conn.commit()

    async def add_reading(self, user_id, reading):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("INSERT INTO readings (user_id, reading) VALUES (?, ?)", user_id, reading)
                await conn.commit()

    async def calculate_payment(self, user_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT SUM(reading) FROM readings WHERE user_id = ?", user_id)
                total_readings = (await cursor.fetchone())[0]
        payment = total_readings * WATER_PRICE
        return payment

    async def get_users(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT user_id FROM users")
                users = await cursor.fetchall()
        return users


db = Database(server='DESKTOP-LHB569H\SQLEXPRESS', database='Test_Bot',TRUSTED_CONNECTION='yes')


async def on_startup(dp):
    dp.loop.create_task(create_db_pool())


async def create_db_pool():
    await db.connect()


@aiocron.crontab('0 12 25 * *')
async def send_notifications():
    users = await db.get_users()
    for user in users:
        user_id = user[0]
        await bot.send_message(user_id, "Не забудьте внести показатели счетчиков.")


@dp.message_handler(commands=['start'])
async def start_cmd_handler(message: types.Message):
    await message.answer("Привет! Спасибо за подписку на нашего бота.")


@dp.message_handler(commands=['register'])
async def register_cmd_handler(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    await db.register_user(user_id=user_id, first_name=first_name, last_name=last_name)
    await message.answer(f"Вы зарегистрированы как {first_name} {last_name}.")


@dp.message_handler(commands=['register_device'])
async def register_device_cmd_handler(message: types.Message):
    user_id = message.from_user.id
    device_name = message.text.split()[1]
    await db.register_device(user_id=user_id, device_name=device_name)
    await message.answer(f"Прибор учета {device_name} зарегистрирован.")


@dp.message_handler(commands=['add_reading'])
async def add_reading_cmd_handler(message: types.Message):
    user_id = message.from_user.id
    reading = message.text.split()[1]
    await db.add_reading(user_id=user_id, reading=reading)
    await bot.send_message(user_id, f"Вы добавили показатель счетчика: {reading}")
    await message.answer("Показатель счетчика добавлен.")


@dp.message_handler(commands=['calculate_payment'])
async def calculate_payment_cmd_handler(message: types.Message):
    user_id = message.from_user.id
    payment = await db.calculate_payment(user_id=user_id)
    await message.answer(f"Ваша оплата: {payment} рублей.")


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)

# В этом примере используется библиотека `aiomssql` для создания пула соединений с базой данных и
# выполнения асинхронных запросов. Обратите внимание на использование ключевого слова `await`
# перед вызовами методов `execute`, `fetchone` и `commit` для выполнения асинхронных операций.
#
# Не забудьте заменить `YOUR_BOT_TOKEN_HERE`, `YOUR_SERVER_NAME`, `YOUR_DATABASE_NAME`, `YOUR_USERNAME` и
# `YOUR_PASSWORD` на соответствующие значения для подключения к вашему боту и базе данных mssql.
