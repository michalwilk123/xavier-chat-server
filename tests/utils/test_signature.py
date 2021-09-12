import time

import pytest

from app.models.crypto import (
    FakeJWT,
    SignatureError,
    hash_signature,
    validate_signature,
)
from tests.conftest import TEST_SECRET


def test_checksum_validation():
    signature = FakeJWT(expiration_time=100, creation=int(time.time()))

    with pytest.raises(SignatureError):
        validate_signature(signature, "bad secret")

    signature.checksum = "not valid checksum"

    assert validate_signature(signature, TEST_SECRET) is False, (
        "The check sum is not valid. Therefore the validation "
        "should be unsuccessful"
    )

    signature.checksum = hash_signature(signature, TEST_SECRET)

    assert validate_signature(
        signature, TEST_SECRET
    ), "Method provided with the correct check sum. Should be successful"
