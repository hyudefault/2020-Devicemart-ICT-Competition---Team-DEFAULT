import numpy as np
import os
import sys
import cv2      # OpenCV Python 모듈

import time
import serial   # Python Serial 통신 모듈

##############################################################

from bs4 import BeautifulSoup
import requests                 # HTTPS 통신을 위해 사용
import json                     # OpenAPI JSON 데이터 처리 위해 사용
import pandas as pd

### LOCATION ############################################
### 국내 측정소 목록 및 OPEN API KEY 값 목록 ###
list = pd.read_excel('list.xlsx')
key = pd.read_excel('key.xlsx')

### 구글 API kEY값 및 공공데이터 포털 API KEY값 ###
### *** 사용자별 개별 KEY값 등록 필요 ***       ###
KEY_LOCATION = key.KEY_LOCATION[0]
SERVICE_KEY_AIR = key.SERVICE_KEY_AIR[0]

address_flag = 0 # 현재 주소와 일치하는 지역명이 있는지 판단
min = 10000.0   # 최소거리
min_i = 0.0     # 현위치 최단경로 측정소 번호 저장
lat = 0         # 현위치 위도값
lng = 0         # 현위치 경도값
##########################################################

### Thread / Parallel Processing #########################
# 미세먼지 정보 수집 및 영상 처리 동시 병렬 처리를 위해 Thread 사용
from threading import Thread

NEED_MASK = 0   # 마스크 착용 권고 전역 변수
                # 다중 Thread간 기능 연계를 위해서 사용 
##########################################################

### OpenCV 기반 얼굴 인식 및 코 인식을 이용한 마스크 감지 기능 Class ###
class FACE_DETECTOR:

    # 영상 처리 기능 클래스 생성 함수 #
    def __init__(self):

        global NEED_MASK    # 마스크 착용 권고 전역 변수로 인식 지정

        print("Devicemart ICT - Default Team / Face_detector module")

        # HaarCascade 기반 사람 코 인식 모듈 사용
        noseCascade = cv2.CascadeClassifier('./face_detect_model/haarcascade_mcs_nose.xml')

        prev_need_mask = 0;     # 이전 이미지 프레임 상 마스크 착용 여부
        current_need_mask = 0;  # 현재 이미지 프레임 상 마스크 착용 여부

        num="0"
        ser = serial.Serial("/dev/ttyACM0",9600)  # Raspberry Pi - Arduino 시리얼 통신 객체

        print('Face detection for video images using OpenCV DNN Module')

        # OpenFace Project Neural Network 모델 사용
        protopath = './face_detect_model/deploy.prototxt'
        modelpath = './face_detect_model/res10_300x300_ssd_iter_140000.caffemodel'

        # 기본 연결 웹캠 연결
        capture = cv2.VideoCapture(0)

        # 웹캠이 정상 연결되어 작동한다면...
        if(capture.isOpened()):
            print('Video cam is available')
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)      # 웹캠 영상 해상도 설정  
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)     # 웹캠 영상 해상도 설정

            # OpenFace Project NN 모델에 맞춰서 OpenCV DNN 모듈 설정
            net = cv2.dnn.readNetFromCaffe(protopath, modelpath)    

            ### 얼굴 인식 기능 ###
            # 만약 OpenFace Project NN 모델이 정상 로딩이 되지 않았다면...
            if(net is None):
                 print('Failed to load Neural Net')
                 sys.exit(0)    # 프로그램 종료
                 
            # 만약 OpenFace Project NN 모델이 정상 로딩이 된다면...
            elif(net is not None):
                 print('Neural Net ready')

                 # 웹캠 영상을 수신하는 동안 작동함
                 while(capture.isOpened()):
                      ret, frame = capture.read()   # 웹캠 영상 이미지 수신

                      # 웹캠 영상 이미지가 정상 수신 된다면...
                      if(ret == True):

                           (h, w) = frame.shape[:2] # 영상 해상도 정보 저장

                           # OpenCV DNN 모듈에 이미지를 입력하기 위해 이미지를 Blob 형태로 정제함
                           blob = cv2.dnn.blobFromImage(cv2.resize(frame,(300,300)), 1.0, (300,300), (104.0, 177.0, 123.0))
                           net.setInput(blob)           # 정제된 이미지 입력
                           detections = net.forward()   # 입력 이미지 기반으로 Neural Network 작동
                           compare_confidence_val = 0.5 # 판단 기준 설정

                           # Neural Network를 통해 판독되는 요소들 중에서...
                           for i in range(0, detections.shape[2]):
                                confidence = detections[0, 0, i, 2]

                                # 특정 판단 기준 이상인 경우에 대해서만 처리함
                                if confidence > compare_confidence_val:
                                     box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                                     (startX, startY ,endX, endY) = box.astype("int")
                                     y = startY - 10 if startY - 10 > 10 else startY + 10

                                     # 사람 얼굴이라 인식되는 대상에 대해서만 결과 이미지에 Box를 그림
                                     cv2.rectangle(frame, (startX, startY), (endX, endY), (0,0,255), 2)
                                     gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

                                     ### 사람 코 감지 기능을 이용한 마스크 착용 여부 확인 기능 ###
                                     num="1"
                                     # 얼굴 이미지 요소 중에서 사람 코 감지 시도 #
                                     nose = noseCascade.detectMultiScale(gray,1.3,5)

                                     # 사람 코가 감지되는 게 있는 경우...
                                     if((len(nose)>0)):
                                          current_need_mask = 1 # 현재 이미지 확인 결과 마스크 착용이 필요함
                                     # 사람 코가 감지되는 게 없는 경우...
                                     else:
                                          current_need_mask = 0 # 현재 이미지 확인 결과 마스크 착용 불필요 / 사용자는 이미 마스크 착용

                                     # 영상 인식의 Robust함을 강화하기 위해 프레임간 상태 변화를 기준으로 마스크 착용 권고 여부 결정
                                     # 이전 이미지 프레임과 비교시 현재 마스크 착용에 대해 변화가 있는 경우...
                                     if((prev_need_mask == 0) and (current_need_mask == 1)):
                                          
                                          # 미세먼지 정보 수집 결과 현재 미세먼지 농도가 높다면...
                                          if(NEED_MASK == 1):

                                               # 마스크 박스를 제어하여 마스크를 자동 제공함
                                               ser.write(bytes(num.encode("ascii")))
                                               time.sleep(1)

                                     prev_need_mask = current_need_mask     # 이미지 프레임간 상태 업데이트 

                                     # 코 감지시 결과 이미지에 표시함
                                     for(x,y,w,h) in nose:
                                          cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

                           # 웹캠 수신 영상 전시
                           cv2.imshow('Video Frame', frame)
                           print("Face - Current mask flag : ")
                           print(NEED_MASK)
                           if(cv2.waitKey(1) > 0):break

                 # 프로그램 종료에 따른 윈도우 객체 해제
                 capture.release()
                 cv2.destroyAllWindows()

        else:
             print('Failed to opend video feed')
             sys.exit(0)    # 웹캠 작동 불가 시 프로그램 종료

