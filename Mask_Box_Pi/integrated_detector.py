import numpy as np
import os
import sys
import cv2

import time
import serial

##############################################################

from bs4 import BeautifulSoup
import requests
import time
from threading import Thread
import json
import pandas as pd

### LOCATION ###

list = pd.read_excel('list.xlsx')
key = pd.read_excel('key.xlsx')

KEY_LOCATION = key.KEY_LOCATION[0]
SERVICE_KEY_AIR = key.SERVICE_KEY_AIR[0]


# 최소거리

address_flag = 0
min = 10000.0
min_i = 0.0

###########################################################

from threading import Thread

NEED_MASK = 0

##########################################################

class FACE_DETECTOR:

    def __init__(self):

        global NEED_MASK
        
        print("Devicemart ICT - Default Team / Face_detector module")

        noseCascade = cv2.CascadeClassifier('./face_detect_model/haarcascade_mcs_nose.xml')

        prev_need_mask = 0;
        current_need_mask = 0;

        num="0"
        ser=serial.Serial("/dev/ttyACM0",9600)

        print('Face detection for video images using OpenCV DNN Module')
        protopath = './face_detect_model/deploy.prototxt'
        modelpath = './face_detect_model/res10_300x300_ssd_iter_140000.caffemodel'

        capture = cv2.VideoCapture(0)

        if(capture.isOpened()):
            print('Video cam is available')
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            net = cv2.dnn.readNetFromCaffe(protopath, modelpath)

            if(net is None):
                 print('Failed to load Neural Net')
                 sys.exit(0)

            elif(net is not None):
                 print('Neural Net ready')
                 
                 while(capture.isOpened()):
                      ret, frame = capture.read()

                      if(ret == True):
	
                           (h, w) = frame.shape[:2]
                           blob = cv2.dnn.blobFromImage(cv2.resize(frame,(300,300)), 1.0, (300,300), (104.0, 177.0, 123.0))
                           net.setInput(blob)
                           detections = net.forward()
                           compare_confidence_val = 0.5

                           for i in range(0, detections.shape[2]):
                                confidence = detections[0, 0, i, 2]
	
                                if confidence > compare_confidence_val:
                                     box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                                     (startX, startY ,endX, endY) = box.astype("int")
                                     y = startY - 10 if startY - 10 > 10 else startY + 10
                                     cv2.rectangle(frame, (startX, startY), (endX, endY), (0,0,255), 2)
                                     gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
								
                                     #Nose detection
                                     num="1"
                                     nose = noseCascade.detectMultiScale(gray,1.3,5)

                                     if((len(nose)>0)):
                                          current_need_mask = 1
                                     else:
                                          current_need_mask = 0

                                     if((prev_need_mask == 0) and (current_need_mask == 1)):
                                          if(NEED_MASK == 1):
                                               ser.write(bytes(num.encode("ascii")))
                                               time.sleep(1)

                                     prev_need_mask = current_need_mask

                                     #Draw a rectangle around the nose
                                     for(x,y,w,h) in nose:
                                          cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

                           cv2.imshow('Video Frame', frame)
                           print("Face - Current mask flag : ")
                           print(NEED_MASK)
                           if(cv2.waitKey(1) > 0):break

                 capture.release()
                 cv2.destroyAllWindows()

        else:
             print('Failed to opend video feed')
             sys.exit(0)

