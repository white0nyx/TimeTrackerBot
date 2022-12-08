from tgbot.misc.work_with_json import get_user_from_json_db


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
