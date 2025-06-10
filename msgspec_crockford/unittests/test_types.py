# pyright: reportMissingImports=false, reportGeneralTypeIssues=false, reportArgumentType=false
from __future__ import annotations

import uuid
import pytest

from msgspec_crockford import CrockfordUUID


def test_str_round_trip() -> None:
    cuuid = CrockfordUUID.generate_v4()
    assert CrockfordUUID(str(cuuid)) == cuuid


def test_uuid_property_returns_uuid() -> None:
    cuuid = CrockfordUUID.generate_v4()
    assert isinstance(cuuid.uuid, uuid.UUID)
    assert cuuid.uuid.bytes == cuuid.bytes


def test_invalid_bytes_length() -> None:
    with pytest.raises(ValueError):
        CrockfordUUID(b"short")
