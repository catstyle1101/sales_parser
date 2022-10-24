import datetime
import json
import os
import time
from typing import NamedTuple

from tqdm import tqdm

from database import DataBase, Prefix

from dotenv import load_dotenv

from errors import ManagerNotFoundError, TooManyDocumentsError

from models import Manager

import requests

from sale_calculator import Sale, calculate_full_rating

from sale_formatter import format_data_rating

load_dotenv()

INDEX_I = 1
INDEX_NUMDOC = 2
INDEX_CLIENT = 5
INDEX_DATE = 6
INDEX_SUM = 14
DOMAIN = os.getenv('DOMAIN')
LOGIN_URL = os.getenv('LOGIN_URL')
SCRAPE_URL = os.getenv('SCRAPE_URL')
SCRAPE_MANAGER_URL = os.getenv('SCRAPE_MANAGER_URL')


class DatesOfDocuments(NamedTuple):
    date_begin: str
    date_end: str


def timer(func) -> None:

    def wrapper():
        time_start = time.time()
        func()
        print()
        print(f'Время работы {int(time.time() - time_start)} секунд')
    return wrapper


@timer
def main():
    session = create_session()
    base = DataBase()
    list_of_managers = base.get_all_managers()
    list_of_dates = get_list_of_dates()
    sales_data = collect_all_data(session, list_of_dates, list_of_managers, base)
    data_for_rating = calculate_full_rating(sales_data)
    formatted_string = format_data_rating(data_for_rating)
    print()
    print(formatted_string)


def create_session() -> requests.Session:
    headers = {
        'authority': f'{DOMAIN}',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 '
                       '(KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'),
        'x-requested-with': 'XMLHttpRequest',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'referer': f'https://{DOMAIN}/cat/invoice.html',
        'accept-language': 'en-US,en;q=0.9,ru;q=0.8',
        }
    login = os.getenv('USER')
    password = os.getenv('PASSWORD')
    auth_data = {'auth[password]': password, 'auth[login]': login}
    session = requests.session()
    result = session.get(
        LOGIN_URL.format(login, password),
        data=auth_data, headers=headers,
    )
    session_id = result.cookies.get('session-id')
    if result.status_code == 200:
        print(f'Connection established. Session ID is {session_id}')
        return session
    else:
        raise ConnectionError


def get_list_of_dates(month: (int | None) = None) -> list[DatesOfDocuments]:
    """Split dates of current month to list of DatesOfDocumnents"""
    increment = 5
    date_pattern = "%d/%m/%y"
    year = datetime.date.today().year
    list_of_dates = list()
    today = datetime.date.today()
    if month:
        today = (datetime.date(year=year, month=(month % 12) + 1, day=1) + datetime.timedelta(days=-1))
    for i in range(1, today.day + 1, increment + 1):
        date_begin = datetime.date(day=i, month=today.month, year=today.year)
        try:
            date_end = datetime.date(day=i+increment, month=today.month, year=today.year)
        except ValueError:
            date_end = datetime.date(year=year, month=(month % 12) + 1, day=1) + datetime.timedelta(days=-1)
        if i + increment > today.day:
            date_end = datetime.date(day=today.day, month=today.month, year=today.year)
        date = DatesOfDocuments(
            date_begin.strftime(date_pattern),
            date_end.strftime(date_pattern),
        )
        list_of_dates.append(date)
    return list_of_dates


def collect_all_data(
        session: requests.Session,
        dates: list[DatesOfDocuments],
        managers: list[Manager],
        base) -> list[Sale]:
    result = list()
    prefixes = [i.prefix for i in managers] + [i.prefix for i in base.get_all_not_managers()]
    jobs = len(dates) * len(prefixes)
    progress_bar = tqdm(total=jobs, colour='green')
    for date in dates:
        for prefix in prefixes:
            progress_bar.update(1)
            data = parse_data(session, date, prefix, managers, base)
            if data:
                for string in data:
                    result.append(string)
    progress_bar.close()
    return result


def parse_data(
        session: requests.Session,
        dates: DatesOfDocuments,
        prefix: Manager.prefix,
        managers: list[Manager],
        base):
    url = SCRAPE_URL.format(dates.date_begin, dates.date_end, prefix)
    response = session.get(url)
    result = json.loads(response.text)
    if _check_parsed_data(result, dates=dates, prefix=prefix):
        return _parse_json(result, session, managers, base)


def _check_parsed_data(result: json, dates: DatesOfDocuments, prefix: Manager.prefix):
    if result['records'] == 0:
        return None
    if result['userdata']['limit'] == 'yes':
        raise TooManyDocumentsError(f'Слишком много документов в периоде {dates}, префикс {prefix}')
    return True


def _parse_json(json_, session, managers_list, base) -> list[Sale]:
    result = list()
    for row in json_['rows']:
        try:
            sum_doc = float(row['cell'][INDEX_SUM])
        except ValueError:
            sum_doc = 0
        prefix = Prefix(row['cell'][INDEX_NUMDOC][:7])
        manager = base.get_manager_by_prefix(str(prefix))
        if not manager:
            try:
                manager = base.get_manager_by_internal_digit_code(
                    scrap_manager(row['id'], session, managers_list))
            except ManagerNotFoundError:
                continue
        if manager:
            result.append(Sale(
                int_number=row['id'],
                number=row['cell'][INDEX_NUMDOC],
                client=row['cell'][INDEX_CLIENT],
                date=datetime.datetime.strptime(row['cell'][INDEX_DATE], '%d/%m/%y'),
                sum_doc=sum_doc,
                i=row['cell'][INDEX_I] == 'i',
                manager=manager,
            ))
    return result


def scrap_manager(numdoc, session, managers_list) -> str:
    url = SCRAPE_MANAGER_URL.format(numdoc)
    string = session.get(url).text
    if 'Запись не найдена' in string:
        return 0
    val_manager = string.find('contact_mandetail')
    begin = string.find('(', val_manager) + 1
    end = string.find(')', val_manager)
    return int(string[begin:end])


if __name__ == '__main__':
    main()
