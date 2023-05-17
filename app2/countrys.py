import sqlalchemy
from sqlalchemy import orm
from database import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Countrys(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'countrys'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    country_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hospital_ids = orm.relation("Hospital", back_populates='country_id')


