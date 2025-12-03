const int EN_PIN = 11;        // 속도 조절

const int MD1_IN1_PIN = 2;    // 1번 펌프
const int MD1_IN2_PIN = 3;
const int MD1_IN3_PIN = 4;    // 2번 펌프
const int MD1_IN4_PIN = 5;

const int MD2_IN1_PIN = 7;    // 3번 펌프
const int MD2_IN2_PIN = 8;
const int MD2_IN3_PIN = 9;    // 4번 펌프
const int MD2_IN4_PIN = 10;

const int MD3_IN1_PIN = A0;   // 5번 펌프
const int MD3_IN2_PIN = A1;
const int MD3_IN3_PIN = A2;   // 6번 펌프
const int MD3_IN4_PIN = A3;

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
  // 모터 핀
  pinMode(EN_PIN, OUTPUT);

  pinMode(MD1_IN1_PIN, OUTPUT);
  pinMode(MD1_IN2_PIN, OUTPUT);
  pinMode(MD1_IN3_PIN, OUTPUT);
  pinMode(MD1_IN4_PIN, OUTPUT);

  pinMode(MD2_IN1_PIN, OUTPUT);
  pinMode(MD2_IN2_PIN, OUTPUT);
  pinMode(MD2_IN3_PIN, OUTPUT);
  pinMode(MD2_IN4_PIN, OUTPUT);

  pinMode(MD3_IN1_PIN, OUTPUT);
  pinMode(MD3_IN2_PIN, OUTPUT);
  pinMode(MD3_IN3_PIN, OUTPUT);
  pinMode(MD3_IN4_PIN, OUTPUT);

  stopAll();
  
  // 버튼, 릴레이, 부저 핀
  pinMode(RELAY_PIN, OUTPUT);           // 릴레이
  pinMode(PUSH_BUTTON_1, INPUT_PULLUP); // ON, OFF 버튼
  pinMode(PUSH_BUTTON_2, INPUT_PULLUP); // 비상 정지, 부저 정지
  pinMode(BZ_PIN, OUTPUT);              // 부저 핀

  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(BZ_PIN, LOW);
}

void loop()
{
  if (Serial.available())
  {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "P1") runPump(1);
    else if (cmd == "P2") runPump(2);
    else if (cmd == "P3") runPump(3);
    else if (cmd == "P4") runPump(4);
    else if (cmd == "P5") runPump(5);
    else if (cmd == "P6") runPump(6);
  }

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

void runPump(int num) {
  stopAll();
  analogWrite(EN_PIN, 150);

  switch (num) {
    case 1:
      digitalWrite(MD1_IN1_PIN, HIGH);
      digitalWrite(MD1_IN2_PIN, LOW);
      break;
    case 2:
      digitalWrite(MD1_IN3_PIN, HIGH);
      digitalWrite(MD1_IN4_PIN, LOW);
      break;
    case 3:
      digitalWrite(MD2_IN1_PIN, HIGH);
      digitalWrite(MD2_IN2_PIN, LOW);
      break;
    case 4:
      digitalWrite(MD2_IN3_PIN, HIGH);
      digitalWrite(MD2_IN4_PIN, LOW);
      break;
    case 5:
      digitalWrite(MD3_IN1_PIN, HIGH);
      digitalWrite(MD3_IN2_PIN, LOW);
      break;
    case 6:
      digitalWrite(MD3_IN3_PIN, HIGH);
      digitalWrite(MD3_IN4_PIN, LOW);
      break;
  }

  Serial.print(num);
  Serial.println("번 펌프 동작");

  delay(3000);
  stopAll();
}

void stopAll() {
  digitalWrite(MD1_IN1_PIN, LOW);
  digitalWrite(MD1_IN2_PIN, LOW);
  digitalWrite(MD1_IN3_PIN, LOW);
  digitalWrite(MD1_IN4_PIN, LOW);

  digitalWrite(MD2_IN1_PIN, LOW);
  digitalWrite(MD2_IN2_PIN, LOW);
  digitalWrite(MD2_IN3_PIN, LOW);
  digitalWrite(MD2_IN4_PIN, LOW);

  digitalWrite(MD3_IN1_PIN, LOW);
  digitalWrite(MD3_IN2_PIN, LOW);
  digitalWrite(MD3_IN3_PIN, LOW);
  digitalWrite(MD3_IN4_PIN, LOW);

  analogWrite(EN_PIN, 0);
}

