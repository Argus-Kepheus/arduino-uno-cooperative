#include <Arduino.h>

typedef void (*TaskCallback)();
struct Task { TaskCallback cb; uint16_t next; uint16_t period; };

uint8_t maskState = 0;
void toggleLed(uint8_t i) {
  const uint8_t m = (uint8_t)(1U << i);
  maskState ^= m;
  digitalWrite((uint8_t)(2 + i), (maskState & m) ? HIGH : LOW);
}
void t1(){toggleLed(0);} void t2(){toggleLed(1);} void t3(){toggleLed(2);}
void t4(){toggleLed(3);} void t5(){toggleLed(4);} void t6(){toggleLed(5);}

Task tasks[6];
TaskCallback callbacks[6] = {t1,t2,t3,t4,t5,t6};

void setup() {
  Serial.begin(115200);
  for (uint8_t i=0;i<6;++i) {
    pinMode((uint8_t)(2+i), OUTPUT);
    tasks[i] = {callbacks[i], (uint16_t)millis(), 500};
  }
  Serial.println(F("TEST 09: six independent native tasks"));
}

void loop() {
  for (uint8_t i=0;i<6;++i) {
    const uint16_t now=(uint16_t)millis();
    if ((int16_t)(now-tasks[i].next) >= 0) {
      const uint16_t scheduled=tasks[i].next;
      tasks[i].cb();
      tasks[i].next=(uint16_t)(scheduled+tasks[i].period);
    }
  }
}
