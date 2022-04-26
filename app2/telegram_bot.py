import random
import sqlite3

import emoji
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils import executor

import db_session
from main import load_user
from news import News
from users import User

TOKEN = '5330961932:AAE4raRPL_4YWvhoszimBDRL8dODuL6K6FE'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
game = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Камень 🗿")
        ],
        [
            KeyboardButton(text="Ножницы ✂"),
            KeyboardButton(text="Бумага 📃"),
        ],
        [
            KeyboardButton(text="Закончить игру..")
        ],
    ],
    resize_keyboard=True
)

game1 = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Да"),
            KeyboardButton(text="Нет"),
        ],
    ],
    resize_keyboard=True
)
game2 = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="/game"),
        ],
    ],
    resize_keyboard=True
)


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("help", "Помощь"),
        types.BotCommand("game", "Мини-игрушка"),
        types.BotCommand("add_id", "Мини-игрушка"),
        types.BotCommand("register", "Быстрая регистрация"),
        types.BotCommand("show_news", "Последние новости"),
    ])


class Game(StatesGroup):
    q1 = State()
    q2 = State()


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(f'Привет, {message.from_user.full_name}!')


@dp.message_handler(commands=['help'])
async def help(msg: types.Message):
    await bot.send_message(msg.from_user.id,
                           f'~~~~~~~~~~~~Здравствуй! Я бот сайта Requiem~~~~~~~~~~~~\n\n'
                           f'° - "/show_news" - посмотреть последние новости,\n'
                           f'° - "/add_news"- добавить новость (требуется авторизация) \n'
                           f'° - "/register" - регистрация в нашей соц-сети примиком из бота'
                           f'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')


@dp.message_handler(commands=['info'])
async def info(msg: types.Message):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name_in_telega == msg.from_user.id).first()
    if user:
        if user.img:
            photo = open(f'app2/static/img/{user.img}', 'rb')
        else:
            photo = open(f'app2/static/img/cat.jpg', 'rb')
        await bot.send_photo(msg.from_user.id, caption=f"ник-{user.name}\n"
                                                       f"id вашего телеграмм-{user.name_in_telega}\n", photo=photo)

    else:
        await bot.send_message(msg.from_user.id, f"Упс, кажется я вас не нашёл"
                                                 f"")


@dp.message_handler(commands=['add_id'])
async def add_id(msg: types.Message):
    try:
        text = msg.text[9:-1].split(']-[')
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.name == text[0]).first()
        if user:
            if user.check_password(text[1]):
                user.name_in_telega = msg.from_user.id
                db_sess.commit()
                await bot.send_message(msg.from_user.id, "Всё успешно добавлено")
            else:
                await bot.send_message(msg.from_user.id, "Неверный пароль")
        else:
            await bot.send_message(msg.from_user.id, "Такого имя пользователя не существует")
    except Exception:
        await bot.send_message(msg.from_user.id, "Неправильно введены данные")


@dp.message_handler(commands=['show_news'])
async def show_news(msg: types.Message):
    try:
        con = sqlite3.connect("app2/db/blogs.db", check_same_thread=False)
        cur = con.cursor()
        news = cur.execute(
            f"SELECT (SELECT name FROM users WHERE id = user_id), "
            f"created_date, title, content, img FROM news ORDER BY id DESC LIMIT 10").fetchall()
        con.close()
        for new in news:
            if not new[4]:
                await bot.send_message(msg.from_user.id, f"{emoji.emojize('🧸')}Автор записи - {new[0]}\n"
                                                         f"{emoji.emojize('📆')}Дата создания - {new[1]}\n"
                                                         f"Заголовок - {new[2]}\n"
                                                         f"Контекст - {new[3]}")
            else:
                photo = open(f'app2/static/img_news/{new[4]}', 'rb')
                await bot.send_photo(msg.from_user.id, caption=f"{emoji.emojize('✅')}{emoji.emojize('✅')}"
                                                               f"{emoji.emojize('✅')}{emoji.emojize('✅')}\n"
                                                               f"{emoji.emojize('🧸')}Автор записи - {new[0]}\n"
                                                               f"{emoji.emojize('📆')}Дата создания - {new[1]}\n"
                                                               f"Заголовок - {new[2]}\n"
                                                               f"Контекст - {new[3]}", photo=photo)
    except TypeError:
        await bot.send_message(msg.from_user.id, "Неверные данные")


