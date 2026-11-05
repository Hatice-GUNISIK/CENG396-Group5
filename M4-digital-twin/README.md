# Module 4 - Digital Twin & Analytics

**Owners:** Semih Çakır and Enes Taha Kılıç
**Status:** design and synthetic integration fixtures; no live dashboard yet.
**Design baseline:** 5 November 2026.

Module 4 receives measurements and control status, aligns their time references,
updates a measurement-driven structural visualization, and presents plots and trial
metrics. It does not read raw camera images, calibrate IMUs, or close the motor loop.

## Planning package

- [Software design](../docs/Digital%20Twin%20%26%20Analytics/Module4_Software_Design.md)
- [Input/output and architecture diagrams](../docs/Digital%20Twin%20%26%20Analytics/Architecture.md)
- [Data interfaces and unresolved integration decisions](../docs/Digital%20Twin%20%26%20Analytics/Data_Interfaces.md)
- [Independent verification plan](../docs/Digital%20Twin%20%26%20Analytics/Verification_Plan.md)
- [Internal sample schema](contracts/normalized-sample.schema.json)
- [Synthetic records](examples/README.md)

These files propose the implementation. They do not demonstrate working hardware,
live synchronization, a finished user interface, or achieved measurement accuracy.
The Module 3 PDF is an existing proposal, not a finalized shared contract.

## Inputs and outputs

| Source | Input | Use |
|---|---|---|
| M1 | Stage displacement, timestamp, ON/OFF and limit/fault status | Stage view, control-state labels, trial segmentation |
| M2 | Calibrated acceleration, timestamp, sensor identity and health | Acceleration plots and peak/RMS metrics |
| M3 | BASE and FLOOR_1-3 signed X displacement in mm, timestamp, validity/confidence and events | Measured structural motion and displacement plots |
| Local fixtures | Explicitly synthetic records or recorded trials | Independent development and replay |

Outputs: live structure view, synchronized plots, stream-quality indicators,
per-trial peak/RMS metrics, OFF/ON comparison, and exported data/report files.
The first implementation may use a 2D front view; 3D is optional and does not add
measurement dimensions that the one-axis experiment does not supply.

## Included runnable utility

`tools/replay.py` validates basic fixture ordering and emits a JSONL file to stdout
at its recorded pace. It is a local replay utility, not a network receiver or a
dashboard. Python 3.10+ and the standard library are sufficient.

```sh
python3 M4-digital-twin/tools/replay.py M4-digital-twin/examples/cv_mock.jsonl --speed 2
python3 M4-digital-twin/tools/replay.py M4-digital-twin/examples/normalized_mock.jsonl --no-wait
```

## Proposed implementation order

1. Agree clock mapping, sensor placement, units and transport with M1-M3.
2. Build mock/replay ingestion, normalization and stream-quality states.
3. Add a measured 2D structure view and displacement/acceleration plots.
4. Add trial recording, metrics and OFF/ON comparison with input context.
5. Integrate real streams and execute the verification plan.

Frontend framework, 3D library and deployment mode remain open decisions. Python
is the proposed adapter/replay environment because M3 proposes Python; this does
not require a particular frontend framework or transport.
