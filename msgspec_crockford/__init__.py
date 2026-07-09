# pyright: reportMissingImports=false, reportAttributeAccessIssue=false
"""Crockford Base32 UUID support for the msgspec serialization library."""

from __future__ import annotations

from _pycrockford_rs_bindings import decode_crockford, encode_crockford

from .exceptions import CrockfordUUIDError
from .hooks import cuuid_decoder, cuuid_encoder
from .types import CrockfordUUID

__all__ = [
    "CrockfordUUID",
    "CrockfordUUIDError",
    "cuuid_decoder",
    "cuuid_encoder",
    "decode_crockford",
    "encode_crockford",
]
