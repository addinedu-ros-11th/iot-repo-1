const int EN_PIN = 11;                  // 속도 조절

const int MD1_IN1_PIN = 2;
const int MD1_IN2_PIN = 3;
const int MD1_IN3_PIN = 4;
const int MD1_IN4_PIN = 5;

const int MD2_IN1_PIN = 7;
const int MD2_IN2_PIN = 8;
const int MD2_IN3_PIN = 9;
const int MD2_IN4_PIN = 10;

const int MD3_IN1_PIN = A0;
const int MD3_IN2_PIN = A1;
const int MD3_IN3_PIN = A2;
const int MD3_IN4_PIN = A3;

const int RELAY_PIN = 12;    
const int PUSH_BUTTON_1 = A4;
const int PUSH_BUTTON_2 = A5; 
const int BZ_PIN = 13;

bool relayToggle = false;
bool lastButton1State = HIGH;
int pressCount = 0;
bool lastButton2State = HIGH;

void setup()
{
  Serial.begin(9600);

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
  
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(PUSH_BUTTON_1, INPUT_PULLUP);
  pinMode(PUSH_BUTTON_2, INPUT_PULLUP);
  pinMode(BZ_PIN, OUTPUT);

  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(BZ_PIN, LOW);

  Serial.println("SYSTEM READY");
}

void loop()
{
  // 버튼 (A4) 전원 토글
  bool currentButton1 = digitalRead(PUSH_BUTTON_1);

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

      if (!relayToggle) stopAll();
    }

    pressCount = 0;
    delay(200);
  }
  lastButton1State = currentButton1;

  // 버튼 (A5) 부저/비상정지
  bool currentButton2 = digitalRead(PUSH_BUTTON_2);

  if (lastButton2State == HIGH && currentButton2 == LOW)
  {
    pressCount++;

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
    relayToggle = false;
    stopAll();

    Serial.println("POWER OFF (EMERGENCY)");
    delay(200);
  }
  lastButton2State = currentButton2;

  // GUI 명령 처리 (1번만 읽도록 통합)
  if (Serial.available() > 0)
  {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    // 전원 
    if (cmd == "P_ON")
    {
      if (digitalRead(BZ_PIN) == HIGH)
        Serial.println("RELAY BLOCKED (BUZZER ON)");
      else
      {
        relayToggle = true;
        digitalWrite(RELAY_PIN, HIGH);
        Serial.println("POWER ON");
        pressCount = 0;
      }
    }
    else if (cmd == "P_OFF")
    {
      relayToggle = false;
      digitalWrite(RELAY_PIN, LOW);
      stopAll();
      Serial.println("POWER OFF");
    }

    // 부저
    else if (cmd == "BZ_ON")
    {
      pressCount = 1;
      digitalWrite(BZ_PIN, HIGH);
      Serial.println("BUZZER ON");

      relayToggle = false;
      digitalWrite(RELAY_PIN, LOW);
      stopAll();
      Serial.println("POWER OFF");
    }
    else if (cmd == "BZ_OFF")
    {
      pressCount = 2;
      digitalWrite(BZ_PIN, LOW);
      Serial.println("BUZZER OFF");
    }

    // 펌프 (P1 ~ P6)
    else if (cmd.startsWith("P") && cmd.length() == 2)
    {
      int num = cmd.substring(1).toInt();
      if (num >= 1 && num <= 6)
      {
        // 펌프 조건 체크
        if (!relayToggle)
        {
          Serial.println("PUMP BLOCKED (POWER OFF)");
        }
        else if (digitalRead(BZ_PIN) == HIGH)
        {
          Serial.println("PUMP BLOCKED (BUZZER ON)");
        }
        else
        {
          runPump(num);
        }
      }
    }
    else if (cmd.startsWith("PUMP"))
    {
      // 예: "PUMP,2,2000"
      int c1 = cmd.indexOf(',');
      int c2 = cmd.indexOf(',', c1 + 1);

      int pump_num = cmd.substring(c1 + 1, c2).toInt();
      int run_time = cmd.substring(c2 + 1).toInt();

      if (!relayToggle)
      {
        Serial.println("PUMP BLOCKED (POWER OFF)");
      }
      else if (digitalRead(BZ_PIN) == HIGH)
      {
        Serial.println("PUMP BLOCKED (BUZZER ON)");
      }
      else
      {
        runPumpTime(pump_num, run_time);
      }
    }
  }
}

void runPump(int num)
{
  runPumpTime(num, 3000);   // 기본 3초
}

// 펌프
void runPumpTime(int num, int run_time)
{
  stopAll();
  analogWrite(EN_PIN, 150);  // 속도 설정

  switch (num) {
    case 1: digitalWrite(MD1_IN1_PIN, HIGH); digitalWrite(MD1_IN2_PIN, LOW); break;
    case 2: digitalWrite(MD1_IN3_PIN, HIGH); digitalWrite(MD1_IN4_PIN, LOW); break;
    case 3: digitalWrite(MD2_IN1_PIN, HIGH); digitalWrite(MD2_IN2_PIN, LOW); break;
    case 4: digitalWrite(MD2_IN3_PIN, HIGH); digitalWrite(MD2_IN4_PIN, LOW); break;
    case 5: digitalWrite(MD3_IN1_PIN, HIGH); digitalWrite(MD3_IN2_PIN, LOW); break;
    case 6: digitalWrite(MD3_IN3_PIN, HIGH); digitalWrite(MD3_IN4_PIN, LOW); break;
    default: return;
  }

  Serial.print("PUMP RUN ");
  Serial.print(num);
  Serial.print(" for ");
  Serial.print(run_time);
  Serial.println("ms");

  delay(run_time);  
  stopAll();
}

void stopAll()
{
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
