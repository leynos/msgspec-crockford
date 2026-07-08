"""Exception types raised by the Crockford UUID integration."""

from __future__ import annotations


class CrockfordUUIDError(ValueError):
    """Error raised for invalid Crockford UUID operations."""

    @classmethod
    def invalid_length(cls, expected: int, actual: int) -> CrockfordUUIDError:
        """Build an error for a byte payload of the wrong length."""
        return cls(f"expected {expected} bytes, got {actual}")

    @classmethod
    def unsupported_value(cls) -> CrockfordUUIDError:
        """Build an error for a value of an unsupported type."""
        return cls("expected Crockford string, 16 bytes, or uuid.UUID")
