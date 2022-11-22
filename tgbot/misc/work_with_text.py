def get_the_time_in_seconds(str_time: str):
    time_parts = str_time.split(':')
    h, m, s = tuple(map(int, time_parts))
    time_in_seconds = h * 3600 + m * 60 + s

    return time_in_seconds


def convert_to_preferred_format(sec):
    sec = sec % (24 * 3600)
    hour = sec // 3600
    sec %= 3600
    minutes = sec // 60
    sec %= 60
    return "%d:%02d:%02d" % (hour, minutes, sec)


def get_statistic(categories):
    text = '📈 Ваша статистика\n\n'

    for category in categories:
        text += f'{category["name"]} - {convert_to_preferred_format(category["seconds"])}\n'

    return text