### Google Geolocation / Geocoding API 기반 사용자 위치 파악 Class ###
class LOCATION:

    def __init__(self):

        global NEED_MASK    # 마스크 착용 권고 전역 변수로 인식 지정
        global lat          # 현위치 위도값 전역 변수로 인식 지정
        global lng          # 현위치 경도값 전역 변수로 인식 지정

        while True:
            print("Devicemart ICT - Default Team / Fine_Dust module")

            ### 현재 위치 정보 갱신 ###
            print("\n\n현재위치를 갱신합니다.\n\n")

            ### 현재 좌표(위도 경도) ###
            URI1 = "https://www.googleapis.com/geolocation/v1/geolocate?key="
            URI1 = URI1 + KEY_LOCATION
            response1 = requests.post(URI1)         # HTTP POST 방식으로 데이터 수신
            result1 = json.loads(response1.text)    # 수신 정보 JSON으로 전환


            lat = float(result1["location"]["lat"])
            lng = float(result1["location"]["lng"])

            #### 현재 위치(주소) ###
            URI2 = "https://maps.googleapis.com/maps/api/geocode/json?latlng="
            URI2 = URI2 + str(lat) + "," + str(lng) + "&key=" + KEY_LOCATION
            response2 = requests.post(URI2)         # HTTP POST 방식으로 데이터 수신
            result2 = json.loads(response2.text)    # 수신 정보 JSON으로 전환

            address = result2["results"][0]["formatted_address"]
            print("현재주소 : " + address)

            ### 현재 주소와 일치하는 지역명을 찾는다 ###
            self.j_AIR = 0
            for _ in result2["results"][0]["address_components"]:
                address_component = result2["results"][0]["address_components"][self.j_AIR]["long_name"]

                if address_component == "Seoul":
                    self.min_distance(0, 25)
                elif address_component == "Gyeonggi-do":
                    self.min_distance(25, 119)
                elif address_component == "Incheon":
                    self.min_distance(119, 139)
                elif address_component == "Gangwon":
                    self.min_distance(139, 160)
                elif address_component == "Chungcheongnam-do":
                    self.min_distance(160, 191)
                elif address_component == "Daejeon":
                    self.min_distance(191, 201)
                elif address_component == "Chungcheongbuk-do":
                    self.min_distance(201, 220)
                elif address_component == "Busan":
                    self.min_distance(220, 242)
                elif address_component == "Ulsan":
                    self.min_distance(242, 259)
                elif address_component == "Daegu":
                    self.min_distance(259, 273)
                elif address_component == "Gyeongsangbuk-do":
                    self.min_distance(273, 307)
                elif address_component == "Gyeongsangnam-do":
                    self.min_distance(307, 339)
                elif address_component == "Jeollanam-do":
                    self.min_distance(339, 376)
                elif address_component == "Gwangju":
                    self.min_distance(376, 385)
                elif address_component == "Jeollabuk-do":
                    self.min_distance(385, 411)
                elif address_component == "Jeju-do":
                    self.min_distance(411, 417)
                elif address_component == "Sejong-si":
                    self.min_distance(417, 421)
                self.j_AIR += 1

            ### 현재 주소와 일치하는 지역명이 없다면 전체 측정도들과 비교한다. ###
            if address_flag == 0:
                self.min_distance(0, 421)

    ### 최소거리 계산 ###
    @staticmethod
    def min_distance(num1, num2):
        global address_flag     # 현재 주소와 일치하는 지역명이 있는지 판단
        global min              # 최소거리 전역 변수 인식
        global min_i            # 현위치 최단경로 측정소 번호 전역 변수 인식

        address_flag = 1

        for i_AIR in range(num1, num2):

            ### 측정소 리스트에 존재하는 위도 경도 ###
            lat3 = float(round(list.Latitude[i_AIR], 6))
            lng3 = float(round(list.Longitude[i_AIR], 6))
            temp = ((lat - lat3) ** 2 + (lng - lng3) ** 2) ** 0.5

            if min > temp:
                min = temp
                min_i = i_AIR

        ### 현위치 최단 경로 측정소 정보를 미세먼지 정보 수집 클래스에 전달 ###
        AIR(min_i)


