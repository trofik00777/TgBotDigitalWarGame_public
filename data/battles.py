import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Battles(SqlAlchemyBase):
    __tablename__ = 'battles'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    player1 = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("users.username"), nullable=True)
    player2 = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("users.username"), nullable=True)
    id_board_1 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    id_board_2 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    position = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    step = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    winner = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("users.username"), nullable=True)
    isPlaying = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
