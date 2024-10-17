import random


def phone_number() -> str:
    return f"{random.randint(0, 999):03d}-{random.randint(0, 999):03d}-{random.randint(0, 9999):04d}"
