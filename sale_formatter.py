from models import Manager


def format_data_rating(data: dict[Manager, ]):
    message = '(exclamationmark)' * 10
    message += '\nРезультаты продаж менеджеров:\n'
    idx = 1
    for manager, sales in data.items():
        manager = manager.short_fullname
        if idx == 1:
            message += '(trophy) '
        if idx == 2:
            message += '(silvermedal) '
        if idx == 3:
            message += '(bronzemedal) '
        if idx < 4:

            message += f"{manager:17} ГО: {sales['sum']:10,}, медиана: " \
                       f"{sales['median']:8,} ПКБ: {sales['pkb']:2}\n".replace(',', ' ')
        else:
            message += f"{manager:23} ГО: {sales['sum']:10,}, медиана: " \
                       f"{sales['median']:8,} ПКБ: {sales['pkb']:2}\n".replace(',', ' ')
        idx += 1
    message += '(exclamationmark)' * 10
    return message
