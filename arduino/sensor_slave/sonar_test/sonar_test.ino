#include <Arduino.h>

const int trigPins[] = {3, 5, 7, 9, 11, 13};
const int echoPins[] = {2, 4, 6, 8, 10, 12};
const int numSensors = 6;

const int minValue = 0;
const int maxValue = 30; // 30cm as max distance for 100%

void setup() {
  Serial.begin(9600);

  for (int i = 0; i < numSensors; i++) {
    pinMode(trigPins[i], OUTPUT);
    pinMode(echoPins[i], INPUT);
  }
}

void loop() {
  int percentValues[numSensors];

  for (int i = 0; i < numSensors; i++) {
    long duration;
    int distance;
    int mappedValue;

    // 1. Trig 핀 초기화 (LOW 상태 유지)
    digitalWrite(trigPins[i], LOW);
    delayMicroseconds(2);

    // 2. 초음파 발사! (10마이크로초 동안 HIGH)
    digitalWrite(trigPins[i], HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPins[i], LOW);

    // 3. Echo 핀으로 돌아오는 펄스 길이 측정 (단위: 마이크로초)
    duration = pulseIn(echoPins[i], HIGH, 30000); // 30ms timeout

    // 4. 거리 계산 (cm 단위)
    // 소리의 속도: 340m/s = 0.034cm/us
    // 왕복 거리이므로 2로 나눔
    // 거리 = 시간 x 속도 / 2
    distance = duration * 0.034 / 2;

    if (duration == 0) {
      mappedValue = 0; // Timeout or no echo
    } else {
      mappedValue = map(distance, minValue, maxValue, 100, 0);
      mappedValue = constrain(mappedValue, 0, 100);
    }

    percentValues[i] = mappedValue;

    // Small delay between sensors to prevent interference
    delay(10);
  }

  // 5. 시리얼 모니터에 출력
  for (int i = 0; i < numSensors; i++) {
    Serial.print(percentValues[i]);
    if (i < numSensors - 1) {
      Serial.print(" ");
    }
  }
  Serial.println();

  // 0.1초 대기 후 재측정
  delay(100);
}
