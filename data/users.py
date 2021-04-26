import sqlalchemy
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.String,
                           primary_key=True)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)
    friends = sqlalchemy.Column(sqlalchemy.String, nullable=True, default="0")
