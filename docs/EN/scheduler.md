<!-- doc-id: scheduler -->
<!-- language: EN -->
<!-- content-revision: 1 -->

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

Baseline capacity is exactly 11 tasks.

<!-- section: modular-clock -->
## 16-bit modular clock

The scheduler uses the lower 16 bits of `millis()`. Comparisons use signed
modular differences, allowing `65535 -> 0` rollover without stopping the system,
provided intervals remain below 32768 ms and the scheduler is not prevented
from running for such a long interval. The current longest period is 4000 ms.

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

IDs 0 through 5 must be `blinkLed1` ... `blinkLed6`. This avoids storing an
extra six-entry task-ID table.

<!-- section: callback-rules -->
## Callback rules

Callbacks should return quickly, never call `delay()`, never deliberately busy
wait, and split long operations into cooperative stages.
