# pyright: reportMissingImports=false, reportAttributeAccessIssue=false
from __future__ import annotations

import msgspec
import pytest

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from msgspec_crockford import CrockfordUUID, cuuid_decoder


class Record(msgspec.Struct):
    id: CrockfordUUID
    name: str


def test_msgspec_roundtrip() -> None:
    record = Record(CrockfordUUID.generate_v4(), "example")
    encoder = msgspec.json.Encoder()
    data = encoder.encode({"id": str(record.id), "name": record.name})
    decoder = msgspec.json.Decoder(type=Record, dec_hook=cuuid_decoder)
    assert decoder.decode(data) == record


def test_msgspec_invalid() -> None:
    dec = msgspec.json.Decoder(type=Record, dec_hook=cuuid_decoder)
    with pytest.raises(msgspec.ValidationError):
        dec.decode(b'{"id":"invalid","name":"x"}')
