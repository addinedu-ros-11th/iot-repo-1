#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 9
MFRC522 rfid(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();
  
  pinMode(13, OUTPUT); // 상태 표시용 LED
  
  // 시작 알림 (빠르게 3번 깜빡)
  for(int i=0; i<3; i++) {
    digitalWrite(13, HIGH); delay(50);
    digitalWrite(13, LOW);  delay(50);
  }
}

void loop() {
  // [핵심] RFID 모듈이 멍때리지 않도록 계속 초기화 명령을 줌
  // (이 줄이 있으면 카드를 대고 있다가 떼었을 때 재인식이 잘 됩니다)
  rfid.PCD_Init(); 

  // 카드 감지 확인
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    
    // 1. LED 켜기 (인식 시작)
    digitalWrite(13, HIGH);
    
    String content = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
      content.concat(String(rfid.uid.uidByte[i] < 0x10 ? " 0" : " "));
      content.concat(String(rfid.uid.uidByte[i], HEX));
    }
    content.toUpperCase();
    
    // 2. 데이터 전송
    Serial.print("UID:");
    Serial.println(content.substring(1));
    
    // 3. LED 끄기 (전송 완료)
    // 아주 짧게 둬서 파이썬이 없어도 빨리 루프를 돌게 함
    delay(50); 
    digitalWrite(13, LOW);

    // 4. 카드 통신 종료 및 암호화 중지
    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
  }
  
  // 파이썬 명령 처리
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    // ... 명령 처리 로직 ...
  }
}
