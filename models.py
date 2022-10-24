from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Manager(Base):
    __tablename__ = 'managers'

    internal_digit_code = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    fullname = Column(String, nullable=False)
    short_fullname = Column(String, nullable=False)
    prefix = Column(String(10), unique=True, nullable=False)
    internal_alphanumeric_code = Column(String(10))
    is_manager = Column(Boolean, nullable=False)
    specialization = Column(String(10), nullable=False)

    def __repr__(self):
        return f'{self.short_fullname}'
