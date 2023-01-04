from datetime import datetime

from tgbot.misc.work_with_json import get_user_from_json_db, get_all_not_none_category_operations, \
    get_count_sessions_for_period, get_time_per_day_for_category, get_time_per_categories_for_period
import matplotlib.pyplot as plt
import json

import numpy as np


def get_total_analytics(user_id, period_statistic):
    """Получение общей статистики"""
    user = get_user_from_json_db(user_id)
    categories = user.get('categories')
    member_since = user.get('user_data').get('member_since')

    total_time = 0
    time_before_bot = 0
    total_hours_without_based_seconds = 0
    total_sessions = 0
    total_all_days = []

    if period_statistic == 'all_time':
        for category in categories:
            seconds = category['seconds']
            total_time += seconds
            time_before_bot += category['based_seconds']
            total_seconds_without_based_seconds = seconds - category['based_seconds']
            total_hours_without_based_seconds += total_seconds_without_based_seconds
            operations = category['operations']

            total_sessions += len([x for x in operations if x.get('seconds') is not None and x.get('seconds') > 0])

            for operation in operations:

                if operation['date'] not in total_all_days:
                    total_all_days.append(operation['date'])

        if total_sessions == 0:
            return 'No sessions'

        current_series = get_current_series(user_id)
        max_series = get_max_series(user_id)

        count_categories = len(categories)

        time_per_day = int(total_hours_without_based_seconds / len(total_all_days))

        average_time_in_category = int(total_hours_without_based_seconds / count_categories)
        average_time_per_session = int(total_time / total_sessions)

        time_after_bot = total_time - time_before_bot

        return {'total_time': total_time,
                'time_before_bot': time_before_bot,
                'time_after_bot': time_after_bot,
                'total_sessions': total_sessions,
                'current_series': current_series,
                'max_series': max_series,
                'time_per_day': time_per_day,
                'average_time_in_category': average_time_in_category,
                'average_time_per_session': average_time_per_session,
                'count_categories': count_categories,
                'member_since': member_since}

    else:

        days_and_time = get_all_time_by_days(user_id)
        seconds_by_day = list(days_and_time.values())[-period_statistic:]
        total_time = sum(seconds_by_day)

        all_time = 0
        for category in categories:
            all_time += category['seconds']
            time_before_bot += category['based_seconds']
        total_sessions = sum(get_count_sessions_for_period(user_id, period_statistic))

        current_series = get_current_series(user_id)
        max_series = get_max_series(user_id)

        time_per_day = total_time // period_statistic

        count_categories = len(categories)
        average_time_in_category = int(total_time / count_categories)
        if total_sessions == 0:
            average_time_per_session = 0

        else:
            average_time_per_session = int(total_time / total_sessions)

        time_after_bot = all_time - time_before_bot
        return {'total_time': total_time,
                'time_before_bot': time_before_bot,
                'time_after_bot': time_after_bot,
                'total_sessions': total_sessions,
                'current_series': current_series,
                'max_series': max_series,
                'time_per_day': time_per_day,
                'average_time_in_category': average_time_in_category,
                'average_time_per_session': average_time_per_session,
                'count_categories': count_categories,
                'member_since': member_since
                }


def get_dict_date_all_seconds(user_id, period=None):
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

    if period is not None:
        keys = list(all_days_and_operations.keys())[-period:]
        values = list(all_days_and_operations.values())[-period:]
        all_days_and_operations = {}

        for i in range(len(keys)):
            all_days_and_operations[keys[i]] = values[i]

    return all_days_and_operations


def get_dict_date_all_sessions(user_id, period=None):
    user = get_user_from_json_db(user_id)
    categories = user['categories']
    date_all_sessions = {}

    for category in categories:
        for operation in category['operations']:
            date = operation['date']
            count_session = 0 if operation['seconds'] is None else 1

            if date not in date_all_sessions.keys():
                date_all_sessions[date] = count_session

            else:
                date_all_sessions[date] += count_session

    if period is not None:
        keys = list(date_all_sessions.keys())[-period:]
        values = list(date_all_sessions.values())[-period:]
        date_all_sessions = {}
        for i in range(len(keys)):
            date_all_sessions[keys[i]] = values[i]

    return date_all_sessions


def get_plot_total_time(user_id, period=None):
    """Построение графика изменения общего времени"""
    data_dict = get_dict_date_all_seconds(user_id)

    if period is None:
        days = list(data_dict.keys())
        seconds = data_dict.values()
    else:
        days = list(data_dict.keys())[-period:]
        seconds = list(data_dict.values())[-period:]

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
    plt.close()


def get_statistic_by_day_of_week(user_id, period=None):
    """Получение словаря, который хранит часы и сессии для каждого дня недели"""

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

    # Сбор информации о часах
    dict_data_all_seconds = get_dict_date_all_seconds(user_id, period)
    for date, hours in dict_data_all_seconds.items():
        year, month, day = map(int, date.split('-'))
        day_of_week = days[datetime(year, month, day).weekday()]
        days_and_sessions[day_of_week]['hours'] += hours

    # Сбор информации о сессиях
    date_all_sessions = get_dict_date_all_sessions(user_id, period)
    for date, sessions in date_all_sessions.items():
        year, month, day = map(int, date.split('-'))
        day_of_week = days[datetime(year, month, day).weekday()]
        days_and_sessions[day_of_week]['sessions'] += sessions

    return days_and_sessions


