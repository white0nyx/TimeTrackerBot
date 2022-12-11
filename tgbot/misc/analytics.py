from datetime import date, datetime

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

    plt.figure(figsize=(9, 6))

    all_time_progress_list = [0]
    for sec in seconds:
        last_all_time = all_time_progress_list[-1]
        all_time_progress_list.append(last_all_time + sec)
    all_time_progress_list = all_time_progress_list[1:]

    plt.title('Изменение количества общих часов')
    plt.xlabel('День использования бота')
    plt.ylabel('Потрачено часов')
    plt.xticks(range(len(days)))
    day_use_bot = list(range(1, len(days) + 1))

    if len(days) == 1:
        plt.plot(day_use_bot, all_time_progress_list, 'o-r')
    else:
        plt.plot(day_use_bot, all_time_progress_list, 'r')

    plt.grid()
    plt.savefig(f'data/{user_id}_total_time.png')
    plt.clf()


def get_statistic_by_day_of_week(user_id):
    user = get_user_from_json_db(user_id)
    categories = user.get('categories')

    days_and_sessions = {'monday': {'hours': 0, 'sessions': 0},
                         'tuesday': {'hours': 0, 'sessions': 0},
                         'wednesday': {'hours': 0, 'sessions': 0},
                         'thursday': {'hours': 0, 'sessions': 0},
                         'friday': {'hours': 0, 'sessions': 0},
                         'saturday': {'hours': 0, 'sessions': 0},
                         'sunday': {'hours': 0, 'sessions': 0}}

    dict_data_all_seconds = get_dict_data_all_seconds(user_id)

    for date, hours in dict_data_all_seconds.items():
        year, month, day = map(int, date.split('-'))

        days = {0: 'monday',
                1: 'tuesday',
                2: 'wednesday',
                3: 'thursday',
                4: 'friday',
                5: 'saturday',
                6: 'sunday'}

        day_of_week = days[datetime(year, month, day).weekday()]

        days_and_sessions[day_of_week]['hours'] += hours

    for category in categories:
        for operation in category.get('operations'):
            date = operation.get('date')
            seconds = operation.get('seconds')

            if seconds is None:
                continue

            year, month, day = map(int, date.split('-'))

            days = {0: 'monday',
                    1: 'tuesday',
                    2: 'wednesday',
                    3: 'thursday',
                    4: 'friday',
                    5: 'saturday',
                    6: 'sunday'}

            day_of_week = days[datetime(year, month, day).weekday()]
            if seconds > 0:
                days_and_sessions[day_of_week]['sessions'] += 1

    return days_and_sessions


def get_diagram_week_statistic(user_id):
    days_and_sessions = get_statistic_by_day_of_week(user_id)

    days_of_week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

    hours_per_day = []
    sessions_per_day = []
    for day in days_and_sessions.values():
        hours_per_day.append(day.get('hours'))
        sessions_per_day.append(day.get('sessions'))

    width = 0.3

    x = np.arange(len(days_of_week))

    fig, ax = plt.subplots(figsize=(9, 6))

    rects_1 = ax.bar(x - width / 2, hours_per_day, width, label='Часы')
    rects_1 = ax.bar(x + width / 2, sessions_per_day, width, label='Сессии')

    ax.set_title('Статистика по дням')
    ax.set_xticks(x)
    ax.set_xticklabels(days_of_week)
    ax.legend()
    ax.grid()
    plt.savefig(f'data/{user_id}_week_statistic.png')
    plt.clf()
