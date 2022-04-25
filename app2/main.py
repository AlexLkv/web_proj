import os
from io import BytesIO
from os import abort
import requests
from PIL import Image
from bs4 import BeautifulSoup
from flask import Flask, redirect, render_template, request, jsonify, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import db_session
import news_users_api
from forms.news import NewsForm
from news import News
from users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


def latest_news(channel_name):
    telegram_url = 'https://t.me/s/'
    url = telegram_url + channel_name
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    link = soup.find_all("a")
    url = link[-1]['href']
    url = url.replace('https://t.me/', '')
    channel_name, news_id = url.split('/')
    urls = []
    for i in range(10):
        urls.append(f'{channel_name}/{int(news_id) - i}')
    return urls


def main():
    db_session.global_init("db/blogs.db")
    app.register_blueprint(news_users_api.blueprint)
    app.run()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/", methods=['GET', 'POST'])
def index1():
    db_sess = db_session.create_session()
    if request.method == 'POST':
        f = request.files['f']
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.img = str(current_user.id) + '.' + str(f.filename.split('.')[-1])
        db_sess.commit()
        image = Image.open(BytesIO(f.read()))
        image.save(f'static/img/{user.img}')

    if current_user.is_authenticated:
        news = db_sess.query(News).filter((News.user == current_user) | (News.is_private != True)) \
            .order_by(News.id.desc()).all()
    else:
        news = db_sess.query(News).filter(News.is_private != True).order_by(News.id.desc()).all()
    return render_template("index.html", news=news, lenta='lenta')


@app.route("/news_local", methods=['GET', 'POST'])
def news_local():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != True)
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news)


@app.route("/categorys/<int:id_category>", methods=['GET', 'POST'])
def categorys(id_category):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.category_id == id_category)
    return render_template('index.html', news=news, lenta="lenta")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    if request.method == 'POST':
        if request.form.get('username') and request.form.get('email') \
                and request.form.get('pass1') and request.form.get('pass2'):
            if request.form.get('pass1') != request.form.get('pass2'):
                return render_template('register.html',
                                       message="Пароли не совпадают")
            if '@' not in request.form.get('email') or '&' in request.form.get('email'):
                return render_template('register.html',
                                       message="В логине нет '@' или есть '&'")
            db_sess = db_session.create_session()

            if db_sess.query(User).filter(User.email == request.form.get('email')).first():
                return render_template('register.html',
                                       message="Такой пользователь уже есть")
            user = User(
                name=request.form.get('username'),
                email=request.form.get('email'),
                img=''
            )
            user.set_password(request.form.get('pass1'))
            db_sess.add(user)
            db_sess.commit()
            return redirect('/login')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('email') and request.form.get('pass'):
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == request.form.get('email')).first()

            if user and user.check_password(request.form.get('pass')):
                login_user(user)
                return redirect("/")
            return render_template('login.html',
                                   message="Неправильный логин или пароль")
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        news.category_id = request.form.get('association')
        if request.files['f']:
            f = request.files['f']
            news.img = str(news.id) + '.' + str(f.filename.split('.')[-1])
            image = Image.open(BytesIO(f.read()))
            image.save(f'static/img_news/{news.img}')
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route("/it-tech-tg", methods=["GET"])
def news_page4():
    urls = []
    channel_name = 'habr_com'
    urls = latest_news(channel_name)
    return render_template('news_telega.html', urls=urls)


@app.route("/about-us-tg", methods=["GET"])
def news_page3():
    urls = []
    channel_name = 'requiem_site'
    urls = latest_news(channel_name)
    return render_template('news_telega.html', urls=urls)


@app.route("/world-tg", methods=["GET"])
def news_page2():
    urls = []
    channel_name = 'rian_ru'
    urls = latest_news(channel_name)
    return render_template('news_telega.html', urls=urls)


@app.route("/memes-tg", methods=["GET"])
def news_page1():
    channel_name = 'inoshapotyan'
    urls = latest_news(channel_name)
    return render_template('news_telega.html', urls=urls)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.img = news.img
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.category_id = request.form.get('association')
            news.is_private = form.is_private.data
            if request.files['f']:
                f = request.files['f']
                news.img = str(news.id) + '.' + str(f.filename.split('.')[-1])
                image = Image.open(BytesIO(f.read()))
                image.save(f'static/img_news/{news.img}')
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        if news.img:
            os.remove(f'static/img_news/{news.img}')
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route("/home_page/<int:id>", methods=["GET", "POST"])
@login_required
def home_page(id):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(
            News.user_id == id)
        your_count = news.count()
    return render_template('index.html', news=news, lenta="home_page", img=current_user.img, your_count=your_count, user_id=id)


@app.route("/home_page/<int:id>/<int:id_category>", methods=["GET", "POST"])
@login_required
def home_page_funny(id, id_category):
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(
            News.user_id == id, News.category_id == id_category)
        your_count = news.count()
    return render_template('index.html', news=news, lenta="home_page", your_count=your_count, user_id=id)


if __name__ == '__main__':
    main()
