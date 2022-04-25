import sqlite3
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import emoji
import db_session
from main import load_user
from users import User
from news import News

TOKEN = '5330961932:AAE4raRPL_4YWvhoszimBDRL8dODuL6K6FE'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['help'])
async def help(msg: types.Message):
    await bot.send_message(msg.from_user.id,
                           f'Здравствуй! Я бот сайта "-Requiem-"\n\n'
                           f'{emoji.emojize("🟧")} Чтобы посмотреть последние новости 10 новостей,'
                           f'введите команду "/show_news"\n\n'
                           f'{emoji.emojize("🟪")}Чтобы Добавить новость, введите "/add_news", но для этого нужно быть '
                           f'зарегистрированным.\n'
                           f'Введите всё по примеру, подставляя свои данные: "/add_news '
                           f'[email]&&[password]&&[номер категории(смотрите нижи)]&&[title_news]&&[content]"'
                           f'Категории:\n'
                           f'1-Развлечение 2-Мир 3-Наши новости 4-Для Детей 5-Компьютерные технологии\n\n'
                           f'{emoji.emojize("🟦")}Если вы в первый раз и хотите зарегистрироваться, введите команду '
                           f'"/register" \nВведите всё по примеру, подставляя свои данные: '
                           f'"/register [our name]&&[our email]&&[password]'
                           f'&&[answer our password]"')


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
    if len(text) == 5:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == text[0]).first()
        await bot.send_message(msg.from_user.id, text)
        if user and user.check_password(text[1]):
            try:
                load_user(user.id)
                news = News()
                news.title = text[3]
                news.category_id = text[2]
                news.content = text[4]
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
    else:
        await bot.send_message(msg.from_user.id, "Не соблюдены правила написания")


@dp.message_handler(commands=['register'])
async def register(msg: types.Message):
    text = msg.text[11:-1].split(']&&[')
    con = sqlite3.connect("app2/db/blogs.db", check_same_thread=False)
    if text[2] == text[3]:
        if '@' in text[1] and '&' not in text[1]:
            db_sess = db_session.create_session()

            if db_sess.query(User).filter(User.email == text[2]).first():
                await bot.send_message(msg.from_user.id, "Такой пользователь уже есть")
            else:
                user = User(
                    name=text[0],
                    email=text[1],
                )
                user.set_password(text[2])
                db_sess.add(user)
                db_sess.commit()
                await bot.send_message(msg.from_user.id, "Ваш аккаунт успешно зарегистрирован!")
        else:
            await bot.send_message(msg.from_user.id, "В логине нет '@' или есть '&'")
    else:
        await bot.send_message(msg.from_user.id, "Пароли не верны")


@dp.message_handler(content_types=['text'])
async def main(msg: types.Message):
    await bot.send_message(msg.from_user.id, "Скорее всего вы имели в виду, что-то другое\n"
                                             "Чтобы посмотреть все функции напишите команду /help")


if __name__ == '__main__':
    db_session.global_init("app2/db/blogs.db")
    executor.start_polling(dp)