class LOCATION:

    def __init__(self):

        global NEED_MASK

        print("Devicemart ICT - Default Team / Fine_Dust module")

        print("\n\n현재위치를 갱신합니다.\n\n")

        # 현재 좌표(위도 경도)
        URI1 = "https://www.googleapis.com/geolocation/v1/geolocate?key="
        URI1 = URI1 + KEY_LOCATION
        response1 = requests.post(URI1)
        result1 = json.loads(response1.text)
        global lat
        global lng

        lat = float(result1["location"]["lat"])
        lng = float(result1["location"]["lng"])

        # 현재 위치(주소)
        URI2 = "https://maps.googleapis.com/maps/api/geocode/json?latlng="
        URI2 = URI2 + str(lat) + "," + str(lng) + "&key=" + KEY_LOCATION
        response2 = requests.post(URI2)
        result2 = json.loads(response2.text)

        address = result2["results"][0]["formatted_address"]
        print("현재주소 : " + address)

        for _ in result2["results"][0]["address_components"]:
            address_component = result2["results"][0]["address_components"][self.j_AIR]["long_name"]

            # print(address_component)

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

        if address_flag == 0:
            self.min_distance(0, 421)



    @staticmethod
    def min_distance(num1, num2):
        global address_flag
        global min
        global min_i
        address_flag = 1


        for i_AIR in range(num1, num2):
            # print(i_AIR)
            lat3 = float(round(list.Latitude[i_AIR], 6))
            lng3 = float(round(list.Longitude[i_AIR], 6))
            temp = ((lat - lat3) ** 2 + (lng - lng3) ** 2) ** 0.5

            if min > temp:
                min = temp
                min_i = i_AIR
        #print()
        #print()
        #print("측정소 위치 : " + list.Station_Korea[min_i])
        #print(min_i)

        AIR(min_i)

        # endtime = time.time()
        # print(endtime-starttime)

    j_AIR = 0




### FINE_AIR ###


flag_SYS = 0


class AIR:

    def __init__(self, min_i):

        print("\n\n미세먼지 데이터를 받아옵니다.\n\n")

        #print("min_i : ")
        #print(min_i)
        URI_AIR = "http://openapi.airkorea.or.kr/openapi/services/rest/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty?stationName="
        StationName_AIR = list.City_Korea[min_i]
        DataTerm_AIR = "&dataTerm=DAILY"
        PageNo_AIR = "&pageNo=1"
        NumOfRows_AIR = "&numOfRows=1"  # 1 최신, 10 마지막
        Ver_AIR = "&ver=1.3"
        URI_AIR = URI_AIR + StationName_AIR + DataTerm_AIR + PageNo_AIR + NumOfRows_AIR + SERVICE_KEY_AIR + Ver_AIR
        # print(URI)


        response = requests.get(URI_AIR)
        # print(response.text)
        start = time.time()
        soup = BeautifulSoup(response.text, 'html.parser')
        ItemList = soup.findAll('item')

        self.Info(ItemList, StationName_AIR)
        self.Waiting(start)
        if flag_SYS == 0:
            LOCATION()

    @staticmethod
    def Waiting(start):
        while True:
            end = time.time()
            if flag_SYS == 1:
                break
            if end - start >= 10:
                # print("30분 경과했습니다.")
                break

    @staticmethod
    def Info(ItemList, StationName):

        global pm10state, pm25state

        global NEED_MASK

        for item in ItemList:
            print("측정 시간 : " + item.find('datatime').text)
            print("위치 : " + StationName)
            print()

            # 미세먼지
            pm10 = item.find('pm10value').text
            print("미세먼지 : " + pm10 + " ㎍/㎥")
            if 0 <= int(pm10) and int(pm10) <= 30:
                pm10state = "좋음"
            elif 31 <= int(pm10) and int(pm10) <= 50:
                pm10state = "보통"
            elif 51 <= int(pm10) and int(pm10) <= 100:
                pm10state = "나쁨"
            elif 101 <= int(pm10):
                pm10state = "매우나쁨"
            print(pm10state)

            # 초미세먼지
            pm25 = item.find('pm25value').text
            print("초미세먼지 : " + pm25 + " ㎍/㎥")
            if 0 <= int(pm25) and int(pm25) <= 15:
                pm25state = "좋음"
            elif 16 <= int(pm25) and int(pm25) <= 25:
                pm25state = "보통"
            elif 26 <= int(pm25) and int(pm25) <= 50:
                pm25state = "나쁨"
            elif 51 <= int(pm25):
                pm25state = "매우나쁨"
            print(pm25state)

            if (pm10state or pm25state) == ("나쁨" or "매우나쁨"):
                print("마스크 착용을 권장드립니다.")
                NEED_MASK = 1
            else:
                NEED_MASK = 0

        print("Current mask flag : ")
        print(NEED_MASK)

def Exit():
    while True:
        if input() == "exit":
            global flag_SYS
            print("program exited")
            flag_SYS = 1
            break

t1 = Thread(target=LOCATION)
t2 = Thread(target=FACE_DETECTOR)

t1.start()
t2.start()
