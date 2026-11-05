# Module 4 Software Design

**STRATA - Digital Twin & Analytics**
**Owners:** Semih Çakır and Enes Taha Kılıç
**Course:** CENG 396, Group 5; instructor Erkan Zergeroğlu
**Date:** 5 November 2026
**Status:** proposed design, not completed implementation.

## 1. Purpose and boundary

Represent the measured one-axis response of the base and three-floor building in
a live interface. Combine camera displacement, IMU acceleration and actuator
status without confusing measured quantities, display interpolation and optional
model predictions. Provide synchronized plots, recorded trials and reproducible
summary metrics.

M1 controls the motor locally. M2 owns IMU acquisition/calibration. M3 owns camera
calibration and marker tracking. M4 consumes their output; it never sends a motor
command or makes a safety decision for M1. Local mock/replay must allow development
while physical modules are unavailable.

## 2. Inputs and deliverables

- **M1:** time-stamped actuator status, upper-stage relative displacement,
  control state and limit/fault flags. Base position may be available but must be
  explicitly agreed, including its reference frame.
- **M2:** calibrated acceleration in m/s², sensor identity/location, time and health.
- **M3:** base/floor signed X displacement in mm, frame/trial identity, quality,
  validity and tracking events, following its proposed record format.
- **Development:** clearly labelled synthetic or recorded data, plus trial metadata.
- **Outputs:** measured structural view; displacement and acceleration charts;
  stream/quality indicators; per-trial peak/RMS; comparable OFF/ON reports and exports.

Do not assume that IMUs are installed on every floor. The interface lists only
configured sensors. Do not derive displacement by double-integrating IMU data in
the initial scope. Do not infer stage position from a floor marker.

## 3. Proposed software components

These are function responsibilities, not implemented function names. The included
replay CLI is the only runnable utility in this planning package.

| ID / function | Input | Output and required behavior |
|---|---|---|
| F01 `load_config` | Configuration file | Validate stream identities, units, quality/time policies, view scale and recording paths; reject invalid configuration before a trial |
| F02 `load_trial_metadata` | Trial setup and source metadata | Trial identity, sensor placement, control mode, source type, units/reference frames and clock maps; preserve provenance |
| F03 `open_sources` | Live/mock/replay settings | Independent source handles; a missing source must not stop unrelated streams |
| F04 `read_source_record` | Source handle | Complete source record or diagnostic; bound buffers, reject malformed/truncated lines and cap record size |
| F05 `validate_source_record` | Raw record, adapter version | Typed valid record or rejection reason; reject non-finite values and invalid identity/units |
| F06 `normalize_record` | Valid M1/M2/M3 record, configuration | Internal samples with source/trial/channel identity, units, reference frame, validity and original time; retain original raw record separately |
| F07 `map_time` | Source time, approved clock mapping | Trial time and mapping provenance; if unavailable, mark stream unsynchronized and do not combine it numerically with others |
| F08 `update_stream_health` | Arrival time, sequence and status | Waiting/live/stale/disconnected and measurement quality; configurable thresholds; distinguish connection from measurement validity |
| F09 `buffer_samples` | Mapped sample | Bounded per-channel buffer, sequence deduplication and late-record policy; record gaps/overruns |
| F10 `build_view_state` | Recent valid samples, health | Base/floor positions and stage state with age/quality; never replace missing displacement with zero |
| F11 `render_structure` | View state and display scale | One-axis measured 2D structure view; optional visual exaggeration clearly labelled; invalid/stale floors visibly unavailable |
| F12 `update_plots` | Buffered samples and time window | mm and m/s² charts on a shared trial-time axis; gaps for unavailable samples; bounded refresh frequency |
| F13 `start_trial` | Setup and output directory | Unique trial directory and immutable starting metadata; refuse overwrite and mixed live/synthetic sources |
| F14 `record_sample` | Raw record, normalized samples and diagnostics | Append JSONL with origin and validity; failure marks recording incomplete and is visible to operator |
| F15 `compute_metrics` | Channel, valid samples, selected interval and gap policy | Peak absolute value, time-weighted RMS, coverage and exclusions; no metric when evidence is insufficient |
| F16 `compare_trials` | OFF and ON summaries plus metadata | Side-by-side results and qualified percentage changes; flag incomparable inputs, missing mode, mixed provenance or insufficient coverage |
| F17 `export_trial` | Trial records, metadata and metrics | CSV measurements, JSON metadata/summary and human-readable report; retain units, nulls, mode and source labels |
| F18 `close_trial` | Source/recording handles and stop reason | Idempotent cleanup, completion status and diagnostics; preserve the original failure |
| F19 `run_dashboard` | Config and operator actions | Orchestrate independent input, recording and rendering; UI/render stalls do not block producers; always close resources |

## 4. Live digital twin behavior

The initial twin is a measurement-driven front view of the fixed table, shaken
base, optional motor stage, and three floors. Floor movement comes from M3; IMUs
provide acceleration traces and sensor indicators. The schematic is not a finite
element model or an earthquake predictor.

