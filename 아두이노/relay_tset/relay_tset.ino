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
  // 4번 버튼 읽기
  bool currentButton1 = digitalRead(PUSH_BUTTON_1);
  
  // A4 버튼이 "눌리는 순간" 감지 (HIGH -> LOW)
  if (lastButton1State == HIGH && currentButton1 == LOW)
  { 
    relayToggle = !relayToggle;
    digitalWrite(RELAY_PIN, relayToggle ? HIGH : LOW);

    Serial.println(relayToggle ? "POWER ON" : "POWER OFF");
    
    pressCount = 0; 

    delay(200); // 디바운싱
  }

  lastButton1State = currentButton1;

  // A5 버튼 읽기
  bool currentButton2 = digitalRead(PUSH_BUTTON_2);

  // A5 버튼이 "눌리는 순간" 감지 (HIGH -> LOW)
  if (lastButton2State == HIGH && currentButton2 == LOW)
  {
    digitalWrite(RELAY_PIN, LOW);
    relayToggle = 0;
    Serial.println("POWER OFF");

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

    delay(200);
  }
  lastButton2State = currentButton2;
}

