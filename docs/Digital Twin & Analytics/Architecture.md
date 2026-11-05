# Module 4 architecture proposal

Status: design only, 5 November 2026. No transport or UI framework is finalized.

## Module input/output boundary

```mermaid
flowchart LR
    M1["M1: actuator position, mode, limits/faults"] --> M4
    M2["M2: calibrated acceleration, identity, health"] --> M4
    M3["M3: base/floor displacement, validity, confidence, events"] --> M4
    DEV["Synthetic fixtures / recorded replay"] --> M4
    META["Trial setup / sensor map / clock mapping"] --> M4
    M4["M4: Digital Twin & Analytics"] --> VIEW["Measured structure view + time plots"]
    M4 --> METRIC["Peak / RMS + qualified OFF/ON comparison"]
    M4 --> LOG["Trial recordings + exports + quality indicators"]
```

M4 is downstream. No edge sends camera or dashboard data into M1's motor loop.

## Internal flow

```mermaid
flowchart TD
    SOURCE["Independent source adapters: live / mock / replay"] --> VALIDATE["Validate source record and preserve raw input"]
    VALIDATE --> NORMAL["Normalize units, channels and reference frame"]
    NORMAL --> CLOCK["Map source clock to trial time"]
    CLOCK --> BUFF["Bounded buffers + source/quality state"]
    CLOCK --> REC["Trial recorder: raw + normalized + events"]
    BUFF --> VIEW["Measured view + plots"]
    REC --> ANALYSIS["Coverage-aware peak/RMS"]
    ANALYSIS --> COMPARE["OFF/ON comparison with base-input context"]
    ANALYSIS --> EXPORT["CSV + JSON + report"]
    COMPARE --> EXPORT
```

Unsynchronized sources can be displayed on clearly labelled local timelines, but
cannot enter synchronized cross-source analysis. Slow rendering must not block
source acquisition. Recording failure is visible and marks the trial incomplete.

## Interface wireframe (proposed)

```text
+---------------------------------------------------------------------+
| STRATA | LIVE / MOCK / REPLAY | Trial ID | ON/OFF/UNKNOWN | Recording |
+------------------------------------+--------------------------------+
| Measured front view                | Displacement vs trial time (mm)|
| fixed reference + base             | BASE, FLOOR_1, FLOOR_2, FLOOR_3 |
| stage if available + 3 floors      +--------------------------------+
| visible quality/age per target     | Acceleration vs time (m/s²)    |
| scale and exaggeration label       | configured sensors only        |
+------------------------------------+--------------------------------+
| M1 status | M2 status | M3 status | clock mapping | loss/fault events |
+---------------------------------------------------------------------+
| Window | Peak | RMS | coverage | OFF/ON trials + base-input context  |
| Start/stop recording | Replay | Export | incomplete-data warnings    |
+---------------------------------------------------------------------+
```

Controls affect M4 recording/replay only. A control-state badge displays the
reported M1 mode; it is not a motor ON/OFF switch.

## Source and measurement state

```mermaid
stateDiagram-v2
    [*] --> Waiting
    Waiting --> Live: accepted record
    Live --> Stale: no fresh record within configured threshold
    Stale --> Live: accepted fresh record
    Live --> Disconnected: source closes
    Stale --> Disconnected: source closes
    Disconnected --> Waiting: reconnect attempt
```

Measurement validity is separate: a live CV connection may deliver invalid
measurements while a marker is occluded. On reconnect, revalidate source metadata
and trial/clock identity before accepting records into the previous segment.
