#include <Arduino.h>

#include "project_config.h"
#include "avr_contracts.h"
#include "avr_fast_io.h"
#include "cooperative_scheduler.h"
#include "button_debounce.h"
#include "metrics.h"
#include "display_activity.h"
#include "oled_status.h"
#include "tft_dashboard.h"


CooperativeScheduler scheduler;
MetricsSampler metricsSampler;

MetricsSnapshot metricsSnapshot = {0, 0, 0, 0, 0, 0, 0};
MetricsSnapshot displaySnapshot = {0, 0, 0, 0, 0, 0, 0};

DebouncedButton mainButton;
DebouncedButton decreaseIntervalButton;
DebouncedButton increaseIntervalButton;

OledStatus oledStatus;
TftDashboard tftDashboard;


// The first six scheduler slots are intentionally reserved for the six
// independent blue-LED tasks. This avoids a separate six-byte ID table.
static const uint8_t BLUE_TASK_FIRST_ID =
    AvrContracts::BLUE_TASK_FIRST_ID;
static const uint8_t BLUE_TASK_COUNT =
    AvrContracts::BLUE_TASK_COUNT;


uint8_t blinkIntervalIndex =
    Config::BLINK_INTERVAL_INITIAL_INDEX;

bool mainButtonPressed = false;
bool oledAvailable = false;


// Display pipeline state.
uint8_t metricsRevision = 0;
uint8_t displayedRevision = 0;
uint8_t displayTargetRevision = 0;
uint8_t displayStage = 0;
bool displayCycleActive = false;


// -----------------------------------------------------------------------------
// Blue LEDs
// -----------------------------------------------------------------------------

void toggleBlueLed(uint8_t index) {

  AvrFastIo::toggleBlueLed(index);
}


void blinkLed1() { toggleBlueLed(0); }
void blinkLed2() { toggleBlueLed(1); }
void blinkLed3() { toggleBlueLed(2); }
void blinkLed4() { toggleBlueLed(3); }
void blinkLed5() { toggleBlueLed(4); }
void blinkLed6() { toggleBlueLed(5); }


// -----------------------------------------------------------------------------
// Shared blink interval
// -----------------------------------------------------------------------------

uint16_t currentBlinkIntervalMs() {

  return
      (uint16_t)(
          Config::BLINK_INTERVAL_BASE_MS
          << blinkIntervalIndex);
}


void setBlinkIntervalIndex(
    uint8_t newIndex) {

  if (
      newIndex >= Config::BLINK_INTERVAL_COUNT ||
      newIndex == blinkIntervalIndex) {

    return;
  }


  blinkIntervalIndex =
      newIndex;


  const uint16_t newPeriod =
      currentBlinkIntervalMs();


  for (
      uint8_t i = 0;
      i < BLUE_TASK_COUNT;
      ++i) {

    scheduler.setPeriodPreservePhase(
        (uint8_t)(BLUE_TASK_FIRST_ID + i),
        newPeriod);
  }


  tftDashboard.log(
      TftDashboard::EVENT_INTERVAL_CHANGED,
      (int16_t)newPeriod);
}


// -----------------------------------------------------------------------------
// Buttons
// -----------------------------------------------------------------------------

void scanButtons() {

  const uint16_t now =
      (uint16_t)millis();


  bool mainRaw;
  bool decreaseRaw;
  bool increaseRaw;


  AvrFastIo::sampleButtons(
      mainRaw,
      decreaseRaw,
      increaseRaw);


  // Main button ---------------------------------------------------------------

  const DebouncedButton::Event mainEvent =
      mainButton.poll(now, mainRaw);


  if (
      mainEvent ==
      DebouncedButton::PRESSED) {

    mainButtonPressed =
        true;


    digitalWrite(
        Config::GREEN_LED_PIN,
        HIGH);


    tftDashboard.log(
        TftDashboard::EVENT_BUTTON_PRESSED);
  }

  else if (
      mainEvent ==
      DebouncedButton::RELEASED) {

    mainButtonPressed =
        false;


    digitalWrite(
        Config::GREEN_LED_PIN,
        LOW);


    tftDashboard.log(
        TftDashboard::EVENT_BUTTON_RELEASED);
  }


  // Decrease interval ---------------------------------------------------------

  const DebouncedButton::Event decreaseEvent =
      decreaseIntervalButton.poll(now, decreaseRaw);


  if (
      decreaseEvent ==
          DebouncedButton::PRESSED &&
      blinkIntervalIndex > 0) {

    setBlinkIntervalIndex(
        blinkIntervalIndex - 1);
  }


  // Increase interval ---------------------------------------------------------

  const DebouncedButton::Event increaseEvent =
      increaseIntervalButton.poll(now, increaseRaw);


  if (
      increaseEvent ==
          DebouncedButton::PRESSED &&
      blinkIntervalIndex + 1 <
          Config::BLINK_INTERVAL_COUNT) {

    setBlinkIntervalIndex(
        blinkIntervalIndex + 1);
  }
}


