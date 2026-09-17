# pycrockford_msgspec

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](
https://deepwiki.com/leynos/msgspec-crockford)

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

### Markdown formatting

`make fmt` and `make check-fmt` run `mdtablefix` (version 0.6.0, the same
release CI installs); install it once with
`cargo install --locked mdtablefix --version 0.6.0`. `make fmt` also runs
`markdownlint-cli2`, which CI provides through its GitHub action; locally
install it with `bun install -g markdownlint-cli2` (or
`npm install -g markdownlint-cli2`). This replaces the previous `mdformat-all`
wrapper.

### Building the documentation

The documentation lives in `docs/` and uses Sphinx. Install Sphinx and run:

```bash
uv pip install sphinx
sphinx-build -M html docs/source docs/_build
```

Generated HTML will appear in `docs/_build/html`. This directory is ignored by
Git and should not be committed.

### Spelling policy

Run `make spelling` after changing Markdown. The target refreshes the shared
`leynos` en-GB-oxendict dictionary only when its published source is newer than
the ignored local cache, regenerates the tracked `typos.toml`, and runs the
pinned `typos` 1.48.0 release. Add narrow repository-only exceptions to
`typos.local.toml`; never edit the generated configuration by hand.
