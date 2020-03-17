/*
 * Name:        Air_Purifier_HW_Arduino_UNO.ino
 * Created:     2020-03-17 오후 8:06
 * Author:      bmj10104@naver.com
 *  PMS7003 미세먼지 측정 센서를 사용한 공기청정기 펌웨어입니다.
 *  적외선 리모컨을 이용해 모드를 변경하면 LED와 FAN 속도가 변하고,
 *  센서를 통해 측정된 미세먼지 농도값은 LCD에 표시됩니다.
 */
 
#include <SoftwareSerial.h>           // 소프트웨어시리얼 사용을 위한 헤더
#include <LiquidCrystal_I2C.h>        // LCD용 라이브러리
#include <Wire.h>                     // LCD_I2C 통신용 라이브러리
#include <IRremote.h>                 // 적외선 리모컨용 라이브러리

SoftwareSerial mySerial(6,5);         // Arduino Uno prot RX, TX
LiquidCrystal_I2C lcd(0x27,16,2);     // lcd 객체 선언

//---------------------Microdust Sensor 변수 선언-----------------------------
#define START_1 0x42                  // Frame packet start byte
#define START_2 0x4d                  // Frame packet start byte
#define DATA_LENGTH_H 0               // Start byte를 제외한 프레임 갯수
#define DATA_LENGHT_L 1
#define PM1_0_ATMOSPHERE_H 8          // PM1_0 = 1.0
#define PM1_0_ATMOSPHERE_L 9
#define PM2_5_ATMOSPHERE_H 10         // PM2_5 = 2.5
#define PM2_5_ATMOSPHERE_L 11
#define PM10_ATMOSPHERE_H 12          // PM10
#define PM10_ATMOSPHERE_L 13
#define PM2_5_PARTICLE_H 16
#define PM2_5_PARTICLE_L 17
#define VERSION 26
#define ERROR_CODE  27
#define CHECKSUM  29
 // PMS 7003 센서에서 보내주는 데이터의 위치별 데이터 내용 구조
byte bytCount1 = 0;
byte bytCount2 = 0;
unsigned char chrRecv;
unsigned char chrData[30];
int PM01;
int PM25;
int PM10;

unsigned int GetPM_Data(unsigned char chrSrc[], byte bytHigh, byte bytLow)
{
  return (chrSrc[bytHigh] << 8) + chrSrc[bytLow];
}
//------------------------------------------------------------------------

int RECV_PIN = A0;                    //define input pin on Arduino
IRrecv irrecv(RECV_PIN);              // 적외선 센서 입력 핀
decode_results results;               //

const int ledPin1 = 13;               // Mode 1 표시용 LED 
const int ledPin2 = 12;               // Mode 2 표시용 LED
const int ledPin3 = 11;               // Mode 3 표시용 LED

const int INA = 7;                    // Motor 방향 제어
const int INB = 8;                    // Motor 방향 제어
const int PWM = 9;                    // Motor PWM 조절

int ModeState=0;                      // Mode 

void mode_setting_fn(int ModeState);  // Mode에 따른 동작 함수

int Motor_speed_1=220;                // Mode 1 PWM 값
int Motor_speed_2=240;                // Mode 2 PWM 값
int Motor_speed_3=250;                // Mode 3 PWM 값

int prm=0;                            // previous ModeState
int prs=0;                            // previous Motor_speed


void setup() {
  Serial.begin(9600);                 // for debugging
  Serial.println("PMS7003 Ready ");
  
  mySerial.begin(9600);               // Use software serial
  
  lcd.init();
  lcd.backlight();

  irrecv.enableIRIn();                // Start the receiver

  mode_setting_fn(ModeState);         // Mode 0 동작
  
  pinMode(ledPin1,OUTPUT);
  pinMode(ledPin2,OUTPUT);
  pinMode(ledPin3,OUTPUT);
  pinMode(INA, OUTPUT);
  pinMode(INB, OUTPUT);
  pinMode(PWM, OUTPUT);
}

