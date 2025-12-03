int BUZZERPIN = 2;

int PUSH_BUTTON_1 = 3;
int PUSH_BUTTON_2 = 4;

int RED_LED = 8;
int GREEN_LED = 9;

void setup()
{
  Serial.begin(9600);
  pinMode(BUZZERPIN, OUTPUT);
  
  pinMode(PUSH_BUTTON_1, INPUT);
  pinMode(PUSH_BUTTON_2, INPUT);  

  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
}

void loop()
{
  int BUTTON_1 = digitalRead(PUSH_BUTTON_1);
  int BUTTON_2 = digitalRead(PUSH_BUTTON_2);

  if(BUTTON_1 == HIGH)
  {
    digitalWrite(BUZZERPIN, HIGH);
    digitalWrite(RED_LED, HIGH);
    digitalWrite(GREEN_LED, LOW);
    Serial.println("소리 켜짐");
  }

  if(BUTTON_2 == HIGH)
  {
    digitalWrite(BUZZERPIN, LOW);
    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(RED_LED, LOW);
    Serial.println("소리 꺼짐");
  }
}