def get_diagram_week_statistic(user_id, period=None):
    """Получение диаграммы, которая отображает количество часов и сессий на каждый день недели"""
    days_and_sessions = get_statistic_by_day_of_week(user_id, period)

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
    plt.close(fig)


def get_duration_sessions_data(user_id, period=None):
    """Получение словаря, где ключ - длина сессий, значение - количество сессий такой длины"""
    sessions = {'< 30 минут': 0, '30-60 минут': 0, '1-2 часа': 0, '2-4 часа': 0, '4+ часа': 0}
    dict_date_sessions_durations = get_dict_date_sessions_durations(user_id, period)

    for date, sessions_durations in dict_date_sessions_durations.items():
        for key, value in sessions_durations.items():
            sessions[key] += value

    return sessions


def get_dict_date_sessions_durations(user_id, period=None):
    """Получить словарь вида {date: {'< 30 минут': x, ... '4+ часа': y}}, за указанный период"""
    user = get_user_from_json_db(user_id)

    dict_date_sessions_durations = {}
    for category in user['categories']:
        for operation in category['operations'][::-1]:

            date = operation['date']
            seconds = operation['seconds']

            if seconds is None:
                seconds = 0

            if period is not None and len(
                    dict_date_sessions_durations) == period and date not in dict_date_sessions_durations.keys():
                continue

            if date in dict_date_sessions_durations.keys():
                if 1 <= seconds < 1_800:
                    dict_date_sessions_durations[date]['< 30 минут'] += 1

                elif 1_800 <= seconds < 3_600:
                    dict_date_sessions_durations[date]['30-60 минут'] += 1

                elif 3_600 <= seconds < 7_200:
                    dict_date_sessions_durations[date]['1-2 часа'] += 1

                elif 7_200 <= seconds < 14_400:
                    dict_date_sessions_durations[date]['2-4 часа'] += 1

                elif 14_400 <= seconds:
                    dict_date_sessions_durations[date]['4+ часа'] += 1

            else:

                dict_date_sessions_durations[date] = {'< 30 минут': 0,
                                                      '30-60 минут': 0,
                                                      '1-2 часа': 0,
                                                      '2-4 часа': 0,
                                                      '4+ часа': 0,
                                                      }

                if 1 <= seconds < 1_800:
                    dict_date_sessions_durations[date]['< 30 минут'] = 1

                elif 1_800 <= seconds < 3_600:
                    dict_date_sessions_durations[date]['30-60 минут'] = 1

                elif 3_600 <= seconds < 7_200:
                    dict_date_sessions_durations[date]['1-2 часа'] = 1

                elif 7_200 <= seconds < 14_400:
                    dict_date_sessions_durations[date]['2-4 часа'] = 1

                elif 14_400 <= seconds:
                    dict_date_sessions_durations[date]['4+ часа'] = 1

    return dict_date_sessions_durations


def get_circle_diagram_sessions_durations(user_id, period=None):
    """Получение круговой диаграммы, отображающей статистику по длинам сессий"""
    sessions_durations_data = get_duration_sessions_data(user_id, period)
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
    plt.close(fig)


def is_possible_get_graphics(user_id):
    """Проверка возможности построить графики"""
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

            if operation.get('start') is None:
                continue

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
    plt.close(fig)


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


def get_all_time_by_days(user_id):
    """Получение словаря, где ключ - день, значение - общее количество потраченного времени в секундах"""
    all_operations = []
    user = get_user_from_json_db(user_id)
    categories = user.get('categories')

    for category in categories:
        operations = category.get('operations')
        for operation in operations:
            all_operations.append(operation)

    all_operations = list(sorted(all_operations, key=lambda x: x['date']))

    day_full_time_list = {}
    for operation in all_operations:

        date = operation.get('date')
        seconds = operation.get('seconds')

        if seconds is None:
            seconds = 0

        if date not in day_full_time_list.keys():
            day_full_time_list[date] = seconds

        else:
            day_full_time_list[date] += seconds

    return day_full_time_list


def get_max_series(user_id):
    """Получить максимальную серию"""
    low_minutes = 900
    time_by_days = get_all_time_by_days(user_id)

    series = 0
    max_series = 0
    for key, value in time_by_days.items():

        if value >= low_minutes:
            series += 1
            max_series = max(max_series, series)

        else:
            series = 0

    return max_series


def get_current_series(user_id):
    """Получить текущую серию"""

    low_minutes = 900
    time_by_days = get_all_time_by_days(user_id)
    reversed_days = list(time_by_days.values())[::-1]

    current_series = 0
    for day in reversed_days:

        if day < low_minutes:
            return current_series

        else:
            current_series += 1

    return current_series
