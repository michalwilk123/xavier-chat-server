from app.models.crypto import OtkCollection
import secrets
from typing import List, Dict


def generate_otks(num_of_keys: int) -> List[str]:
    return [secrets.token_urlsafe() for _ in range(num_of_keys)]
