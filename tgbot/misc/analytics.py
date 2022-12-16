from datetime import datetime

from tgbot.misc.work_with_json import get_user_from_json_db
import matplotlib.pyplot as plt
import json

import numpy as np


def get_total_analytics(user_id):
    """Получение общей статистики"""
    user = get_user_from_json_db(user_id)
    categories = user.get('categories')
    member_since = user.get('user_data').get('member_since')

    total_time = 0
    time_before_bot = 0
    total_hours_without_based_seconds = 0
    total_operations = 0
    total_all_days = []

    for category in categories:
        seconds = category['seconds']
        total_time += seconds
        time_before_bot += category['based_seconds']
        total_seconds_without_based_seconds = seconds - category['based_seconds']
        total_hours_without_based_seconds += total_seconds_without_based_seconds
        operations = category['operations']

        total_operations += len([x for x in operations if x.get('seconds') is not None and x.get('seconds') > 0])

        for operation in operations:

            if operation['date'] not in total_all_days:
                total_all_days.append(operation['date'])

    count_categories = len(categories)

    time_per_day = int(total_hours_without_based_seconds / len(total_all_days))

    average_time_in_category = int(total_hours_without_based_seconds / count_categories)

    time_after_bot = total_time - time_before_bot

    return {'total_time': total_time,
            'time_before_bot': time_before_bot,
            'time_after_bot': time_after_bot,
            'total_sessions': total_operations,
            'time_per_day': time_per_day,
            'average_time_in_category': average_time_in_category,
            'count_categories': count_categories,
            'member_since': member_since}


def get_dict_data_all_seconds(user_id):
    """Получение словаря, где ключ - день, значение - потраченное время в секундах в этот день"""
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
    """Построение графика изменения общего времени"""
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
    """Получение словаря, который хранит часы и сессии для каждого дня недели"""
    user = get_user_from_json_db(user_id)
    categories = user.get('categories')

    days = {0: 'monday',
            1: 'tuesday',
            2: 'wednesday',
            3: 'thursday',
            4: 'friday',
            5: 'saturday',
            6: 'sunday'}

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

        day_of_week = days[datetime(year, month, day).weekday()]

        days_and_sessions[day_of_week]['hours'] += hours

    for category in categories:
        for operation in category.get('operations'):
            date = operation.get('date')
            seconds = operation.get('seconds')

            if seconds is None:
                continue

            year, month, day = map(int, date.split('-'))

            day_of_week = days[datetime(year, month, day).weekday()]
            if seconds > 0:
                days_and_sessions[day_of_week]['sessions'] += 1

    return days_and_sessions


def get_diagram_week_statistic(user_id):
    """Получение диаграммы, которая отображает количество часов и сессий на каждый день недели"""
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

    ax.bar(x - width / 2, hours_per_day, width, label='Часы')
    ax.bar(x + width / 2, sessions_per_day, width, label='Сессии')

    ax.set_title('Статистика по дням')
    ax.set_xticks(x)
    ax.set_xticklabels(days_of_week)
    ax.legend()
    ax.grid()
    plt.savefig(f'data/{user_id}_week_statistic.png')
    plt.clf()


def get_duration_sessions_data(user_id):
    """Получение словаря, где ключ - длина сессий, значение - количество сессий такой длины"""
    sessions_durations = {'< 30 минут': 0, '30-60 минут': 0, '1-2 часа': 0, '2-4 часа': 0, '4+ часа': 0}

    user = get_user_from_json_db(user_id)
    categories = user.get('categories')

    for category in categories:

        for operation in category.get('operations'):

            seconds = operation.get('seconds')

            if seconds is None or seconds <= 0:
                continue

            if seconds < 1_800:
                sessions_durations['< 30 минут'] += 1

            elif 1_800 <= seconds < 3_600:
                sessions_durations['30-60 минут'] += 1

            elif 3_600 <= seconds < 7_200:
                sessions_durations['1-2 часа'] += 1

            elif 7_200 <= seconds < 14_400:
                sessions_durations['2-4 часа'] += 1

            elif 14_400 <= seconds:
                sessions_durations['4+ часа'] += 1

    return sessions_durations


def get_circle_diagram_sessions_durations(user_id):
    """Получение круговой диаграммы, отображающей статистику по длинам сессий"""
    sessions_durations_data = get_duration_sessions_data(user_id)
    clear_sessions_durations_data = {}

    for key, value in sessions_durations_data.items():
        if value != 0:
            clear_sessions_durations_data[key] = value

    labels = list(clear_sessions_durations_data.keys())
    values = list(clear_sessions_durations_data.values())

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.pie(values, labels=labels, autopct='%1.1f%%', shadow=False,
           wedgeprops={'lw': 1, 'ls': '-', 'edgecolor': 'k'},
           rotatelabels=True)
    ax.axis('equal')

    plt.savefig(f'data/{user_id}_sessions_durations_statistic.png')
    plt.clf()


def is_possible_get_circle_diagram_sessions_durations(user_id):
    """Проверка возможности создать круговую диаграмму"""
    sessions_durations_data = get_duration_sessions_data(user_id)
    values = tuple(sessions_durations_data.values())
    return not values[0] == values[1] == values[2] == values[3] == values[4] == 0


def get_statistic_by_hours_in_day(user_id):
    """Получение статистики по часам"""
    user = get_user_from_json_db(user_id)

    hours_in_day = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0,
                    10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0,
                    20: 0, 21: 0, 22: 0, 23: 0}

    categories = user.get('categories')

    for category in categories:

        for operation in category['operations']:

            hour_start = int(operation.get('start').split(':')[0])
            hour_end = int(operation.get('end').split(':')[0])

            for operation_hour in get_range_hours(hour_start, hour_end):
                hours_in_day[operation_hour] += 1

    return hours_in_day


def get_diagram_by_hours_in_day(user_id):
    """Получение диаграммы, отображающей статистику по часам"""
    hours_in_day = get_statistic_by_hours_in_day(user_id)
    hours = list(hours_in_day.keys())
    counts = list(hours_in_day.values())

    x = np.arange(len(hours))

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.bar(hours, counts)

    plt.xlabel('Время суток')
    plt.ylabel('Количество сессий')

    ax.set_title('Время, когда вы пользуетесь ботом')
    ax.set_xticks(x)
    ax.set_xticklabels(hours)

    plt.savefig(f'data/{user_id}_session_count_by_hour_in_day.png')
    plt.clf()


def get_range_hours(start, stop):
    """Получение промежутка часов"""
    result = []

    if stop < start:
        no_hours = []
        for i in range(start - 1, stop, -1):
            no_hours.append(i)

        for i in range(0, 24):
            if i not in no_hours:
                result.append(i)

    else:
        for i in range(start, stop + 1):
            result.append(i)

    return result
