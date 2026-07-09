# pyright: reportMissingImports=false, reportAttributeAccessIssue=false
"""msgspec encode and decode hooks for `CrockfordUUID` values."""

from __future__ import annotations

import typing as typ
from types import NotImplementedType, UnionType

import msgspec

from .exceptions import CrockfordUUIDError
from .types import CrockfordUUID


def _invalid_payload_error(obj: object) -> msgspec.ValidationError:
    """Build a validation error for a non-string CrockfordUUID payload."""
    return msgspec.ValidationError(
        f"Expected str for CrockfordUUID, got {type(obj).__name__}"
    )


def cuuid_decoder(type_hint: object, obj: object) -> CrockfordUUID | NotImplementedType:
    """Decode CrockfordUUID strings for msgspec."""
    origin = typ.get_origin(type_hint)
    args = typ.get_args(type_hint)
    is_crockford_type = type_hint is CrockfordUUID or (
        origin in {typ.Union, UnionType} and CrockfordUUID in args
    )

    if is_crockford_type:
        if obj is None:
            return NotImplemented
        if isinstance(obj, str):
            try:
                return CrockfordUUID(obj)
            except CrockfordUUIDError as exc:
                raise msgspec.ValidationError(str(exc)) from exc
        raise _invalid_payload_error(obj)
    return NotImplemented


def cuuid_encoder(obj: object) -> str | NotImplementedType:
    """Encode CrockfordUUID instances for msgspec."""
    return str(obj) if isinstance(obj, CrockfordUUID) else NotImplemented
