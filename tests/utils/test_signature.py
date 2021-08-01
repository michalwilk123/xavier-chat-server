from app.models.crypto import (
    SignatureError,
    ZkSnarkNaive,
    hash_signature,
    validate_signature,
)
from tests.conftest import TEST_SECRET
import time
import pytest


def test_checksum_validation():
    signature = ZkSnarkNaive(expiration_time=100, creation=int(time.time()))

    with pytest.raises(SignatureError):
        validate_signature(signature, "bad secret")

    signature.check_sum = "not valid checksum"

    assert validate_signature(signature, TEST_SECRET) is False, (
        "The check sum is not valid. Therefore the validation "
        "should be unsuccessful"
    )

    signature.check_sum = hash_signature(signature, TEST_SECRET)

    assert validate_signature(
        signature, TEST_SECRET
    ), "Method provided with the correct check sum. Should be successful"
