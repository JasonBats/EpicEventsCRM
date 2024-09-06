import os
import re
from datetime import datetime, timedelta
from typing import Any, Type

import bcrypt
import jwt

from models import CustomerRepresentative


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed


def verify_password(password, user_password):
    user_password_bytes = password.encode("utf-8")
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


def save_token_in_file(user: Type[CustomerRepresentative]) -> None:
    """
    Encodes and saves token in a file.
    :user
    :param user:
    :return:
    """
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    if JWT_SECRET_KEY is None:
        raise ValueError("JWT_SECRET_KEY environment variabvle is not set")

    expired_date = datetime.today() + timedelta(minutes=5)
    encoded_jwt = jwt.encode(
        {
            "user_id": str(user.id),
            "expired_date": expired_date.strftime("%m/%d/%Y, %H:%M:%S"),
        },
        JWT_SECRET_KEY,
        algorithm="HS256",
    )
    f = open(".credentials", "w+")
    f.write(encoded_jwt)
    f.close()


def check_token_date() -> bool | Any:

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    if JWT_SECRET_KEY is None:
        raise ValueError("JWT_SECRET_KEY environment variabvle is not set")

    if not os.path.isfile(".credentials"):
        return False

    f = open(".credentials", "r")
    encoded_token = f.read()
    decoded_token = jwt.decode(encoded_token, JWT_SECRET_KEY, algorithms=["HS256"])
    if datetime.now() < datetime.strptime(
        decoded_token["expired_date"], "%m/%d/%Y, %H:%M:%S"
    ):
        return decoded_token
    else:
        return False
