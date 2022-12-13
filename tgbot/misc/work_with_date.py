from datetime import datetime


def get_day_of_week(call):
    """Получение дня недели по нажатию на кнопку"""
    days = ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')

    return days[datetime.weekday(call.message.date)]
