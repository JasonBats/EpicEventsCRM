import bcrypt


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed


def verify_password(password, user_password):
    user_password_bytes = password.encode('utf-8')
    access = bcrypt.checkpw(user_password_bytes, user_password)
    return access
