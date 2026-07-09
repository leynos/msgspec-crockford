# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportArgumentType=false
"""Crockford Base32 UUID type backed by the Rust bindings."""

from __future__ import annotations

import typing as typ
import uuid as py_uuid

from _pycrockford_rs_bindings import decode_crockford, encode_crockford

from .exceptions import CrockfordUUIDError


class CrockfordUUID(py_uuid.UUID):
    """UUID stored as Crockford Base32 when stringified."""

    _expected_length: typ.ClassVar[int] = 16

    def __new__(cls, value: str | bytes | py_uuid.UUID) -> CrockfordUUID:
        """Create an instance from a Crockford string, bytes, or UUID."""
        if isinstance(value, py_uuid.UUID):
            bytes_value = value.bytes
        elif isinstance(value, (bytes, bytearray)):
            if len(value) != cls._expected_length:
                raise CrockfordUUIDError.invalid_length(
                    cls._expected_length, len(value)
                )
            bytes_value = bytes(value)
        elif isinstance(value, str):
            try:
                bytes_value = decode_crockford(value)
            except ValueError as exc:
                raise CrockfordUUIDError(str(exc)) from exc
        else:
            raise CrockfordUUIDError.unsupported_value()
        obj = object.__new__(cls)
        py_uuid.UUID.__init__(obj, bytes=bytes_value)
        return obj

    def __init__(self, value: str | bytes | py_uuid.UUID) -> None:
        """Accept the constructor value; state is populated in `__new__`."""

    @classmethod
    def generate_v4(cls) -> CrockfordUUID:
        """Generate a random (version 4) Crockford UUID."""
        return cls(py_uuid.uuid4())

    @classmethod
    def generate_v7(cls) -> CrockfordUUID:
        """Generate a time-ordered (version 7) Crockford UUID."""
        if not hasattr(py_uuid, "uuid7"):
            raise NotImplementedError("uuid.uuid7 is not available")
        return cls(py_uuid.uuid7())  # pyright: ignore[reportAttributeAccessIssue]

    @property
    def uuid(self) -> py_uuid.UUID:
        """A plain `uuid.UUID` view of this identifier."""
        return py_uuid.UUID(bytes=self.bytes)

    def __str__(self) -> str:
        """Render the identifier as Crockford Base32."""
        return encode_crockford(self.bytes)

    def __repr__(self) -> str:
        """Render a constructor-style representation."""
        return f"CrockfordUUID('{self}')"
