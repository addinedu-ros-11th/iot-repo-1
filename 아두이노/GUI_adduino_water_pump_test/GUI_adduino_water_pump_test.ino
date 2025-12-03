const int EN_PIN = 11;

// 1,2번 펌프
const int MD1_IN1_PIN = 2;
const int MD1_IN2_PIN = 3;
const int MD1_IN3_PIN = 4;
const int MD1_IN4_PIN = 5;

// 3,4번 펌프
const int MD2_IN1_PIN = 7;
const int MD2_IN2_PIN = 8;
const int MD2_IN3_PIN = 9;
const int MD2_IN4_PIN = 10;

// 5,6번 펌프
const int MD3_IN1_PIN = A0;
const int MD3_IN2_PIN = A1;
const int MD3_IN3_PIN = A2;
const int MD3_IN4_PIN = A3;

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

