import json
from datetime import datetime


def get_user_from_json_db(user_id):
    """Получения данных пользователя из БД"""
    with open('data/users.json', 'r', encoding='utf-8') as db:
        return json.load(db).get(str(user_id))


def update_user_data(user_id, new_data):
    """Обновление данных пользователя В БД"""
    with open('data/users.json', 'r', encoding='utf-8') as db:
        old_users_data = json.load(db)

    old_users_data[str(user_id)] = new_data

    with open('data/users.json', 'w', encoding='utf-8') as db:
        json.dump(old_users_data, db, indent=4, ensure_ascii=False)


def fill_past_date(user_id, callback_data):
    """Заполнение дней, в которые бот не использовался, пустыми датами"""
    date = str(datetime.now()).split()[0]

    days_in_month = {
        1: 31,
        2: [28, 29],
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31
    }

    user = get_user_from_json_db(user_id)

    category = {}
    for category in user['categories']:
        if category['callback_data'] == callback_data:
            break

    operations = category.get('operations')

    if len(operations) == 0:
        operations.append({'date': date,
                           'start': None,
                           'end': None,
                           'seconds': None})

        update_user_data(user_id, user)
        return

    dates = get_all_dates_operations(operations)

    while date not in dates:
        operations.append({'date': date,
                           'start': None,
                           'end': None,
                           'seconds': None})
        dates.append(date)

        year, month, day = list(map(int, date.split('-')))

        if day > 1:
            day -= 1
        else:
            if month > 1:
                month -= 1
                if month == 2:
                    if year % 4 == 0:
                        day = days_in_month[month][1]
                    else:
                        day = days_in_month[month][0]
                else:
                    day = days_in_month[month]
            else:
                year -= 1
                month = 12
                day = days_in_month[month]

        date = str(year) + '-' + '0' * (2 - len(str(month))) + str(month) + '-' + '0' * (2 - len(str(day))) + str(day)

    operations = list(sorted(operations, key=lambda x: x['date']))

    category['operations'] = operations

    update_user_data(user_id, user)


def fill_all_categories_past_date(user_id):
    """Применение функции fill_past_date ко всем категориям"""
    user = get_user_from_json_db(user_id)
    categories = user['categories']

    for category in categories:
        callback_data = category['callback_data']

        fill_past_date(user_id, callback_data)


def possible_add_time(user_id, time_in_seconds, category_name):
    """Проверка на возможность добавить время"""
    user = get_user_from_json_db(user_id)

    categories = user.get('categories')

    for category in categories:
        if category['name'] == category_name:
            operations = category['operations']
            seconds_today = get_total_sec_today(operations)
            return {'is_possible_add_time': seconds_today + time_in_seconds <= 86_400,
                    'seconds_today': seconds_today}


def get_all_dates_operations(operations):
    """Получить все даты операций"""
    dates = []
    for operation in operations:
        dates.append(operation['date'])

    return dates


def get_total_sec_today(operations):
    """Получить общее время в секундах"""
    today = str(datetime.now()).split()[0]
    last_operation_data = '3000-01-01'

    total_sec_today = 0
    for operation in operations:

        if operation.get('seconds') is None:
            continue

        if operation.get('date') > last_operation_data == today:
            break

        if operation.get('date') == today:
            total_sec_today += operation.get('seconds')

        last_operation_data = operation['date']
    return total_sec_today


def get_all_not_none_category_operations(user_id, category_name):
    """Получить все не пустые операции"""
    user = get_user_from_json_db(user_id)

    not_none_operations = []
    for category in user['categories']:
        if category['name'] == category_name:
            operations = category.get('operations')
            for operation in operations:
                if operation.get('seconds') is not None:
                    not_none_operations.append(operation)

    return not_none_operations


def get_operation_by_serial_number_from_the_end(user_id, category_name, serial_number_of_operation):
    """Получить операцию по серийному номеру"""
    operations = get_all_not_none_category_operations(user_id, category_name)

    index = int(serial_number_of_operation) - 1

    operation = operations[-10:][index]

    return operation


def delete_operation_from_db(user_id, category_name, operation):
    """Удаление операции из БД"""
    user = get_user_from_json_db(user_id)
    categories = user['categories']

    category = None
    for category in categories:
        if category['name'] == category_name:
            break

    operations = category['operations']

    if operation in operations:
        operations.remove(operation)
        category['seconds'] -= operation.get('seconds')
        update_user_data(user_id, user)
        return
