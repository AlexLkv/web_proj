import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from database import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Chiefphysician(SqlAlchemyBase, SerializerMixin, UserMixin):
    __tablename__ = 'chiefphysician'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    phone_number = sqlalchemy.Column(sqlalchemy.String, unique=True,
                                     index=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    login = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hospital_id = orm.relation("Hospital", back_populates='chiefphysician_id')
    hospital = orm.relation('Hospital')