int BUZZERPIN = 2;
int SOUND = 100;

int PUSH_BUTTON_1 = 3;
int PUSH_BUTTON_2 = 4;

void setup()
{
  Serial.begin(9600);
  pinMode(BUZZERPIN, OUTPUT);
  
  pinMode(PUSH_BUTTON_1, INPUT);
  pinMode(PUSH_BUTTON_2, INPUT);  
}

void loop()
{
  int BUTTON_1 = digitalRead(PUSH_BUTTON_1);
  int BUTTON_2 = digitalRead(PUSH_BUTTON_2);

  if(BUTTON_1 == HIGH)
  {
    digitalWrite(BUZZERPIN, HIGH);
    Serial.println("소리 켜짐");
  }

  if(BUTTON_2 == HIGH)
  {
    digitalWrite(BUZZERPIN, LOW);
    Serial.println("소리 꺼짐");
  }
}
