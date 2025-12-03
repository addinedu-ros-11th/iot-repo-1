const int RELAY_PIN = 12;     // 릴레이 핀

const int PUSH_BUTTON_1 = A4; // 버튼
const int PUSH_BUTTON_2 = A5; 

const int BZ_PIN = 13;        // 부저 핀

bool relayToggle = false;     // 릴레이 토글
bool lastButton1State = HIGH; // A4 이전 상태

int pressCount = 0;           // A5 눌림 횟수
bool lastButton2State = HIGH; //  A5 이전 상태

void setup()
{
  Serial.begin(9600);

  pinMode(RELAY_PIN, OUTPUT);
  
  pinMode(PUSH_BUTTON_1, INPUT_PULLUP);
  pinMode(PUSH_BUTTON_2, INPUT_PULLUP);

  pinMode(BZ_PIN, OUTPUT);

  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(BZ_PIN, LOW);
}

void loop()
{
  // A4 버튼: 릴레이 토글
  bool currentButton1 = digitalRead(PUSH_BUTTON_1);
  // 45 버튼이 눌리는 순간 감지 (HIGH -> LOW)
  if (lastButton1State == HIGH && currentButton1 == LOW)
  {
    if (digitalRead(BZ_PIN) == HIGH)
    {
      Serial.println("RELAY BLOCKED (BUZZER ON)");
    }
    
    else
    {
      relayToggle = !relayToggle;
      digitalWrite(RELAY_PIN, relayToggle ? HIGH : LOW);
      Serial.println(relayToggle ? "POWER ON" : "POWER OFF");
    }

    pressCount = 0;
    // digitalWrite(BZ_PIN, LOW);
    delay(200);
  }
  lastButton1State = currentButton1;

  // A5 버튼 읽기
  bool currentButton2 = digitalRead(PUSH_BUTTON_2);

  // A5 버튼이 눌리는 순간 감지 (HIGH -> LOW)
  if (lastButton2State == HIGH && currentButton2 == LOW)
  {
    pressCount++;  // 버튼 누른 횟수 증가

    if (pressCount == 1)
    {
      digitalWrite(BZ_PIN, HIGH);
      Serial.println("BUZZER ON");
    }

    else if (pressCount == 2)
    {
      digitalWrite(BZ_PIN, LOW);
      Serial.println("BUZZER OFF");
    }

    digitalWrite(RELAY_PIN, LOW);
    relayToggle = 0;
    Serial.println("POWER OFF");
    delay(200);
  }
  lastButton2State = currentButton2;
  
  // GUI 명령 처리
  if (Serial.available() > 0)
  {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    // GUI → P_ON = A4 버튼과 동일한 동작
    if (cmd == "P_ON")
    {
      // 부저가 울리면 릴레이 금지
      if (digitalRead(BZ_PIN) == HIGH)
      {
        Serial.println("RELAY BLOCKED (BUZZER ON)");
      }
      else
      {
        relayToggle = true;
        digitalWrite(RELAY_PIN, HIGH);
        Serial.println("POWER ON");

        //초기화
        pressCount = 0;
      }
    }
    // GUI → P_OFF = 릴레이 OFF
    else if (cmd == "P_OFF")
    {
      relayToggle = false;
      digitalWrite(RELAY_PIN, LOW);
      Serial.println("POWER OFF");
    }
    // GUI → BZ_ON = A5 첫번째 누름과 동일
    else if (cmd == "BZ_ON")
    {
      // A5 첫 클릭과 동일하게 처리
      pressCount = 1;
      digitalWrite(BZ_PIN, HIGH);
      Serial.println("BUZZER ON");

      // 비상정지 → 릴레이 OFF
      relayToggle = 0;
      digitalWrite(RELAY_PIN, LOW);
      Serial.println("POWER OFF");
    }
    // GUI → BZ_OFF = A5 두 번째 누름과 동일
    else if (cmd == "BZ_OFF")
    {
      pressCount = 2;
      digitalWrite(BZ_PIN, LOW);
      Serial.println("BUZZER OFF");
    }
  }
}