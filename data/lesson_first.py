from .db_session import SqlAlchemyBase
import sqlalchemy

class First_lesson(SqlAlchemyBase):
    __tablename__ = 'First_lesson'
    first_exersize = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)