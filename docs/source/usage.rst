Usage Guide
===========

Installation
------------

.. code-block:: bash

   uv pip install pycrockford_msgspec

Quick Start
-----------

.. code-block:: python

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
