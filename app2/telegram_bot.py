import sqlite3
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import emoji
from flask_login import login_user
import db_session
import main
from news import News

TOKEN = '5330961932:AAE4raRPL_4YWvhoszimBDRL8dODuL6K6FE'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['help'])
async def help(msg: types.Message):
    await bot.send_message(msg.from_user.id,
                           f'Здравствуй! Я бот сайта "-Requiem-"\n\n'
                           f'{emoji.emojize("🟧")} Чтобы посмотреть последние новости,'
                           f'введите команду "/show_news [кол-во новостей]"\n\n'
                           f'{emoji.emojize("🟪")}Чтобы Добавить новость, введите "/add_news", но для этого нужно быть '
                           f'зарегистрированным.\n'
                           f'Введите всё по примеру, подставляя свои данные: "/add_news [email]&&[password]&&[title_news]&&'
                           f'[content]"\n\n'
                           f'{emoji.emojize("🟦")}Если вы в первый раз и хотите зарегистрироваться, введите команду '
                           f'"/register" \nВведите всё по примеру, подставляя свои данные: "/register [our name]&&[our email]&&[password]'
                           f'&&[answer our password]"')


@dp.message_handler(commands=['show_news'])
async def show_news(msg: types.Message):
    try:
        n = int(msg.text[11:])
        con = sqlite3.connect("app2/db/blogs.db", check_same_thread=False)
        cur = con.cursor()
        news = cur.execute(
            f"SELECT (SELECT name FROM users WHERE id = user_id), "
            f"created_date, title, content, img FROM news ORDER BY id DESC LIMIT {n}").fetchall()
        con.close()
        for new in news:
            await bot.send_message(msg.from_user.id, f"{emoji.emojize('✅')}{emoji.emojize('✅')}"
                                                     f"{emoji.emojize('✅')}{emoji.emojize('✅')}\n"
                                                     f"{emoji.emojize('🧸')}Автор записи - {new[0]}\n"
                                                     f"{emoji.emojize('📆')}Дата создания - {new[1]}\n"
                                                     f"Заголовок - {new[2]}\n"
                                                     f"Контекст - {new[3]}")
            if new[4]:
                photo = open(f'app2/static/img/{new[4]}', 'rb')
                await bot.send_photo(msg.from_user.id, photo)
    except TypeError:
        await bot.send_message(msg.from_user.id, "Неверные данные")


@dp.message_handler(commands=['add_news'])
async def add_news(msg: types.Message):
    text = msg.text[11:-1].split(']&&[')
    if len(text) == 4:
        db_sess = db_session.create_session()
        from app2.users import User
        user = db_sess.query(User).filter(User.email == text[0]).first()
        if user and user.check_password(text[0]):
            main.load_user(user.id)
            news = News()
            news.title = text[2]
            news.content = text[3]
            news.is_private = False
            user.news.append(news)
            db_sess.merge(user)
            db_sess.commit()


@dp.message_handler(commands=['register'])
async def register(msg: types.Message):
    n = int(msg.text[11:])
    con = sqlite3.connect("app2/db/blogs.db", check_same_thread=False)
    cur = con.cursor()
    news = cur.execute(
        f"SELECT (SELECT name FROM users WHERE id = user_id), "
        f"created_date, title, content, img FROM news ORDER BY id DESC LIMIT {n}").fetchall()
    con.close()


@dp.message_handler(content_types=['text'])
async def main(msg: types.Message):
    await bot.send_message(msg.from_user.id, "Скорее всего вы имели в виду, что-то другое")


if __name__ == '__main__':
    executor.start_polling(dp)
