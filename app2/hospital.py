import sqlalchemy
from sqlalchemy import orm
from database import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Hospital(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'hospital'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    hospital_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    country_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("countrys.id"))
    countrys = orm.relation('Countrys')

    veterinarian_id = orm.relation("Veterinarian", back_populates='hospital')
    # chiefphysician_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("chiefphysician.id"))
    # chiefphysician = orm.relation('Chiefphysician')