@dp.message_handler(commands=['add_news'])
async def add_news(msg: types.Message):
    text = msg.text[11:-1].split(']-[')
    if not text:
        await bot.send_message(msg.from_user.id,
                               f"~~~~~~~~~~~~~~~~~~~~~~~-Requiem-~~~~~~~~~~~~~~~~~~~~~~~\n"
                               f"Введите пожалуйста данные в формате:\n"
                               f'"/add_news [Категория новости]-[Заголовок]-[Содержание]\n"'
                               f'Категории новостей:\n'
                               f'1 - Развлечение \n'
                               f'2 - Мир \n'
                               f'3 - Наши новости \n'
                               f'4 - Для Детей \n'
                               f'5 - Компьютерные технологии\n\n'
                               f'**Примечание: \n'
                               f'Логин и пароль используются от аккаунта соц-сети.\n'
                               f'Если вы еще не зарегистрированы - /register.\n'
                               f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    elif len(text) == 3:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.name_in_telega == msg.from_user.id).first()
        await bot.send_message(msg.from_user.id, user.name_in_telega)
        if user:
            try:
                load_user(user.id)
                news = News()
                news.title = text[1]
                news.category_id = text[0]
                news.content = text[2]
                news.is_private = False
                user.news.append(news)
                db_sess.merge(user)
                db_sess.commit()
                await bot.send_message(msg.from_user.id, "Вы успешно добавили новость! Если Хотите получить"
                                                         "больше возможностей, переходите к нам на сайт")
            except Exception:
                await bot.send_message(msg.from_user.id, "Введённые данные неверны")
        else:
            await bot.send_message(msg.from_user.id, "Введённые данные неверны")


@dp.message_handler(commands=['register'])
async def register(msg: types.Message):
    text = msg.text[11:-1].split(']-[')

    if not text:
        await bot.send_message(msg.from_user.id, f"~~~~~~~~~~~~~~~~~~~~~-Requiem-~~~~~~~~~~~~~~~~~~~~~\n"
                                                 f"Введите пожалуйста данные в формате:\n"
                                                 f'"/register [Ник]-[Пароль]-[Еще раз пароль]"'
                                                 f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    elif len(text) == 3 and text[1] == text[2]:
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.name == text[0]).first():
            await bot.send_message(msg.from_user.id, "Такой пользователь уже есть")
        else:
            user = User(
                name=text[0],
                name_in_telega=msg.from_user.id,
            )
            user.set_password(text[2])
            db_sess.add(user)
            db_sess.commit()
            await bot.send_message(msg.from_user.id, "Ваш аккаунт успешно зарегистрирован!")
    else:
        await bot.send_message(msg.from_user.id, "Пароли не верны")


@dp.message_handler(commands=["game"])
async def register(msg: types.Message):
    await bot.send_message(msg.from_user.id, "-.-.-.-.-.-.-.-.-ИГРА-.-.-.-.-.-.-.-.- \n"
                                             "Камень/ножницы\бумага \n \n"
                                             "Делайте свой выбор..", reply_markup=game)
    await Game.q1.set()


