from tgbot.misc.analytics import get_total_analytics


def is_valid_time(str_time, for_edit_time=False):
    """Проверка на корректность введённого времени"""
    if str_time == '0':
        return True

    if str_time.count(':') != 2 or not str_time.replace(':', '').isdigit():
        return '⚠ Данные введены некорректно!\n\n' \
               'Не соблюдён формат чч:мм:сс\n\n' \
               'Пожалуйста, повторите ввод'

    h, m, s = str_time.split(':')

    if not h.isdigit():
        return '⚠ Данные введены некорректно!\n\n' \
               'Количество часов должно быть целым неотрицательным числом\n\n' \
               'Пожалуйста, повторите ввод'

    if for_edit_time and int(h) > 24:
        return '⚠ Данные введены некорректно!\n\n' \
               'Количество часов не должно превышать 24 часа'

    if not m.isdigit() or int(m) > 59:
        return '⚠ Данные введены некорректно!\n\n' \
               'Количество минут должно быть целым числом, ' \
               'которое не может превышать 59 или быть отрицательным\n\n' \
               'Пожалуйста, повторите ввод'

    if not s.isdigit() or int(s) > 59:
        return '⚠ Данные введены некорректно!\n\n' \
               'Количество секунд должно быть целым числом, ' \
               'которое не может превышать 59 или быть отрицательным\n\n' \
               'Пожалуйста, повторите ввод'

    time_in_seconds = int(h) * 3600 + int(m) * 60 + int(s)
    if for_edit_time and time_in_seconds > 86_400:
        return '⚠ Данные введены некорректно!\n\n' \
               'Указываемое время не должно превышать 24 часа'

    return True


def get_the_time_in_seconds(str_time: str):
    """Получение времени в секундах из строки чч:мм:сс"""
    if str_time == '0':
        return 0

    time_parts = str_time.split(':')
    h, m, s = tuple(map(int, time_parts))
    time_in_seconds = h * 3600 + m * 60 + s

    return time_in_seconds


def get_time_in_str_text(sec):
    """Получение времени в формате чч:мм:сс из секунд"""
    # sec = sec % (24 * 3600)
    hour = sec // 3600
    sec %= 3600
    minutes = sec // 60
    sec %= 60
    return "%02d:%02d:%02d" % (hour, minutes, sec)


def get_statistic(user_id, categories):
    """Получение текста для отображения статистики"""
    text = '📈 Ваша общая статистика\n\n'

    user_statistic = get_total_analytics(user_id)
    total_time = get_time_in_str_text(user_statistic.get('total_time'))
    time_before_bot = get_time_in_str_text(user_statistic.get('time_before_bot'))
    time_after_bot = get_time_in_str_text(user_statistic.get('time_after_bot'))
    total_sessions = user_statistic.get('total_sessions')
    time_per_day = get_time_in_str_text(user_statistic.get('time_per_day'))
    average_time_in_category = get_time_in_str_text(user_statistic.get('average_time_in_category'))
    count_categories = user_statistic.get('count_categories')
    member_since = user_statistic.get('member_since').split()[0]

    text += f'Потрачено времени: {total_time}\n' \
            f'До запуска бота: {time_before_bot}\n' \
            f'После запуска бота: {time_after_bot}\n\n' \
            f'Количество сессий: {total_sessions}\n\n' \
            f'Время в день: {time_per_day}\n' \
            f'Время на категорию: {average_time_in_category}\n\n' \
            f'Количество категорий: {count_categories}\n\n'

    for category in categories:
        text += f'{category["name"]} - {get_time_in_str_text(category["seconds"])}\n'

    text += f'\n👤 Подписчик с {member_since}\n\n'

    return text


def get_category_info_message(category_n: str, categories: list):
    """Получение текста для его отображения после нажатия на Inline-кнопку категории"""
    category = {}
    for category in categories:
        if category['callback_data'] == category_n:
            break
    category_name = category.get("name")
    category_all_time = get_time_in_str_text(category.get('seconds'))

    text = f'{category_name}\n\n' \
           f'Всего потрачено времени: {category_all_time}'

    return text


def get_word_end_vp(minutes: int):
    """Получить слово минуты в винительном падеже"""
    ends = {'0': 'минут',
            '1': 'минуту',
            '2': 'минуты',
            '3': 'минуты',
            '4': 'минуты',
            '5': 'минут',
            '6': 'минут',
            '7': 'минут',
            '8': 'минут',
            '9': 'минут'}

    str_number = str(minutes)

    if str_number[-2:] in ('11', '12', '13', '14'):
        return 'минут'

    else:
        return ends.get(str_number[-1])


def get_word_end_rp(minutes: int):
    """Получить слово минуты в родительном падеже"""
    ends = {'0': 'минут',
            '1': 'минуты',
            '2': 'минут',
            '3': 'минут',
            '4': 'минут',
            '5': 'минут',
            '6': 'минут',
            '7': 'минут',
            '8': 'минут',
            '9': 'минут'}

    str_number = str(minutes)

    if str_number[-2:] in ('11', '12', '13', '14'):
        return 'минут'

    else:
        return ends.get(str_number[-1])


def get_text_category_operations(operations, serial_number=None):
    """Получение текста для вывода информации о последних 10 операциях"""
    if serial_number:
        operation = operations[0]

        seconds = operation.get("seconds")
        date = operation.get('date')

        if operation.get('start') is None:
            return f'{serial_number}. ✋ Добавлено вручную {get_time_in_str_text(seconds)}\n' \
                   f'Дата: {date}\n\n'

        else:
            return f'{serial_number}. ⏱ Добавлено через таймер {get_time_in_str_text(operation.get("seconds"))}\n' \
                   f'Дата: {operation.get("end")}\n\n'

    text = 'Все операции этой категории:\n\n'
    for counter, operation in enumerate(operations[-10:], start=1):

        seconds = operation.get("seconds")
        date = operation.get('date')

        if seconds is None:
            continue

        if operation.get('start') is None:
            text += f'{counter}. ✋ Добавлено вручную {get_time_in_str_text(seconds)}\n' \
                    f'Дата: {date}\n\n'

        else:
            text += f'{counter}. ⏱ Добавлено через таймер {get_time_in_str_text(operation.get("seconds"))}\n' \
                    f'Дата: {operation.get("end")}\n\n'

    return text
