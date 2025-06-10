# pyright: reportMissingImports=false, reportAttributeAccessIssue=false
from __future__ import annotations

import msgspec
import pytest

from pycrockford_msgspec import CrockfordUUID, cuuid_decoder, cuuid_encoder


class Sample(msgspec.Struct):
    id: CrockfordUUID
    name: str


def test_encode_decode_round_trip() -> None:
    original = Sample(id=CrockfordUUID.generate_v4(), name="example")
    encoded = msgspec.json.Encoder(enc_hook=cuuid_encoder).encode(original)
    decoded = msgspec.json.Decoder(type=Sample, dec_hook=cuuid_decoder).decode(encoded)
    assert decoded == original


def test_invalid_decode_raises() -> None:
    decoder = msgspec.json.Decoder(type=Sample, dec_hook=cuuid_decoder)
    bad_json = b'{"id":"not-a-cuuid","name":"x"}'
    with pytest.raises(msgspec.ValidationError):
        decoder.decode(bad_json)
