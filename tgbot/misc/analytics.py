from datetime import date

import matplotlib
import pylab

from tgbot.misc.work_with_json import get_user_from_json_db
import matplotlib.pyplot as plt
import json

import numpy as np


def get_total_analytics(user_id):
    user = get_user_from_json_db(user_id)
    categories = user.get('categories')
    member_since = user.get('user_data').get('member_since')

    total_time = 0
    total_hours_without_based_seconds = 0
    total_operations = 0
    total_all_days = []

    for category in categories:
        seconds = category['seconds']
        total_time += seconds
        total_seconds_without_based_seconds = seconds - category['based_seconds']
        total_hours_without_based_seconds += total_seconds_without_based_seconds
        operations = category['operations']

        total_operations += len([x for x in operations if x.get('seconds') is not None])

        for operation in operations:

            if operation['date'] not in total_all_days:
                total_all_days.append(operation['date'])

    count_categories = len(categories)

    time_per_day = int(total_hours_without_based_seconds / len(total_all_days))

    average_time_in_category = int(total_hours_without_based_seconds / count_categories)

    return {'total_time': total_time,
            'total_sessions': total_operations,
            'time_per_day': time_per_day,
            'average_time_in_category': average_time_in_category,
            'count_categories': count_categories,
            'member_since': member_since}


def get_dict_data_all_seconds(user_id):
    with open('data/users.json', 'r', encoding='utf-8') as file:
        user = json.load(file).get(str(user_id))

    categories = user.get('categories')

    all_days_and_operations = {}

    for category in categories:
        operations = category.get('operations')
        for operation in operations:

            date = operation.get('date')
            seconds = operation.get('seconds')

            if seconds is None:
                seconds = 0

            if all_days_and_operations.get(date) is None:
                all_days_and_operations[date] = 0

            all_days_and_operations[date] += seconds / 3600

    all_days_and_operations = dict(sorted(all_days_and_operations.items()))
    return all_days_and_operations


def get_plot_total_time(user_id):
    data_dict = get_dict_data_all_seconds(user_id)
    days = list(data_dict.keys())
    seconds = data_dict.values()

    all_time_progress_list = [0]
    for sec in seconds:
        last_all_time = all_time_progress_list[-1]
        all_time_progress_list.append(last_all_time + sec)
    all_time_progress_list = all_time_progress_list[1:]

    plt.title('Изменение количества общих часов')
    plt.xlabel('День использования бота')
    plt.ylabel('Потрачено часов')
    plt.xticks(range(len(days)))
    day_use_bot = list(range(len(days)))
    
    if len(days) == 1:
        plt.plot(day_use_bot, all_time_progress_list, 'o-r')
    else:
        plt.plot(day_use_bot, all_time_progress_list, 'r')

    plt.savefig(f'data/{user_id}_total_time.png')
    plt.clf()
