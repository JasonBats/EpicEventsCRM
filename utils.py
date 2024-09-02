from datetime import datetime

import bcrypt
import re


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed


def verify_password(password, user_password):
    user_password_bytes = password.encode('utf-8')
    access = bcrypt.checkpw(user_password_bytes, user_password)
    return access


def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


def validate_phone_number(phone_number):
    return phone_number.isnumeric()


def validate_total_amount(amount):
    return amount.isnumeric()


def validate_amount_due(total_amount, amount_due):
    if amount_due.isnumeric():
        return amount_due <= total_amount
    else:
        return False


def validate_date(date):
    if not re.match(r"\d{4}-\d{2}-\d{2}", date):
        return False

    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_end_date(event_date_start, event_date_end):
    if not re.match(r"\d{4}-\d{2}-\d{2}", event_date_end):
        return False

    try:
        end = datetime.strptime(event_date_end, "%Y-%m-%d")
        start = datetime.strptime(event_date_start, "%Y-%m-%d")
        return end >= start
    except ValueError:
        return False
