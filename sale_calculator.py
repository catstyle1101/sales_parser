import datetime
from dataclasses import dataclass
from statistics import median

from database import DataBase

from models import Manager


RETAIL_TRESHOLD = 15000
PRIVATE_CUSTOMER_TRESHOLD = 15000
B2B_TRESHOLD = 50000
RETAIL = 'РМОПП'
PRIVATE_CUSTOMER = 'ООК'


@dataclass()
class Sale:
    int_number: str
    number: str
    client: str
    date: datetime.datetime
    sum_doc: float
    i: bool
    manager: Manager


class ManagerSales:
    def __init__(self):
        pass


def calculate_sales(data: list[Sale]) -> dict:
    result = dict()
    for sale in data:
        if result.get(sale.manager):
            if result[sale.manager].get(sale.client):
                result[sale.manager][sale.client] += int(sale.sum_doc)
            else:
                result[sale.manager].update({sale.client: int(sale.sum_doc)})
        else:
            result[sale.manager] = {sale.client: int(sale.sum_doc)}
    return result


def calculate_rating(manager_sales: dict) -> dict:
    result = dict()
    base = DataBase()
    for manager, sales in manager_sales.items():
        man = base.get_manager_by_short_name(str(manager))
        if man.specialization == RETAIL:
            pkb_value = RETAIL_TRESHOLD
        elif man.specialization == PRIVATE_CUSTOMER:
            pkb_value = PRIVATE_CUSTOMER_TRESHOLD
        else:
            pkb_value = B2B_TRESHOLD
        result[manager] = {
          'sum': sum(sales.values()),
          'median': int(median(sales.values())),
          'pkb': len([i for i in sales.values() if i > pkb_value]),
                         }
    return _sort_sales(result)


def _sort_sales(result: dict) -> dict:
    sorted_keys = sorted(result, key=lambda x: result[x]['sum'], reverse=True)
    sorted_sales = dict()
    for item in sorted_keys:
        sorted_sales[item] = result[item]
    return sorted_sales


def calculate_full_rating(data: list[Sale]):
    manager_sales = calculate_sales(data)
    data_for_rating = calculate_rating(manager_sales)
    return data_for_rating
