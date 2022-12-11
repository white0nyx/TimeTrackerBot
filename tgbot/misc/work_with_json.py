import json
from datetime import datetime


def get_user_from_json_db(user_id):
    with open('data/users.json', 'r', encoding='utf-8') as db:
        return json.load(db).get(str(user_id))


def update_user_data(user_id, new_data):
    with open('data/users.json', 'r', encoding='utf-8') as db:
        old_users_data = json.load(db)

    old_users_data[str(user_id)] = new_data

    with open('data/users.json', 'w', encoding='utf-8') as db:
        json.dump(old_users_data, db, indent=4, ensure_ascii=False)


def fill_past_date(user_id, callback_data):

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
    user = get_user_from_json_db(user_id)
    categories = user['categories']

    for category in categories:
        callback_data = category['callback_data']

        fill_past_date(user_id, callback_data)


def possible_add_time(user_id, time_in_seconds, category_name):
    user = get_user_from_json_db(user_id)

    categories = user.get('categories')

    for category in categories:
        if category['name'] == category_name:
            operations = category['operations']
            seconds_today = get_total_sec_today(operations)
            return {'is_possible_add_time': seconds_today + time_in_seconds <= 86_400,
                    'seconds_today': seconds_today}


def possible_sub_time(user_id, time_in_seconds, category_name):
    user = get_user_from_json_db(user_id)

    categories = user.get('categories')

    for category in categories:
        if category['name'] == category_name:
            operations = category['operations']
            seconds_today = get_total_sec_today(operations)
            return {'is_possible_sub_time': seconds_today - time_in_seconds >= 0,
                    'seconds_today': seconds_today}


def get_all_dates_operations(operations):
    dates = []
    for operation in operations:
        dates.append(operation['date'])

    return dates


def get_total_sec_today(operations):
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


def get_all_category_operations(user_id, category_name):
    user = get_user_from_json_db(user_id)

    operations = None
    for category in user['categories']:
        if category['name'] == category_name:

            operations = category.get('operations')

            break

    return operations





