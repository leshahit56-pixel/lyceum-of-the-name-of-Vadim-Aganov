from .db_session import SqlAlchemyBase
import sqlalchemy


class User(SqlAlchemyBase):
    __tablename__ = 'user_information'
    id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, primary_key=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    patronymic = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    scores = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    avatar = sqlalchemy.Column(sqlalchemy.String, nullable=True)