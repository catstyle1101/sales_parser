import os
import re

from dotenv import load_dotenv

from errors import ManagerNotFoundError

from models import Manager

from sqlalchemy import and_, create_engine, select
from sqlalchemy.orm import Session

load_dotenv()

DB_ADDRESS = os.getenv('DB_ADDRESS')


class Prefix:
    def __init__(self, prefix: str):
        pattern = r'^[0-9]{3}[\/][0-9]{0,3}$'
        if re.match(pattern=pattern, string=prefix):
            self.prefix = prefix
        else:
            raise ValueError('Неверный префикс менеджера')

    def __repr__(self):
        return self.prefix


class DataBase:

    def __init__(self):
        engine = create_engine(
            f"sqlite:///{DB_ADDRESS}",
            echo=False,
        )

        self.session = Session(engine)

    def get_all_managers(self) -> list[Manager]:
        stmt = select(Manager).where(Manager.is_manager == 1)
        result = list()
        for manager in self.session.scalars(stmt):
            result.append(manager)
        return result

    def get_all_not_managers(self) -> list[Manager]:
        stmt = select(Manager).where(Manager.is_manager == 0)
        result = list()
        for manager in self.session.scalars(stmt):
            result.append(manager)
        return result

    def get_manager_by_prefix(self, prefix: str) -> Manager:
        stmt = select(Manager).where(and_(Manager.prefix == prefix, Manager.is_manager == 1))
        return self.session.scalar(stmt)

    def get_manager_by_short_name(self, short_name: str) -> Manager:
        stmt = select(Manager).where(Manager.short_fullname == short_name)
        result = self.session.scalar(stmt)
        if result:
            return self.session.scalar(stmt)
        else:
            raise ManagerNotFoundError()

    def get_manager_by_internal_digit_code(self, internal_digit_code: str) -> Manager:
        stmt = select(Manager).where(Manager.internal_digit_code == internal_digit_code)
        result = self.session.scalar(stmt)
        if result:
            return self.session.scalar(stmt)
        else:
            raise ManagerNotFoundError(f'Менеджер с кодом {internal_digit_code} не найден в БД')
