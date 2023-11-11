import hashlib
import random
import string


from src.core.config import get_config


settings = get_config()


def generate_code(
    code_length: int,
    is_ascii_lowercase: bool = True,
    is_ascii_uppercase: bool = True,
    is_digits: bool = True,
    is_punctuation: bool = True
) -> str:
    symbol = ''
    if is_ascii_lowercase:
        symbol += string.ascii_lowercase
    if is_ascii_uppercase:
        symbol += string.ascii_uppercase
    if is_digits:
        symbol += string.digits
    if is_punctuation:
        symbol += string.punctuation

    if symbol == '': return ''

    return ''.join([random.choice(symbol) for _ in range(code_length)])


def hash_string(
    password: str
) -> str:
    h = hashlib.new(settings.ALGORITHM)
    h.update(password.encode())
    h.update(settings.SECRET_KEY.encode())
    return h.hexdigest()
