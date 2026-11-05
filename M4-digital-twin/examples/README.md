# Synthetic integration fixtures

All records are invented for software development. None are real measurements or
evidence of physical performance. The short 0-500 ms sequence is illustrative,
not a promised sampling rate or an adequate experiment duration.

## cv_mock.jsonl

Six frames shaped like M3's proposed measurement record. `source=cv_mock`,
`timing_basis=synthetic`, trial `m4_mock_01`. Frames 2-4 invalidate FLOOR_3;
the third consecutive invalid frame (4) emits `marker_lost`; frame 5 recovers.
There is no actual camera, TCP connection or metadata handshake in this fixture.

## normalized_mock.jsonl

M4 internal samples corresponding to the same six frames, plus an illustrative
roof-X IMU acceleration channel. The IMU values and placement are fictional and
are not the proposed M2 wire format. Source times have a deliberately exact
identity map `synthetic_identity` because the fixture generator owns both clocks;
this makes no synchronization claim about real hardware.

All samples use `origin=synthetic`. A future recorder replay must keep original
provenance (`origin=replay` and `recorded_origin=synthetic` or `live`); the included
stdout CLI leaves record bytes/fields unchanged, so these stay labelled synthetic.

## example_metadata.json

Fixture-only context: source labels, sign/reference, synthetic clock map and
unconfirmed IMU placement. It is not an approved M3 `trial_meta` packet or the
complete future runtime metadata schema. No M1 status is invented; control mode
is `UNKNOWN`, not OFF. There is no OFF/ON physical comparison in this package.

## Local replay

From the repository root:

```sh
python3 M4-digital-twin/tools/replay.py M4-digital-twin/examples/cv_mock.jsonl
python3 M4-digital-twin/tools/replay.py M4-digital-twin/examples/normalized_mock.jsonl --no-wait
```

The CLI checks JSON objects, finite numbers, nonnegative `t_ms`/`source_t_ms` and
nondecreasing time. It preflights the entire file before emitting records. It does
not validate producer schemas, synchronize clocks, normalize records or implement
a live network adapter. Files must be ordered on one source-time basis, as these
fixtures are; it is not a multiproducer merge tool. Blank lines are ignored.
