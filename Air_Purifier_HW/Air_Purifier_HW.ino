#include <IRremote.h>
#include <LiquidCrystal_I2C.h>
#include <Wire.h>

LiquidCrystal_I2C lcd(0x27,16,2);

void mode_setting_fn(int ModeState);

int RECV_PIN = A0; //define input pin on Arduino
IRrecv irrecv(RECV_PIN);
decode_results results;

const int ledPin1=A3;
const int ledPin2=A2;
const int ledPin3=A1;

const int ENA=7;
const int ENB=8;
const int PWM_1=9;

int ModeState=0;

int Motor_speed_1=150;
int Motor_speed_2=200;
int Motor_speed_3=220;

int val=0;
int prm=0;
int prs=0;

void setup
  Serial.begin(9600);

  lcd.init();
  lcd.backlight();

  irrecv.enableIRIn(); // Start the receiver
  
  pinMode(ledPin1,OUTPUT);
  pinMode(ledPin2,OUTPUT);
  pinMode(ledPin3,OUTPUT);
  pinMode(ENA,OUTPUT);
  pinMode(ENB,OUTPUT);
  pinMode(PWM_1,OUTPUT);

  mode_setting_fn(ModeState);
}

void loop() {

    if (irrecv.decode(&results)) {
      Serial.println(results.value, HEX);
      switch (results.value) {
        case 0xFF6897:
          ModeState=0;
          prm=ModeState;
          mode_setting_fn(ModeState);
          break;
        
        case 0xFF30CF: 
          ModeState=1;
          prm=ModeState;    
          mode_setting_fn(ModeState);
          break; 
        
        case 0xFF18E7:
          ModeState=2;  
          prm=ModeState;        
          mode_setting_fn(ModeState);
          break;
          
        case 0xFF7A85:
          ModeState=3;
          prm=ModeState;
          mode_setting_fn(ModeState);
          break;
          
        case 0x00FF10EF:
          ModeState=4;
          mode_setting_fn(ModeState);
          if(prm==0) {
            lcd.clear();
            lcd.setCursor(0,0);
            lcd.println(val);
            lcd.println(" ug/m^3");
            delay(1000);
            lcd.setCursor(0,1);
            lcd.println("Select MODE 1-4");
          }
          break;
      }
      Serial.println(ModeState);
      mode_setting_fn(prm);
      digitalWrite(ENA,HIGH);
      digitalWrite(ENB,LOW);
      analogWrite(PWM_1,prs);
      irrecv.resume(); // Receive the next value
  }
} 

void mode_setting_fn(int ModeState)
{
  if(ModeState==0) {
    digitalWrite(ledPin1,LOW);
    digitalWrite(ledPin2,LOW);
    digitalWrite(ledPin3,LOW);
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("Air Cleaner*^ ^*");
    delay(1000);
    lcd.setCursor(0,1);
    lcd.print("Select MODE 1-4");
    prs=0;
    }
  if(ModeState==1) {
    digitalWrite(ledPin1,HIGH);
    digitalWrite(ledPin2,LOW);
    digitalWrite(ledPin3,LOW);
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("MODE : 1");
    delay(1000);
    lcd.setCursor(0,1);
    lcd.print("FAN : *");
    prs=Motor_speed_1;
    }
  if(ModeState==2) {
    digitalWrite(ledPin1,LOW);
    digitalWrite(ledPin2,HIGH);
    digitalWrite(ledPin3,LOW);
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("MODE : 2");
    delay(1000);
    lcd.setCursor(0,1);
    lcd.print("FAN : * *");
    prs=Motor_speed_2;
    }
  if(ModeState==3) {  
    digitalWrite(ledPin1,LOW);
    digitalWrite(ledPin2,LOW);
    digitalWrite(ledPin3,HIGH);
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("MODE : 3");
    delay(1000);
    lcd.setCursor(0,1);
    lcd.print("FAN : * * *");     
    prs=Motor_speed_3;
  }
  if(ModeState==4) {
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("Microdust");
    delay(1000);
    lcd.setCursor(1,1);
    lcd.print(val);
    lcd.print(" ug/m^3");
    delay(1000);
  }
}
