# pyright: reportMissingImports=false, reportAttributeAccessIssue=false
from __future__ import annotations

from typing import Any, Type

import msgspec

from _pycrockford_rs_bindings import CrockfordUUID


def cuuid_decoder(type_hint: Type[Any], obj: Any) -> CrockfordUUID:
    """Decode CrockfordUUID strings for msgspec."""
    if type_hint is CrockfordUUID:
        if isinstance(obj, str):
            try:
                return CrockfordUUID(obj)
            except Exception as exc:  # PyO3 raises PyValueError
                raise msgspec.ValidationError(str(exc)) from exc
        raise msgspec.ValidationError(
            f"Expected str for CrockfordUUID, got {type(obj).__name__}"
        )
    return NotImplemented


def cuuid_encoder(obj: Any) -> str:
    """Encode CrockfordUUID instances for msgspec."""
    if isinstance(obj, CrockfordUUID):
        return str(obj)
    return NotImplemented
