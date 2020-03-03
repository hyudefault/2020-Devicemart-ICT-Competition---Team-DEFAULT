#define BASE_RPM 70.0
#define delay_time 300.0
 
int IN_PWM1 = 5;
int motorPin1 = 7;
int motorPin2 = 8;
 
int IN_PWM2 = 6;
int motorPin3 = 2;
int motorPin4 = 4;

int in_Data = 0;
 
void setup() {
  Serial.begin(9600);
  pinMode(motorPin1,OUTPUT);
  pinMode(motorPin2,OUTPUT);
  pinMode(motorPin3,OUTPUT);
  pinMode(motorPin4,OUTPUT);
}
void loop() {
  if(Serial.available())
  {
    in_Data = Serial.read();
    if(in_Data == '1')
    {
      digitalWrite(motorPin1,HIGH);
      digitalWrite(motorPin2,LOW);
      analogWrite(IN_PWM1,BASE_RPM);

      digitalWrite(motorPin3,HIGH);
      digitalWrite(motorPin4,LOW);
      analogWrite(IN_PWM2,BASE_RPM);

      delay(delay_time);
      
      digitalWrite(motorPin1,HIGH);
      digitalWrite(motorPin2,HIGH);
      digitalWrite(motorPin3,HIGH);
      digitalWrite(motorPin4,HIGH);
    }
    else 
    {
      digitalWrite(motorPin1,HIGH);
      digitalWrite(motorPin2,HIGH);
      digitalWrite(motorPin3,HIGH);
      digitalWrite(motorPin4,HIGH);
    }

  }
}
