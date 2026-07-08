# pyright: reportMissingImports=false, reportGeneralTypeIssues=false, reportArgumentType=false
"""Unit tests for the `CrockfordUUID` type."""

from __future__ import annotations

import uuid

import pytest

from msgspec_crockford import CrockfordUUID, CrockfordUUIDError


def test_str_round_trip() -> None:
    """A stringified identifier reconstructs an equal instance."""
    cuuid = CrockfordUUID.generate_v4()
    assert CrockfordUUID(str(cuuid)) == cuuid


def test_uuid_property_returns_uuid() -> None:
    """The `uuid` property exposes an equivalent plain `uuid.UUID`."""
    cuuid = CrockfordUUID.generate_v4()
    assert isinstance(cuuid.uuid, uuid.UUID)
    assert cuuid.uuid.bytes == cuuid.bytes


def test_invalid_bytes_length() -> None:
    """A byte payload that is not 16 bytes long is rejected."""
    with pytest.raises(CrockfordUUIDError, match="expected 16 bytes"):
        CrockfordUUID(b"short")


def test_invalid_string_input() -> None:
    """A malformed Crockford string is rejected."""
    with pytest.raises(CrockfordUUIDError):
        CrockfordUUID("invalid")


def test_invalid_type_input() -> None:
    """A value of an unsupported type is rejected."""
    with pytest.raises(CrockfordUUIDError, match="expected Crockford string"):
        CrockfordUUID(123)  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]


def test_generate_v7_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    """`generate_v7` raises when `uuid.uuid7` is unavailable."""
    monkeypatch.delattr(uuid, "uuid7", raising=False)
    with pytest.raises(NotImplementedError):
        CrockfordUUID.generate_v7()