// -----------------------------------------------------------------------------
// Metrics
// -----------------------------------------------------------------------------

void sampleMetrics() {

  metricsSampler.sample(
      scheduler,
      metricsSnapshot);


  ++metricsRevision;
}


// -----------------------------------------------------------------------------
// Incremental display service
// -----------------------------------------------------------------------------

void serviceDisplays() {

  /*
   * Start one coherent display cycle from an immutable metrics snapshot.
   *
   * If sampleMetrics() executes while the six display stages are being
   * processed, that newer snapshot waits until the current cycle finishes.
   */

  if (
      !displayCycleActive &&
      displayedRevision != metricsRevision) {

    displaySnapshot =
        metricsSnapshot;


    displayTargetRevision =
        metricsRevision;


    displayStage =
        0;


    displayCycleActive =
        true;
  }


  if (displayCycleActive) {

    switch (displayStage) {


      // TFT graph: APP BUSY
      case 0:

        tftDashboard.updateBusyGraph(
            displaySnapshot.appBusyPercent);

        break;


      // TFT graph: free SRAM
      case 1:

        tftDashboard.updateRamGraph(
            displaySnapshot.freeRamBytes);

        break;


      // TFT row: interval, button, APP BUSY
      case 2:

        tftDashboard.updateStatusRow(
            displaySnapshot,
            currentBlinkIntervalMs(),
            mainButtonPressed);

        break;


      // TFT row: SRAM, passes/s, max callback
      case 3:

        tftDashboard.updateResourceRow(
            displaySnapshot);

        break;


      // TFT row: lateness, overruns, minimum sampled SRAM
      case 4:

        tftDashboard.updateTimingRow(
            displaySnapshot);

        break;


      // Compact OLED diagnostic panel
      case 5:

        if (oledAvailable) {

          oledStatus.refreshIfDue(
              displaySnapshot,
              currentBlinkIntervalMs(),
              millis());
        }

        break;
    }


    ++displayStage;


    if (displayStage >= 6) {

      displayedRevision =
          displayTargetRevision;


      displayCycleActive =
          false;
    }


    return;
  }


  /*
   * When no metric-display cycle is pending, render at most one event.
   * This prevents the visual console from monopolizing one scheduler pass.
   */

  tftDashboard.renderNextEvent();
}


// -----------------------------------------------------------------------------
// Serial status
// -----------------------------------------------------------------------------

void printStatus() {

  Serial.print(
      F("APP BUSY: "));

  Serial.print(
      metricsSnapshot.appBusyPercent);


  Serial.print(
      F("% | SRAM: "));

  Serial.print(
      metricsSnapshot.freeRamBytes);


  Serial.print(
      F(" B | LOW: "));

  Serial.print(
      metricsSnapshot.minFreeRamBytes);


  Serial.print(
      F(" B | PASS: "));

  Serial.print(
      metricsSnapshot.passesPerSecond);


  Serial.print(
      F("/s | MAX CALLBACK: "));

  Serial.print(
      metricsSnapshot.maxCallbackUs);


  Serial.print(
      F(" us | MAX LATE: "));

  Serial.print(
      metricsSnapshot.maxLateMs);


  Serial.print(
      F(" ms | OVR: "));

  Serial.print(
      metricsSnapshot.overruns);


  Serial.print(
      F(" | INTERVAL: "));

  Serial.print(
      currentBlinkIntervalMs());


  Serial.println(
      F(" ms"));
}


// -----------------------------------------------------------------------------
// Scheduler heartbeat
// -----------------------------------------------------------------------------

void schedulerHeartbeat() {

  AvrFastIo::toggleSchedulerHeartbeat();
}


// -----------------------------------------------------------------------------
// Hardware setup
// -----------------------------------------------------------------------------