Render M3 displacement relative to the fixed support and initial zero, as proposed
by M3. M1 stage displacement is relative to the moving base. Show it separately
unless base position and a valid common time/reference map permit
`stage_absolute = base_absolute + stage_relative`. Geometry heights are display
configuration, not inferred from the sensor stream.

Use newest valid samples within the freshness threshold. A grey last-known outline
may remain for context, labelled with its age, but must not look like a current
measurement. Optional interpolation is limited to display between valid points
within a configured short gap; never use interpolated display values for metrics.
Do not interpolate across loss, reconnect, clock reset or mode/trial boundaries.

Measured values and optional future model predictions must have different labels
and visual styles. Predictions are outside the first deliverable.

## 5. Timing, data integrity and failure handling

Retain original source timestamps, source sequence/frame IDs, arrival timestamps
and clock-map identity. M3 `t_ms` is local elapsed time, so receiving several streams
does not make them synchronized. Use an agreed shared host clock or an explicitly
calibrated mapping into trial time. Arrival-only alignment is approximate and must
be labelled; it is not suitable for cross-source phase claims.

Deduplicate by `(source, trial_id, sequence, channel)` internally. M3 frame_id is
its sequence. Keep late records in the raw log; do not rewind the live view. Offline
recomputation may sort accepted samples and document its policy. A source clock
reset requires a new mapping/segment, never silent timestamp repair.

Bound queues, plot windows and line lengths. Buffer overflow drops oldest display
items with a visible counter; logging has a separate bounded path. A recording
failure must show an incomplete trial even if visualization continues. Validate
confidence/health, not only network connectivity. CV reference loss invalidates
all CV displacements; a missing target invalidates that target alone.

## 6. Metrics and OFF/ON comparison

For a selected channel/window, `peak = max(abs(x_i))` over finite, valid samples.
For each eligible adjacent pair with `dt > 0` below a configured maximum gap, use
trapezoidal integration of squared samples:

`RMS = sqrt(sum(0.5 * (x_i² + x_(i+1)²) * dt) / sum(dt))`.

This is time-weighted RMS of the sampled squared signal, without mean removal.
Only pairs whose endpoints are valid contribute. Do not bridge missing values,
source resets or control-mode transitions. Coverage is eligible duration divided
by requested window duration; retain valid/invalid counts, maximum gap, policy
and interval boundaries. With fewer than two eligible samples, no eligible
duration, or coverage below the configured acceptance threshold, RMS is unavailable.
An isolated valid sample can have a peak but cannot establish a reliable trial.

Report displacement and acceleration separately, with units and sensor/channel
identity. Split trials or analysis windows at control-mode changes. For comparable
OFF and ON windows, `reduction_pct = 100 * (OFF - ON) / OFF`; report unavailable
when OFF is zero or below an agreed noise threshold. Negative values indicate
increased response, not a calculation error.

Manual shaking will differ between runs. Display base-input measurements and
window durations alongside response metrics. Equal duration alone does not imply
comparable disturbance. Automatic comparability tolerances and minimum coverage
remain group decisions; never label a result successful merely from a lower roof
peak. Synthetic and real trials cannot be compared as physical evidence.

## 7. Trial storage proposal

Runtime data should be written to a configurable folder outside the source tree:

```text
trial_<id>/
  metadata.json          # setup, source versions, sensor map, clock maps, policy
  raw/<source>.jsonl     # received records with receipt timestamps
  measurements.jsonl   # normalized samples, nulls and original source time
  events.jsonl         # tracking, source health, clock/mode and logging events
  summary.json         # completion, coverage and metrics
  measurements.csv     # optional export with explicit units/validity
  report.html          # proposed human-readable export
```

Create a unique directory and never overwrite an earlier trial. The exact runtime
metadata schema and report layout will be specified during implementation; the
included internal sample schema is not a finalized trial-storage specification.

## 8. Delivery phases and open decisions

1. **Planning baseline:** this document, diagrams, interfaces, fixtures and test plan.
2. **Independent demo target (4 December):** replay/mock ingestion, live measured
   view, plots, quality indicators, recording and analytically checked metrics.
3. **Integration:** real adapters, verified clock mapping, sensor placement and
   transport agreed with each producer; document measured performance.
4. **Final target (30 December):** integrated OFF/ON trials, exports and user guide.

Owners collaborate on M4; no unconfirmed division of work between them is assumed.
Agree frontend framework, deployment mode, refresh/latency targets, freshness/gap
thresholds, coverage/comparability policies and time/transport contracts before
claiming integration readiness. See the interface decision table and test plan.

## 9. Reference baseline

- Repository README, STRATA architecture and milestones.
- `docs/Physical Stabilization & Control/Physical_Stabilization_and_Control.pdf`:
  M1-local control and timestamped outputs to M4.
- `docs/Computer Vision & Tracking/Strata_Module3_Documentation.pdf`:
  proposed CV record, validity, JSONL/TCP and timing rules.
- `docs/Presentation_Group5.pdf`: original project proposal; this is not a replacement.

Reviewed against repository commit `a2a6a167e92f5e03a06b82f9e41210aad1ab35a9`.
