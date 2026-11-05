# Module 4 data interfaces

**Status: proposed; not the shared contract.** Do not change `shared/` unilaterally.
Baseline: M1/M3 PDFs and README at `a2a6a16`, reviewed 5 November 2026.

## 1. Existing producer proposals

| Producer | Known from current documentation | Still to agree |
|---|---|---|
| M1 | Stage displacement, control state, limit/fault flags and timestamps; motor loop local | Wire fields, units, time origin, absolute/relative reference, transport and rate |
| M2 | Calibrated acceleration, sensor health, timestamps, replayable stream | Actual sensor locations, X-axis mapping, gravity handling, wire schema, clock, rate and transport |
| M3 | Frame record with BASE and FLOOR_1-3; signed mm, confidence, validity, events; JSONL; optional TCP | Transport approval, endpoint, clock mapping and actual rate |

No M2 software design has been uploaded in the reviewed baseline. M4 must not
invent a binding wire format for M1/M2; adapters will follow their agreed outputs.

## 2. M3 proposed input (preserved, not renamed)

M3 proposes one JSON object per processed frame containing:

- `type: measurement`, `schema_version: 1`, `source: cv` (or `cv_mock`).
- `trial_id`, `frame_id`, `t_ms`, `timing_basis`, `status`.
- `markers`: exactly BASE (10), FLOOR_1 (21), FLOOR_2 (22), FLOOR_3 (23).
- Each marker: `name`, `id`, signed `x_mm`, `confidence`, `valid`, `reason`.
- `events` including `marker_lost` and `marker_recovered` transitions.

Invalid displacement is `null`, with `valid=false` and confidence 0. M3 uses
`ok`, `degraded` and `reference_lost` module states. Loss events are delayed until
the configured consecutive-invalid-frame threshold; values become invalid from
the first bad frame. Do not wait for a loss event before displaying a gap.

M3 position is relative to the fixed support and trial zero, not the moving base.
Its proposed live `host_receipt` time is capture-host receipt time, not exposure
time. Local elapsed `t_ms` starts at the first measurement frame.

If TCP is agreed, M3 proposes UTF-8 JSON separated by LF, `trial_meta` before
measurements on each connection, bounded connection/send timeouts, best-effort
delivery and no historical retransmission. Buffer partial bytes until LF, cap
line size and discard incomplete lines on disconnect. Full `trial_meta` wire
fields are not yet specified by that PDF and must be agreed before implementation.

See `M4-digital-twin/examples/cv_mock.jsonl` for a synthetic measurement fixture.
It intentionally contains no invented TCP metadata handshake.

## 3. M4 internal normalized sample

`M4-digital-twin/contracts/normalized-sample.schema.json` describes one internal
numeric sample. It is not a wire-format requirement for another module.

| Field | Meaning |
|---|---|
| `schema_version`, `type` | Version 1, `sample` |
| `source`, `trial_id`, `sequence`, `channel` | Stable identity and deduplication key |
| `origin` | `live`, `synthetic`, or `replay`; replay additionally needs `recorded_origin` |
| `source_t_ms`, `timing_basis` | Original producer time and its declared basis |
| `trial_t_ms`, `clock_map_id`, `synchronized` | Mapped trial time; null time/map when unsynchronized |
| `quantity`, `unit`, `reference_frame` | Explicit measurement meaning, physical units and reference |
| `value`, `valid`, `confidence`, `reason` | Numeric value or null, validity, optional confidence and quality reason |

Quantities: `displacement/mm` or `acceleration/m/s2`. Unit conversions require a
declared adapter and source metadata. Relative stage displacement remains a
separate reference frame. Health and ON/OFF/fault events are retained separately;
they are not encoded as acceleration or fabricated numeric samples.

For CV use a stable adapter source ID and retain `frame_id` as sequence. Map
`markers[].x_mm` to displacement channels, preserve nulls/confidence/reason and
keep events in the event stream. For M1/M2, use configured sensor identities and
approved metadata. Never treat a missing confidence field as an asserted 100%.

Schema validation is necessary but does not establish physical correctness.
Adapters also verify configured channels, provenance, monotonic source sequence,
trial identity, finite numbers, sensor health and valid clock-map applicability.

## 4. Clock and sequence rules

- All streams need an agreed mapping to one trial clock before synchronized use.
- Mapping proposal: `trial_t_ms = scale * source_t_ms + offset_ms`. Preserve
  the clock-map ID, parameters, method and uncertainty in metadata. Offset-only
  mapping is acceptable only when rate agreement/drift has been checked.
- If no mapping is approved, keep `trial_t_ms=null`, `clock_map_id=null` and
  `synchronized=false`. A plausible-looking timestamp is not synchronization.
- Store local monotonic receipt time separately with its host/clock identity.
  It measures freshness but does not replace source capture time.
- Apply deduplication per source/trial/sequence/channel; retain diagnostics.
- Reconnect, timestamp reset, mapping change and control-mode change create
  explicit segments. Do not interpolate or compute RMS across those boundaries.

## 5. Integration decisions to confirm

| Decision | Participants | Required outcome |
|---|---|---|
| Wire schema and metadata handshake | Each producer + M4 | Versioned examples, field meanings and invalid-data rules |
| Transport | Each producer + M4 | TCP/serial/file/other; endpoint and reconnect/backpressure policy |
| Clock mapping | M1-M4 | Clock owners, start/offset method, drift check and uncertainty |
| Sensor placement and sign | M1-M3 + M4 | IDs, locations, axes, reference frames and units |
| Rates and budgets | Each producer + M4 | Measured input rate, expected jitter, UI update/latency targets |
| Data acceptance | M4 + producers | Freshness, maximum analysis gap and minimum coverage thresholds |
| OFF/ON comparability | Whole group | Base-input measures/tolerances, window selection, near-zero baseline policy |
| Trial identity/mode | M1-M4 | Common ID, mode source, transitions and missing-status behavior |

No placeholder threshold in this package is an achieved performance claim.