@dp.message_handler(state=Game.q1)
async def answer_q1(message: types.Message, state: FSMContext):
    answer = message.text
    bot = ""
    comp = str(random.randint(1, 3))  # 1 - Камень, 2 - Ножницы, 3 - Бумага
    if comp == "1":
        bot = "Камень 🗿"
    elif comp == "2":
        bot = "Ножницы ✂️"
    elif comp == "3":
        bot = "Бумагу 📃"
    if answer == "Закончить игру..":
        await message.answer("By, by.. Ждем тебя снова)", reply_markup=ReplyKeyboardRemove())
        await state.reset_state()
    elif answer == "Камень 🗿" and comp == "1":
        await message.answer(f"Пельмеш выбрал - {bot} \n \n"
                             "-=-=-=-=-=- Ничья! :/ -=-=-=-=-=- \n \n")
        await message.answer("Сыграем еще раз?", reply_markup=game1)
        await Game.next()

        @dp.message_handler(state=Game.q2)
        async def answer_q1(message: types.Message, state: FSMContext):
            if message.text == "Нет":
                await message.answer("By, by.. Ждем тебя снова)", reply_markup=ReplyKeyboardRemove())
                await state.reset_state()
            else:
                await state.reset_state()
                await message.answer("Окей", reply_markup=game2)
    elif answer == "Камень 🗿" and comp == "2":
        await message.answer(f"Пельмеш выбрал - {bot} \n \n"
                             "-=-=-=-=-=- Вы выиграли! :D -=-=-=-=-=-")
        await message.answer("Сыграем еще раз?", reply_markup=game1)
        await Game.next()

        @dp.message_handler(state=Game.q2)
        async def answer_q1(message: types.Message, state: FSMContext):
            if message.text == "Нет":
                await message.answer("By, by.. Ждем тебя снова)", reply_markup=ReplyKeyboardRemove())
                await state.reset_state()
            else:
                await state.reset_state()
                await message.answer("Окей", reply_markup=game2)
    elif answer == "Камень 🗿" and comp == "3":
        await message.answer(f"Пельмеш выбрал - {bot} \n \n"
                             "-=-=-=-=-=- Проигрыш :( -=-=-=-=-=-")
        await message.answer("Сыграем еще раз?", reply_markup=game1)
        await Game.next()

        @dp.message_handler(state=Game.q2)
        async def answer_q1(message: types.Message, state: FSMContext):
            if message.text == "Нет":
                await message.answer("By, by.. Ждем тебя снова)", reply_markup=ReplyKeyboardRemove())
                await state.reset_state()
            else:
                await state.reset_state()
                await message.answer("Окей", reply_markup=game2)
    elif answer == "Ножницы ✂" and comp == "1":
        await message.answer(f"Пельмеш выбрал - {bot} \n \n"
                             "-=-=-=-=-=- Проигрыш :( -=-=-=-=-=-")
        await message.answer("Сыграем еще раз?", reply_markup=game1)
        await Game.next()

        @dp.message_handler(state=Game.q2)
        async def answer_q1(message: types.Message, state: FSMContext):
            if message.text == "Нет":
                await message.answer("By, by.. Ждем тебя снова)", reply_markup=ReplyKeyboardRemove())
                await state.reset_state()
            else:
                await state.reset_state()
                await message.answer("Окей", reply_markup=game2)
    elif answer == "Ножницы ✂" and comp == "2":
        await message.answer(f"Пельмеш выбрал - {bot} \n \n"
                             "-=-=-=-=-=- Ничья! :/ -=-=-=-=-=- \n \n")
        await message.answer("Сыграем еще раз?", reply_markup=game1)
        await Game.next()

        @dp.message_handler(state=Game.q2)
        async def answer_q1(message: types.Message, state: FSMContext):
            if message.text == "Нет":
                await message.answer("By, by.. Ждем тебя снова)", reply_markup=ReplyKeyboardRemove())
                await state.reset_state()
            else:
                await state.reset_state()
                await message.answer("Окей", reply_markup=game2)
    elif answer == "Ножницы ✂" and comp == "3":
        await message.answer(f"Пельмеш выбрал - {bot} \n \n"
                             "-=-=-=-=-=- Вы выиграли! :D -=-=-=-=-=-")
        await message.answer("Сыграем еще раз?", reply_markup=game1)
        await Game.next()

        @dp.message_handler(state=Game.q2)
        async def answer_q1(message: types.Message, state: FSMContext):
            if message.text == "Нет":
                await message.answer("By, by.. Ждем тебя снова)", reply_markup=ReplyKeyboardRemove())
                await state.reset_state()
            else:
                await state.reset_state()
                await message.answer("Окей", reply_markup=game2)
    elif answer == "Бумага 📃" and comp == "1":
        await message.answer(f"Пельмеш выбрал - {bot} \n \n"
                             "-=-=-=-=-=- Вы выиграли! :D -=-=-=-=-=-")
        await message.answer("Сыграем еще раз?", reply_markup=game1)
        await Game.next()

        @dp.message_handler(state=Game.q2)
        async def answer_q1(message: types.Message, state: FSMContext):
            if message.text == "Нет":
                await message.answer("By, by.. Ждем тебя снова)", reply_markup=ReplyKeyboardRemove())
                await state.reset_state()
            else:
                await state.reset_state()
                await message.answer("Окей", reply_markup=game2)
    elif answer == "Бумага 📃" and comp == "2":
        await message.answer(f"Пельмеш выбрал - {bot} \n \n"
                             "-=-=-=-=-=- Проигрыш :( -=-=-=-=-=-")
        await message.answer("Сыграем еще раз?", reply_markup=game1)
        await Game.next()

        @dp.message_handler(state=Game.q2)
        async def answer_q1(message: types.Message, state: FSMContext):
            if message.text == "Нет":
                await message.answer("By, by.. Ждем тебя снова)", reply_markup=ReplyKeyboardRemove())
                await state.reset_state()
            else:
                await state.reset_state()
                await message.answer("Окей", reply_markup=game2)
    elif answer == "Бумага 📃" and comp == "3":
        await message.answer(f"Пельмеш выбрал - {bot} \n \n"
                             "-=-=-=-=-=- Ничья! :/ -=-=-=-=-=- \n \n")
        await message.answer("Сыграем еще раз?", reply_markup=game1)
        await Game.next()

        @dp.message_handler(state=Game.q2)
        async def answer_q1(message: types.Message, state: FSMContext):
            if message.text == "Нет":
                await message.answer("By, by.. Ждем тебя снова)", reply_markup=ReplyKeyboardRemove())
                await state.reset_state()
            else:
                await state.reset_state()
                await message.answer("Окей", reply_markup=game2)
    else:
        await message.answer("Жду правильного ответа!!")


@dp.message_handler(content_types=['text'])
async def main(msg: types.Message):
    await bot.send_message(msg.from_user.id, "Скорее всего вы имели в виду, что-то другое\n"
                                             "Чтобы посмотреть все функции напишите команду /help")


if __name__ == '__main__':
    db_session.global_init("app2/db/blogs.db")

    executor.start_polling(dp)
