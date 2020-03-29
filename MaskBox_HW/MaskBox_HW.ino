#define BASE_RPM 70.0       // 마스크 1개 제공을 위한 DC 모터 속도
#define delay_time 500.0    // 마스크 1개 제공을 위하 기본 Delay 값

// DC 쿨러 모터 #1 Pin 정의
int IN_PWM1 = 5;    // #1 PWM은 5번 핀에서 생성
int motorPin1 = 7;  // #1 모터 H-Bridge Input으로 7번 핀 사용
int motorPin2 = 8;  // #1 모터 H-Bridge Input으로 7번 핀 사용
 
// DC 쿨러 모터 #2 Pin 정의
int IN_PWM2 = 6;    // #2 PWM은 6번 핀에서 생성
int motorPin3 = 2;  // #2 모터 H-Bridge Input으로 2번 핀 사용
int motorPin4 = 4;  // #2 모터 H-Bridge Input으로 4번 핀 사용

int in_Data = 0;    // Raspberry Pi Serial 통신 수신 데이터 변수
 
void setup() {
  Serial.begin(9600);   // Serial 통신 속도 정의
  // 모터 제어를 위한 Pin 사용 정의
  pinMode(motorPin1,OUTPUT);
  pinMode(motorPin2,OUTPUT);
  pinMode(motorPin3,OUTPUT);
  pinMode(motorPin4,OUTPUT);
}
void loop() {
  // Serial 통신 데이터 수신하면...
  if(Serial.available()){
    in_Data = Serial.read();  // Serial 통신 데이터를 읽어서 저장함
    if(in_Data == '1'){       // 수신 데이터가 '1'이라면...
      // DC 쿨러 모터 #1 제어
      digitalWrite(motorPin1,HIGH);
      digitalWrite(motorPin2,LOW);
      analogWrite(IN_PWM1,BASE_RPM);
      
      // DC 쿨러 모터 #2 제어
      digitalWrite(motorPin3,HIGH);
      digitalWrite(motorPin4,LOW);
      analogWrite(IN_PWM2,BASE_RPM);

      delay(delay_time);

      // 미사용에 따른 H-Bridge 전위차 비활성화 
      digitalWrite(motorPin1,HIGH);
      digitalWrite(motorPin2,HIGH);
      digitalWrite(motorPin3,HIGH);
      digitalWrite(motorPin4,HIGH);
    }
    else {
      // 미사용에 따른 H-Bridge 전위차 비활성화
      digitalWrite(motorPin1,HIGH);
      digitalWrite(motorPin2,HIGH);
      digitalWrite(motorPin3,HIGH);
      digitalWrite(motorPin4,HIGH);
    }
  }
}
