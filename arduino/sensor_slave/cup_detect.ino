const int sensorPin = A0;  
//const int ledPin = 13;     


int threshold = 50; 

void setup() {
  //pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  //int rawValue = analogRead(sensorPin); // 0 ~ 1023 사이의 값 읽기


  if (rawValue > threshold) {
    //digitalWrite(ledPin, HIGH); // 아두이노 LED 켜기 (확인용)
    Serial.println("1");        // 파이썬으로 "1" (True) 전송
  } 
  else {
    //digitalWrite(ledPin, LOW);  // 아두이노 LED 끄기
    Serial.println("0");        // 파이썬으로 "0" (False) 전송
  }
  
  delay(100); // 파이썬이 읽을 시간을 주기 위해 약간의 딜레이
}
