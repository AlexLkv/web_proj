import datetime
import sqlalchemy
from sqlalchemy import orm
from database import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(SqlAlchemyBase, SerializerMixin, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    phone_number = sqlalchemy.Column(sqlalchemy.String, unique=True,
                                     index=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    img = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    news = orm.relation("News", back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
