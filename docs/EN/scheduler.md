<!-- doc-id: scheduler -->
<!-- language: EN -->
<!-- content-revision: 2 -->

# Cooperative Scheduler

<!-- section: model -->
## Model

Each task is a `void callback()`. The scheduler checks its release time, invokes
the function, measures duration, and calculates the next release. Tasks have no
private stacks and callbacks do not preempt one another.

<!-- section: compact-descriptor -->
## Compact descriptor

```cpp
struct Task {
    TaskCallback callback;
    TickMs nextRunMs;
    uint16_t periodMs;
};
```

<!-- BEGIN GENERATED: scheduler-summary -->
| Contract | Canonical value |
|---|---|
| Capacity | 11 |
| Tick | uint16_t / 16 bit |
| Modular range | 65536 ms |
| Signed half-range | 32768 ms |
| Longest configured period | 4000 ms |
| Scheduling policy | fixed-rate |
| Missed-release policy | skip missed releases; do not execute catch-up bursts |
<!-- END GENERATED: scheduler-summary -->

<!-- section: modular-clock -->
## 16-bit modular clock

The scheduler uses the lower bits of `millis()` represented by its generated
tick contract. Comparisons use signed modular differences, allowing modular
rollover without stopping the system as long as the half-range rule summarized
above is respected.

<!-- section: fixed-rate -->
## Fixed-rate scheduling

The next release is based on the planned release time rather than callback
completion:

```text
next = scheduled + period
```

This avoids cumulative drift.

<!-- section: overrun-policy -->
## Overrun policy

If callback completion leaves one or more releases in the past, those releases
are skipped, `OVR` is incremented, and scheduling advances to a future release.
No catch-up burst is executed.

<!-- section: period-changes -->
## Period changes

When the blue-LED period changes, the remaining fraction of the current cycle is
scaled to the new period so an intentional speed change is not reported as
artificial lateness.

<!-- section: instrumentation -->
## Instrumentation

The scheduler records callback busy time per window, scheduler passes, maximum
callback duration, maximum lateness, and missed releases.

<!-- section: registration-order -->
## Registration order

<!-- BEGIN GENERATED: registration-order -->
| Task ID | Callback |
|---:|---|
| 0 | blinkLed1 |
| 1 | blinkLed2 |
| 2 | blinkLed3 |
| 3 | blinkLed4 |
| 4 | blinkLed5 |
| 5 | blinkLed6 |
| 6 | scanButtons |
| 7 | sampleMetrics |
| 8 | serviceDisplays |
| 9 | printStatus |
| 10 | schedulerHeartbeat |
<!-- END GENERATED: registration-order -->

The first blue-task range is intentionally arithmetic, avoiding a separate
task-ID table.

<!-- section: callback-rules -->
## Callback rules

Callbacks should return quickly, never call `delay()`, never deliberately busy
wait, and split long operations into cooperative stages.
