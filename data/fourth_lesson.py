from .db_session import SqlAlchemyBase
import sqlalchemy

class Fourth_lesson(SqlAlchemyBase):
    __tablename__ = 'Fourth_lesson'
    user_email = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('user_information.email'), primary_key=True)
    exersize_one = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    exersize_one_solution = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    exersize_two = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    exersize_two_solution = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    exersize_three = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    exersize_three_solution = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    exersize_four = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    exersize_four_solution = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    exersize_five = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    exersize_five_solution = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    exersize_six = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    exersize_six_solution = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    exersize_seven = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    exersize_seven_solution = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    exersize_eight = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    exersize_eight_solution = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    exersize_nine = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    exersize_nine_solution = sqlalchemy.Column(sqlalchemy.Text, nullable=True)

    # 0 - ЗАДАЧА НЕ РЕШЕНА 1 - ЗАДАЧА РЕШЕНА НЕВЕРНО 2 - ЗАДАЧА РЕШЕНА ВЕРНО