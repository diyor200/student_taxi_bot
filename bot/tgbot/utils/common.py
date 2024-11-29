def get_user_link(username, c) -> str:
    if username:
        # Link to the user by username
        return f"https://t.me/{username}"
    else:
        # Link to the user by user ID
        return f"tg://user?id={telegram_id}"
