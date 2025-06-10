# pycrockford_msgspec

A Python extension providing Crockford Base32 UUID support for the
[msgspec](https://jcristharif.com/msgspec/) serialization library. The core
encoding and decoding logic is written in Rust and exposed through PyO3.

## Features

- `CrockfordUUID` type with generation helpers for v4 UUIDs
- `cuuid_encoder` and `cuuid_decoder` hooks for msgspec
- Stable ABI wheels built with `maturin` and the `abi3` feature

## Installation

```bash
uv pip install pycrockford_msgspec
```

## Quick Start

```python
import msgspec
from pycrockford_msgspec import CrockfordUUID, cuuid_encoder, cuuid_decoder

class Event(msgspec.Struct):
    event_id: CrockfordUUID
    payload: dict

encoder = msgspec.json.Encoder(enc_hook=cuuid_encoder)
decoder = msgspec.json.Decoder(type=Event, dec_hook=cuuid_decoder)

event = Event(CrockfordUUID.generate_v4(), {"hello": "world"})
data = encoder.encode(event)
restored = decoder.decode(data)

assert restored == event
```

## Development

Build wheels using `maturin`:

```bash
uv pip install -e .[dev]
maturin build --release
```

Run tests:

```bash
cargo test
pytest -q
```

### Building the documentation

The documentation lives in `docs/` and uses Sphinx. Install Sphinx and run:

```bash
uv pip install sphinx
sphinx-build -M html docs/source docs/_build
```

Generated HTML will appear in `docs/_build/html`. This directory is ignored by
Git and should not be committed.
