import json


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






