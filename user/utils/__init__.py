import math


def is_password_hash(password):
        if len(password) == 88 and "$" in password:
        # Длина пароля совпадает с длиной хеша пароля и он имеет префикс "pbkdf2_"
        # и имеет разделитель "$" внутри строки, что указывает на то что это salted hash
            return True
        else:
        # Проверяем, является ли строка паролем
            return False