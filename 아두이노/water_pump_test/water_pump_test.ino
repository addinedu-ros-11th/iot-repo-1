const int EN_PIN = 11 ;

const int MD1_IN1_PIN = 2 ;               // 1번 워터펌프
const int MD1_IN2_PIN = 3 ;
const int MD1_IN3_PIN = 4 ;               // 2번 워터펌프
const int MD1_IN4_PIN = 5 ;

const int MD2_IN1_PIN = 7 ;               // 3번 워터펌프
const int MD2_IN2_PIN = 8 ;
const int MD2_IN3_PIN = 9 ;               // 4번 워터펌프
const int MD2_IN4_PIN = 10 ;

const int MD3_IN1_PIN = A0 ;              // 5번 워터펌프
const int MD3_IN2_PIN = A1 ;
const int MD3_IN3_PIN = A2 ;              // 6번 워터펌프
const int MD3_IN4_PIN = A3 ;

void setup()
{
  Serial.begin(9600);

  pinMode(EN_PIN, OUTPUT);

  // 1, 2 워터 펌프 드라이버 핀
  pinMode(MD1_IN1_PIN, OUTPUT);
  pinMode(MD1_IN2_PIN, OUTPUT);
  pinMode(MD1_IN3_PIN, OUTPUT);
  pinMode(MD1_IN4_PIN, OUTPUT);

  // 3, 4 워터 펌프 드라이버 핀
  pinMode(MD2_IN1_PIN, OUTPUT);
  pinMode(MD2_IN2_PIN, OUTPUT);
  pinMode(MD2_IN3_PIN, OUTPUT);
  pinMode(MD2_IN4_PIN, OUTPUT);

  // 5, 6 워터 펌프 드라이버 핀
  pinMode(MD3_IN1_PIN, OUTPUT);
  pinMode(MD3_IN2_PIN, OUTPUT);
  pinMode(MD3_IN3_PIN, OUTPUT);
  pinMode(MD3_IN4_PIN, OUTPUT);

  stopAll();
}


// 모터 정방향
void loop() 
{
  // 1번 워터 펌프 동작
  digitalWrite(MD1_IN1_PIN, HIGH);
  digitalWrite(MD1_IN2_PIN, LOW);
  analogWrite(EN_PIN, 150); // 모터 속도 변경 가능 (0 ~ 255)
  Serial.println("1번 모터 동작");
  delay(3000);

  stopAll();
  Serial.println("정지");
  delay(1000);

  // 2번 워터 펌프 동작
  digitalWrite(MD1_IN3_PIN, HIGH);
  digitalWrite(MD1_IN4_PIN, LOW); 
  analogWrite(EN_PIN, 150); // 모터 속도 변경 가능 (0 ~ 255)
  Serial.println("2번 모터 동작");
  delay(3000);

  stopAll();
  Serial.println("정지");
  delay(1000);

  // 3번 워터 펌프 동작
  digitalWrite(MD2_IN1_PIN, HIGH);
  digitalWrite(MD2_IN2_PIN, LOW);
  analogWrite(EN_PIN, 150); // 모터 속도 변경 가능 (0 ~ 255)
  Serial.println("3번 모터 동작");
  delay(3000);

  stopAll();
  Serial.println("정지");
  delay(1000);

  // 4번 워터 펌프 동작
  digitalWrite(MD2_IN3_PIN, HIGH);
  digitalWrite(MD2_IN4_PIN, LOW); 
  analogWrite(EN_PIN, 150); // 모터 속도 변경 가능 (0 ~ 255)
  Serial.println("4번 모터 동작");
  delay(3000);

  stopAll();
  Serial.println("정지");
  delay(1000);

  // 5번 워터 펌프 동작
  digitalWrite(MD3_IN1_PIN, HIGH);
  digitalWrite(MD3_IN2_PIN, LOW);
  analogWrite(EN_PIN, 150); // 모터 속도 변경 가능 (0 ~ 255)
  Serial.println("5번 모터 동작");
  delay(3000);

  stopAll();
  Serial.println("정지");
  delay(1000);

  // 6번 워터 펌프 동작
  digitalWrite(MD3_IN3_PIN, HIGH);
  digitalWrite(MD3_IN4_PIN, LOW); 
  analogWrite(EN_PIN, 150); // 모터 속도 변경 가능 (0 ~ 255)
  Serial.println("6번 모터 동작");
  delay(3000);

  stopAll();
  Serial.println("정지");
  delay(1000);
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


