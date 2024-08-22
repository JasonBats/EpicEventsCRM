import bcrypt


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed


def verify_password(hashed_password, user_password):
    print(bcrypt.checkpw(user_password.encode('utf-8'), hashed_password))
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)
