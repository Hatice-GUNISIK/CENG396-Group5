# Module 4 independent verification plan

Status: planned tests, not passed live-system results. Owners: Semih Çakır and
Enes Taha Kılıç. Baseline: 5 November 2026.

The planning fixtures and replay CLI can be checked now. UI, metrics, recording
and adapter tests below become executable as those components are implemented.
Record software versions, configuration, input fixture, expected output, actual
result and pass/fail evidence for each run. Do not mark a design table as a test log.

| ID | Scenario | Expected behavior / evidence |
|---|---|---|
| V01 | Schema, null, finite values, units | Reject malformed JSON, NaN/Infinity, mismatched quantity/unit and invalid value/null combinations; preserve rejection reason |
| V02 | M3 fixture loss/recovery | FLOOR_3 null at frames 2-4; exactly one marker_lost at frame 4 and recovered at frame 5; no zero substitution |
| V03 | Reference loss | All CV displacements unavailable; do not falsely report every visible target as individually lost |
| V04 | Independent sources | Disconnect M2 while M3 continues; CV view remains active and M2 state becomes unavailable |
| V05 | Clock offset/drift | Align known timestamps using approved map; unmapped samples cannot enter a common plot/analysis as synchronized data |
| V06 | Sequence faults | Duplicate sequence/channel cannot count twice; late samples cannot rewind live view; reset opens a new segment |
| V07 | Visual displacement | Feed known -10, 0, +10 mm; rendered direction and labelled scale match; height does not change |
| V08 | Gaps and stale values | Missing values appear as graph gaps; stale outline is labelled with age; invalid data excluded from metrics |
| V09 | Constant waveform | x=5 mm at t=0,1,2 s: peak=5 mm, time-weighted RMS=5 mm, coverage=100% |
| V10 | Uneven sample times | t=[0,1,3] s, x=[0,2,2] mm: integral=10 mm²s, duration=3 s, RMS=sqrt(10/3) mm; peak=2 mm |
| V11 | Gap-aware coverage | t=[0,1,2,3] s, x=[2,2,null,2] mm; max gap=1.1 s: only [0,1] eligible; coverage=1/3, RMS=2 before coverage gate |
| V12 | No usable interval | Isolated sample, all invalid, or zero-duration window: RMS unavailable; no divide-by-zero or success badge |
| V13 | OFF/ON math | Comparable peaks OFF=10, ON=6: reduction=40%; ON=12: -20%; OFF=0: unavailable |
| V14 | Mode/provenance | UNKNOWN mode is not OFF; split at transitions; synthetic vs measured pair cannot yield a physical-comparison claim |
| V15 | Disturbance comparison | Different base input or duration is surfaced with metadata; do not claim attenuation from roof peak alone |
| V16 | Recording/export | Reopen JSONL/CSV/summary; values, units, nulls, time, provenance and mode preserved; unique directory prevents overwrite |
| V17 | Storage/render failure | Simulate unwritable output and slow UI; trial marked incomplete, source producer unblocked; clean shutdown |
| V18 | Transport faults (if TCP selected) | Split line across packets, oversized input, bad UTF-8, missing metadata and reconnect; bounded memory, complete-line parsing and diagnostics |
| V19 | Buffer load | Measured rate/jitter stress run; bounded buffers and explicit dropped-item counters; record latency percentiles and host specs |
| V20 | Replay equivalence | Same recorded input yields same offline metrics across playback speeds; wall-time pacing cannot change source timestamps |

## Fixtures included now

- `cv_mock.jsonl`: six schema-shaped CV frames, including target loss/recovery.
- `normalized_mock.jsonl`: measured-view displacement and proposed IMU acceleration
  represented in M4's internal schema. All data is synthetic; IMU placement is an
  example, not a confirmed M2 configuration.
- `tools/replay.py`: stdout replay of either fixture with optional time scaling.

These short records exercise integration shape and missing-data behavior, not
sensor accuracy, speed, physical response, or a meaningful OFF/ON comparison.
Later add long constant/sine sequences, invalid-record fixtures, reference loss,
clock resets and disconnected-source cases when the relevant components exist.

## Future evidence to collect

Keep independent-demo results distinct from final integrated results. For each
physical trial preserve source logs, calibration IDs, sensor map, approved clock
map, mode, base input, chosen analysis interval, coverage and software revision.
Agree quantitative rate, latency, noise and comparability criteria before testing;
report actual measured values even when they miss the target.
