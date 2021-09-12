import secrets
from typing import List


def generate_otks(num_of_keys: int) -> List[str]:
    return [secrets.token_urlsafe() for _ in range(num_of_keys)]
