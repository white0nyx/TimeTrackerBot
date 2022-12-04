import json
from datetime import datetime


def get_user_from_json_db(user_id):
    with open('data/users.json', 'r', encoding='utf-8') as db:
        return json.load(db).get(str(user_id))


def update_user_data(user_id, new_data):
    with open('data/users.json', 'r+', encoding='utf-8') as db:
        old_users_data = json.load(db)
        del old_users_data[str(user_id)]
        old_users_data[user_id] = new_data
        db.seek(0)
        json.dump(old_users_data, db, indent=4, ensure_ascii=False)


def fill_past_date(user_id, callback_data, date=str(datetime.now()).split()[0]):
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
        operations[date] = 0
        update_user_data(user_id, user)
        return

    while date not in operations.keys():
        operations[date] = 0

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

    operations = dict(sorted(operations.items(), key=lambda x: x[0]))

    category['operations'] = operations

    update_user_data(user_id, user)


def fill_all_categories_past_date(user_id):
    user = get_user_from_json_db(user_id)
    categories = user['categories']

    for category in categories:
        callback_data = category['callback_data']

        fill_past_date(user_id, callback_data)






