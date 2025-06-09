# pyright: reportMissingImports=false, reportAttributeAccessIssue=false
import uuid

from _pycrockford_rs_bindings import (
    encode_crockford_py,
    decode_crockford_py,
    CrockfordUUID,
)  # type: ignore[attr-defined]


def test_round_trip() -> None:
    raw = bytes(range(16))
    encoded = encode_crockford_py(raw)
    decoded = decode_crockford_py(encoded)
    assert decoded == raw


def test_crockforduuid_construction_and_equality() -> None:
    raw = bytes(range(16))
    uuid_obj = uuid.UUID(bytes=raw)

    by_str = CrockfordUUID(encode_crockford_py(raw))
    by_bytes = CrockfordUUID(raw)
    by_uuid = CrockfordUUID(uuid_obj)

    assert by_str.bytes == raw
    assert by_bytes.bytes == raw
    assert by_uuid.bytes == raw
    assert by_str == by_bytes == by_uuid
    assert isinstance(by_uuid.uuid, uuid.UUID)
