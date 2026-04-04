import secrets
import string

ALPHABET = string.ascii_letters + string.digits


def generate_short_code(length):
    return "".join(secrets.choice(ALPHABET) for _ in range(length))
