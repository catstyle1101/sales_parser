from database.models import Manager

MESSAGE_TEMPLATE = '{manager:17} ГО: {sum:10,}, медиана: {median:8,} ПКБ: {pkb:2}\n'
MEDALS = {1: '🏆 ', 2: '🥈 ', 3: '🥉 '}
EXCLAMATIONS_COUNT_IN_MESSAGE = 10


def format_data_rating(data: dict[Manager, ]) -> str:
    attention = '❗' * EXCLAMATIONS_COUNT_IN_MESSAGE
    header = '\nРезультаты продаж менеджеров:\n'
    results = list()
    for idx, (manager, sales) in enumerate(data.items(), 1):
        results.append(MESSAGE_TEMPLATE.format(
            manager=''.join([MEDALS.get(idx, ''), manager.short_fullname]),
            sum=sales['sum'],
            median=sales['median'],
            pkb=sales['pkb'],
            ).replace(',', ' '))
    return ''.join(([attention, header] + results + [attention, ]))