void loop() {
  // PMS 7003: 9600 bps / None Parity /Stop 1 bit를 사용하는 32 Byte의 데이터를 1초 간격으로 송신
  if(mySerial.available()) {    
    for(int i = 0;i<32;i++) {
      chrRecv = mySerial.read();
      if(chrRecv == START_2){
        bytCount1 = 2;
        break;
      }
    }
    if(bytCount1 == 2) {
      bytCount1 = 0;
      for(int i = 0; i< 30; i++) {     // 미세먼지 측정 결과 값을 30byte로 전송  
        chrData[i] = mySerial.read();
      }
      if((unsigned int) chrData[ERROR_CODE] == 0 ) {
        PM01 = GetPM_Data(chrData, PM1_0_ATMOSPHERE_H, PM1_0_ATMOSPHERE_L);
          // PM1.0 값을 읽으려면 PM1_0_ATMOSPHERE_H,PM1_0_ATMOSPHERE_L 부분을 읽으면 된다.
        PM25 = GetPM_Data(chrData, PM2_5_ATMOSPHERE_H, PM2_5_ATMOSPHERE_L);
          // PM2.5 값을 읽으려면 PM2_5_ATMOSPHERE_H,PM2_5_ATMOSPHERE_L 부분을 읽으면 된다.
        PM10 = GetPM_Data(chrData, PM10_ATMOSPHERE_H, PM10_ATMOSPHERE_L);
          // PM10 값을 읽으려면 PM10_ATMOSPHERE_H,PM10_ATMOSPHERE_L 부분을 읽으면 된다.
        Serial.print("PM1.0=");
        Serial.print(PM01);
        Serial.print(",PM2.5=");
        Serial.print(PM25);
        Serial.print(",PM10=");
        Serial.println(PM10);
        delay(1000);                    // 1초 대기 
      }
      else {
        Serial.println("PMS7003 ERROR");
      }
    }
  }
  else {
    Serial.println("PMS7003 NOT available");
  }
  if (irrecv.decode(&results)) {        // IR 리모컨의 신호가 입력되면,
    switch (results.value) {            // 각각의 경우에 따라 동작
      case 0xFF6897:                    // IR 리모컨의 0 번을 누르면,
        ModeState=0;                    // Mode 0으로 변경
        prm=ModeState;                  // 모드 상태 값 저장
        mode_setting_fn(ModeState);     // Mode 0 동작
        break;
      
      case 0xFF30CF:                    // IR 리모컨의 1 번을 누르면,
        ModeState=1;                    // Mode 1로 변경
        prm=ModeState;                  // 모드 상태 값 저장
        mode_setting_fn(ModeState);     // Mode 1 동작
        break; 
      
      case 0xFF18E7:                    // IR 리모컨의 2 번을 누르면,
        ModeState=2;                    // Mode 2로 변경
        prm=ModeState;                  // 모드 상태 값 저장
        mode_setting_fn(ModeState);     // Mode 2 동작
        break;
        
      case 0xFF7A85:                    // IR 리모컨의 3 번을 누르면,
        ModeState=3;                    // Mode 3으로 변경
        prm=ModeState;                  // 모드 상태 값 저장
        mode_setting_fn(ModeState);     // Mode 3 동작
        break;
        
      case 0x00FF10EF:                  // IR 리모컨의 4 번을 누르면,
        ModeState=4;                    // Mode 4로 변경
        mode_setting_fn(ModeState);     // Mode 4 동작
         break; 
    }
    
    mode_setting_fn(prm);               // Mode 4 동작 이후 이전 모드로 돌아가서 동작
    irrecv.resume();                    // Receive the next value
  }
} 