### 공공데이터 포털 OpenAPI 기반 최단거리 측정소 미세먼지 정보 수집 Class ###
class AIR:

    def __init__(self, min_i):

        ### 미세먼지 데이터 초기화 ###
        print("\n\n미세먼지 데이터를 받아옵니다.\n\n")

        URI_AIR = "http://openapi.airkorea.or.kr/openapi/services/rest/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty?stationName="

        ### 현위치 최단 경로 측정소 ###
        StationName_AIR = list.City_Korea[min_i]
        DataTerm_AIR = "&dataTerm=DAILY"
        PageNo_AIR = "&pageNo=1"

        ### 1부터 최신 10까지 가능 (1시간 단위로 측정, 기록된 값을 불러온다.) ###
        NumOfRows_AIR = "&numOfRows=1"
        Ver_AIR = "&ver=1.3"
        URI_AIR = URI_AIR + StationName_AIR + DataTerm_AIR + PageNo_AIR + NumOfRows_AIR + SERVICE_KEY_AIR + Ver_AIR

        response = requests.get(URI_AIR)
        start = time.time()
        soup = BeautifulSoup(response.text, 'html.parser')
        ItemList = soup.findAll('item')

        ### 미세먼지 정보 출력을 위해 대기오염 정보 및 현재 위치 정보를 전달한다. ###
        self.Info(ItemList, StationName_AIR)
        ### 다음 수신 대기 ###
        self.Waiting(start)

    ### 대기중 ###
    @staticmethod
    def Waiting(start):
        while True:
            end = time.time()

            ### 갱신되는 시간설정 ###
            if end - start >= 10:
                break

    ### 미세먼지 정보 출력 ###
    @staticmethod
    def Info(ItemList, StationName):

        global pm10state, pm25state

        global NEED_MASK

        for item in ItemList:
            print("측정 시간 : " + item.find('datatime').text)
            print("위치 : " + StationName)
            print()

            ### 미세먼지 수치 ###
            pm10 = item.find('pm10value').text
            print("미세먼지 : " + pm10 + " ㎍/㎥")

            ### 미세먼지 등급 판별 ###
            if 0 <= int(pm10) and int(pm10) <= 30:
                pm10state = "좋음"
            elif 31 <= int(pm10) and int(pm10) <= 50:
                pm10state = "보통"
            elif 51 <= int(pm10) and int(pm10) <= 100:
                pm10state = "나쁨"
            elif 101 <= int(pm10):
                pm10state = "매우나쁨"
            print(pm10state)

            ### 초미세먼지 수치 ###
            pm25 = item.find('pm25value').text
            print("초미세먼지 : " + pm25 + " ㎍/㎥")

            ### 초미세먼지 등급 판별 ###
            if 0 <= int(pm25) and int(pm25) <= 15:
                pm25state = "좋음"
            elif 16 <= int(pm25) and int(pm25) <= 25:
                pm25state = "보통"
            elif 26 <= int(pm25) and int(pm25) <= 50:
                pm25state = "나쁨"
            elif 51 <= int(pm25):
                pm25state = "매우나쁨"
            print(pm25state)

            ### 마스크 착용 판단 ###
            if (pm10state or pm25state) == ("나쁨" or "매우나쁨"):
                print("마스크 착용을 권장드립니다.")
                NEED_MASK = 1
            else:
                NEED_MASK = 0

        print("Current mask flag : ")
        print(NEED_MASK)

        
### 미세먼지 정보 수집 기능과 영상 처리 기능에 대해 각각 Thread 생성 ###
t1 = Thread(target=LOCATION)        # 미세먼지 정보 수집 기능 Thread 생성
t2 = Thread(target=FACE_DETECTOR)   # 영상처리 기능 Thread 생성

# 마스크 착용 권고 전역 변수 NEED_MASK를 공유 자원으로 이용하여 기능 연계
t1.start()  # 미세먼지 정보 수집 기능 Thread 작동 시작
t2.start()  # 영상처리 기능 Thread 작동 시작
