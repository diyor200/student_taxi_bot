from datetime import datetime, timedelta


def get_user_link(username, telegram_id) -> str:
    if username:
        # Link to the user by username
        return f"https://t.me/{username}"
    else:
        # Link to the user by user ID
        return f"tg://user?id={telegram_id}"


def get_route_date_range() -> list:
    return [datetime.now(), datetime.now() + timedelta(days=2)]
