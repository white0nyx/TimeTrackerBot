from datetime import datetime


def get_day_of_week(call):
    days = ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')

    return days[datetime.weekday(call.message.date)]