void mode_setting_fn(int ModeState)     // Mode에 따른 동작 함수
{
  if(ModeState==0) {                    // Mode 0 이면,
    digitalWrite(ledPin1,LOW);
    digitalWrite(ledPin2,LOW);
    digitalWrite(ledPin3,LOW);          // LED 다 끄기
    analogWrite(PWM,0);                 // 모터 정지
    prs=0;                              // 모터 속도 저장
    lcd.clear();
    lcd.setCursor(0,1);                 // 커서를 첫 번째 줄에 가져다 놓기
    lcd.print("Air Cleaner*^ ^*");      // LCD에 "Air Cleaner*^ ^*" 표시
    delay(250);                         // 0.25초 대기
    lcd.setCursor(0,1);                 // 커서를 두 번째 줄에 가져다 놓기
    lcd.print("Select MODE 1-4");       // LCD에 "Select MODE 1-4"
    }
  if(ModeState==1) {                    // Mode 1 이면,
    digitalWrite(ledPin1,HIGH);         // 초록색 LED 켜기
    digitalWrite(ledPin2,LOW);
    digitalWrite(ledPin3,LOW);
    digitalWrite(INA,HIGH);
    digitalWrite(INB,LOW);
    analogWrite(PWM,Motor_speed_1);     // 모터 동작
    prs=Motor_speed_1;                  // 모터 속력 저장
    lcd.clear();
    lcd.setCursor(0,1);                 // 커서를 첫 번째 줄에 가져다 놓기
    lcd.print("MODE : 1");              // LCD에 모드 표시
    delay(250);                         // 0.25초 대기
    lcd.setCursor(0,1);                 // 커서를 두 번째 줄에 가져다 놓기
    lcd.print("FAN : *");               // FAN 세기 표시
    }
  if(ModeState==2) {                    // Mode 2 이면,
    digitalWrite(ledPin1,LOW);
    digitalWrite(ledPin2,HIGH);         // 빨간색 LED 켜기
    digitalWrite(ledPin3,LOW);          
    digitalWrite(INA,HIGH);
    digitalWrite(INB,LOW);
    analogWrite(PWM,Motor_speed_2);     // 모터 동작
    prs=Motor_speed_2;                  // 모터 속력 저장
    lcd.clear();
    lcd.setCursor(0,1);                 // 커서를 첫 번째 줄에 가져다 놓기
    lcd.print("MODE : 2");              // LCD에 모드 표시
    delay(250);                         // 0.25초 대기
    lcd.setCursor(0,1);                 // 커서를 두 번째 줄에 가져다 놓기
    lcd.print("FAN : * *");             // LCD에 FAN 세기 표시
    }
  if(ModeState==3) {                    // Mode 3 이면,
    digitalWrite(ledPin1,LOW);
    digitalWrite(ledPin2,LOW);
    digitalWrite(ledPin3,HIGH);         // 노란색 LED 켜기
    digitalWrite(INA,HIGH);
    digitalWrite(INB,LOW);
    analogWrite(PWM,Motor_speed_3);     // 모터 동작
    prs=Motor_speed_3;                  // 모터 속력 저장
    lcd.clear();
    lcd.setCursor(0,1);                 // 커서를 첫 번째 줄에 가져다 놓기
    lcd.print("MODE : 3");              // LCD에 모드 표시
    delay(250);                         // 0.25초 대기
    lcd.setCursor(0,1);                 // 커서를 두 번째 줄에 가져다 놓기
    lcd.print("FAN : * * *");           // LCD에 FAN 세기 표시
  }
  if(ModeState==4) {                    // Mode 4 이면,
    digitalWrite(INA,HIGH);             
    digitalWrite(INB,LOW);              
    analogWrite(PWM,prs);               // 이전 모드의 모터 속력으로 Motor 동작
    lcd.clear();
    lcd.setCursor(0,1);                 // 커서를 첫 번째 줄에 가져다 놓기
    lcd.print(PM10);
    lcd.print(" ug/m^3");               // LCD에 PM10 농도값 표시
    lcd.setCursor(0,1);                 // 커서를 두 번째 줄에 가져다 놓기
    lcd.print(PM25);            
    lcd.print(" ug/m^3");               // LCD에 PM2.5 농도값 표시
    delay(2000);                        // 2초 대기
  }
}
