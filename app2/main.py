import datetime
import os
import random
from io import BytesIO
from os import abort
import database
import jyserver.Flask as jsf
from PIL import Image
from flask import Flask, redirect, render_template, request, jsonify, make_response, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_mysqldb import MySQL, MySQLdb
from app2.hospital import Hospital
from app2.veterinarian import Veterinarian
from forms.news import NewsForm
from news import News
from users import User
from countrys import Countrys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pd6uKfJLInXEPKa8eLT8'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'animal_clinic'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)
app.permanent_session_lifetime = datetime.timedelta(days=1)
app.secret_key = 'otp'
app.secret_key = 'phone_number'
app.secret_key = 'country_id'
app.secret_key = "hospital_id"

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    database.global_init("blogs.db")
    app.run()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@login_manager.user_loader
def load_user(user_id):
    db_sess = database.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/", methods=['GET', 'POST'])
def index1():
    db_sess = database.create_session()
    if request.method == 'POST':
        f = request.files['f']
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user.img:
            os.remove(f'static/img/{user.img}')
        user.img = str(current_user.id) + '.' + str(f.filename.split('.')[-1])
        db_sess.commit()
        image = Image.open(BytesIO(f.read()))
        image.save(f'static/img/{user.img}')

    return render_template("index.html", lenta='lenta')


@app.route("/news_local", methods=['GET', 'POST'])
def news_local():
    db_sess = database.create_session()
    news = db_sess.query(News).filter(News.is_private != True)
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news)


@jsf.use(app)
class App:
    def __init__(self):
        self.count = 0

    def test(self, value):
        self.count = int(value)
        self.js.document.getElementById("count").innerHTML = self.count


@app.route("/record/1", methods=['GET', 'POST'])
@login_required
def record1():
    if request.method == 'POST':
        if request.form.get('select_page_country'):
            session['country_id'] = str(request.form.get('select_page_country'))
            return redirect("/record/2")
    db_sess = database.create_session()
    if current_user.is_authenticated:
        countrys = db_sess.query(Countrys)
    return render_template("record1.html", values=countrys)


@app.route("/record/2", methods=['GET', 'POST'])
@login_required
def record2():
    if request.method == 'POST':
        if request.form.get('hospital_id'):
            session['hospital_id'] = str(request.form.get('select_page_country'))
            session.pop('country_id', None)
            return redirect("/record/3")
    db_sess = database.create_session()
    if current_user.is_authenticated:
        hospitals = db_sess.query(Hospital).filter(Hospital.country_id == session['country_id'])
    return render_template("record2.html", values=hospitals)


@app.route("/record/3", methods=['GET', 'POST'])
@login_required
def record3():
    if request.method == 'POST':
        if request.form.get('veterinarian_id'):
            session['veterinarian_id'] = str(request.form.get('veterinarian_id'))
            session.pop('hospital_id', None)
            return redirect("/record/4")
    db_sess = database.create_session()
    if current_user.is_authenticated:
        veterinarians = db_sess.query(Veterinarian).filter(Veterinarian.hospital_id == session['hospital_id'])
    return render_template("record3.html", values=veterinarians)


@app.route("/record/4", methods=['GET', 'POST'])
@login_required
def record4():
    return render_template("record4.html")


# Регистрация
@app.route('/register')
def reqister():
    return render_template('reg_phone.html')


@app.route('/getOTP', methods=['POST'])
def getOTP():
    number = request.form['number']
    getOTPApi(number)
    return render_template('getOTP.html')


@app.route('/validateOTP', methods=['POST'])
def validateOTP():
    otp = request.form['otp']
    if 'otp' in session:
        print(session["otp"])
        s = session["otp"]
        session.pop('otp', None)
        if otp == s:
            return render_template('reg_name_psw_surname.html')


def getOTPApi(number):
    code = random.randint(10000, 1000000)
    # a = sms.SMSTransport()
    print(number[1:])
    # a.send(to=number[1:], msg=str(code))
    session['phone_number'] = number
    session['otp'] = str(code)
    print(code)
    return code


@app.route('/finish_register', methods=['POST'])
def finish_register():
    if request.method == 'POST':
        if request.form.get('username') \
                and request.form.get('pass1') and request.form.get('pass2'):
            if request.form.get('pass1') != request.form.get('pass2'):
                return render_template('reg_name_psw_surname.html',
                                       message="Пароли не совпадают")
            if '-' in request.form.get('username'):
                return render_template('reg_name_psw_surname.html',
                                       message="В нике недопустимый знак '-'")
            db_sess = database.create_session()
            user = User(phone_number=session['phone_number'],
                        name=request.form.get('username'),
                        surname=request.form.get('username'),
                        img=''
                        )
            user.set_password(request.form.get('pass1'))
            db_sess.add(user)
            db_sess.commit()
            session.pop('phone_number', None)
            return redirect('/login')


# Вход в аккаунт
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('phone_number') and request.form.get('pass'):
            db_sess = database.create_session()
            user = db_sess.query(User).filter(User.phone_number == request.form.get('phone_number')).first()

            if user and user.check_password(request.form.get('pass')):
                login_user(user)
                return redirect("/")
            return render_template('login.html',
                                   message="Неправильный номер телефона или пароль")
    return render_template('login.html')


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    bukva = {'1', '2', '3', "4", "5", "6", "7", '8', "9", "0"}
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = database.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        news.category_id = request.form.get('association')
        if request.files['f']:
            f = request.files['f']
            news.img = ''.join(list(bukva)) + '.' + str(f.filename.split('.')[-1])
            image = Image.open(BytesIO(f.read()))
            image.save(f'static/img_news/{news.img}')
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = database.create_session()
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
        db_sess = database.create_session()
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
    db_sess = database.create_session()
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
        db_sess = database.create_session()
        news = db_sess.query(News).filter(
            News.user_id == id)
        your_count = news.count()
    return render_template('index.html', news=news, lenta="home_page", img=current_user.img,
                           your_count=your_count, user_id=id)


@app.route("/home_page/<int:id>/<int:id_category>", methods=["GET", "POST"])
@login_required
def home_page_funny(id, id_category):
    if current_user.is_authenticated:
        db_sess = database.create_session()
        news = db_sess.query(News).filter(
            News.user_id == id, News.category_id == id_category)
        your_count = news.count()
    return render_template('index.html', news=news, lenta="home_page", your_count=your_count, user_id=id)


if __name__ == '__main__':
    main()
