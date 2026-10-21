import random
import string


def random_name(length: int = 8) -> str:
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))