void configureOutputs() {

  for (
      uint8_t i = 0;
      i < Config::BLUE_LED_COUNT;
      ++i) {

    const uint8_t pin =
        (uint8_t)(
            Config::BLUE_LED_FIRST_PIN + i);


    pinMode(
        pin,
        OUTPUT);


    digitalWrite(
        pin,
        LOW);
  }


  pinMode(
      Config::GREEN_LED_PIN,
      OUTPUT);


  digitalWrite(
      Config::GREEN_LED_PIN,
      LOW);


  pinMode(
      Config::SCHEDULER_HEARTBEAT_LED_PIN,
      OUTPUT);


  digitalWrite(
      Config::SCHEDULER_HEARTBEAT_LED_PIN,
      LOW);


  /*
   * D12 is configured later by DisplayActivity::begin().
   *
   * This revision uses software SPI for the TFT, so D12 is never captured
   * by the ATmega328P hardware-SPI peripheral.
   */
}


// -----------------------------------------------------------------------------
// Task registration
// -----------------------------------------------------------------------------

void registerTasks() {

  const uint16_t blinkPeriod =
      currentBlinkIntervalMs();


  /*
   * IMPORTANT:
   * These must remain the first six scheduler registrations. Their numeric
   * IDs are intentionally used by setBlinkIntervalIndex().
   */

  scheduler.add(
      blinkLed1,
      blinkPeriod,
      0);

  scheduler.add(
      blinkLed2,
      blinkPeriod,
      0);

  scheduler.add(
      blinkLed3,
      blinkPeriod,
      0);

  scheduler.add(
      blinkLed4,
      blinkPeriod,
      0);

  scheduler.add(
      blinkLed5,
      blinkPeriod,
      0);

  scheduler.add(
      blinkLed6,
      blinkPeriod,
      0);


  scheduler.add(
      scanButtons,
      Config::BUTTON_SCAN_PERIOD_MS,
      0);


  scheduler.add(
      sampleMetrics,
      Config::METRICS_SAMPLE_PERIOD_MS,
      Config::METRICS_SAMPLE_PERIOD_MS);


  scheduler.add(
      serviceDisplays,
      Config::DISPLAY_SERVICE_PERIOD_MS,
      Config::DISPLAY_SERVICE_PERIOD_MS);


  scheduler.add(
      printStatus,
      Config::SERIAL_STATUS_PERIOD_MS,
      Config::SERIAL_STATUS_PERIOD_MS);


  scheduler.add(
      schedulerHeartbeat,
      Config::SCHEDULER_HEARTBEAT_PERIOD_MS,
      0);
}


// -----------------------------------------------------------------------------
// Arduino setup / loop
// -----------------------------------------------------------------------------

void setup() {

  Serial.begin(
      Config::SERIAL_BAUD);


  configureOutputs();


  // Buttons -------------------------------------------------------------------

  mainButton.begin(
      Config::MAIN_BUTTON_PIN,
      (uint8_t)Config::BUTTON_DEBOUNCE_MS);


  decreaseIntervalButton.begin(
      Config::DECREASE_INTERVAL_BUTTON_PIN,
      (uint8_t)Config::BUTTON_DEBOUNCE_MS);


  increaseIntervalButton.begin(
      Config::INCREASE_INTERVAL_BUTTON_PIN,
      (uint8_t)Config::BUTTON_DEBOUNCE_MS);


  mainButtonPressed =
      mainButton.isPressed();


  digitalWrite(
      Config::GREEN_LED_PIN,

      mainButtonPressed
          ? HIGH
          : LOW);


  // Main TFT ------------------------------------------------------------------

  /*
   * tftDashboard.begin() also initializes the orange D12 activity LED.
   */

  tftDashboard.begin();


  tftDashboard.log(
      TftDashboard::EVENT_STARTUP);


  // Diagnostic OLED -----------------------------------------------------------

  oledAvailable =
      oledStatus.begin();


  tftDashboard.log(
      oledAvailable
          ? TftDashboard::EVENT_OLED_OK
          : TftDashboard::EVENT_OLED_FAIL);


  // Metrics -------------------------------------------------------------------

  metricsSnapshot.freeRamBytes =
      estimateFreeRamBytes();


  metricsSnapshot.minFreeRamBytes =
      metricsSnapshot.freeRamBytes;


  displaySnapshot =
      metricsSnapshot;


  metricsSampler.begin();


  // Scheduler -----------------------------------------------------------------

  registerTasks();


  tftDashboard.log(
      TftDashboard::EVENT_INTERVAL_CHANGED,
      (int16_t)currentBlinkIntervalMs());


  Serial.print(
      F("Native cooperative tasks registered: "));


  Serial.println(
      scheduler.taskCount());
}


void loop() {

  scheduler.execute();
}