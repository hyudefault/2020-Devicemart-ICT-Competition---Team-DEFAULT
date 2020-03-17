import numpy as np
import os
import sys
import cv2

import time
import serial


noseCascade = cv2.CascadeClassifier('haarcascade_mcs_nose.xml')

prev_need_mask = 0;
current_need_mask = 0;

num="0"
ser=serial.Serial("/dev/ttyACM0",9600)

print('Face detection for video images using OpenCV DNN Module')
protopath = '/home/pi/Downloads/deploy.prototxt'
modelpath = '/home/pi/Downloads/res10_300x300_ssd_iter_140000.caffemodel'

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
						if(len(nose)>0):
							current_need_mask = 1
							if((prev_need_mask == 0) and (current_need_mask == 1)):
								ser.write(bytes(num.encode("ascii")))
								time.sleep(1)
							prev_need_mask = current_need_mask
						#Draw a rectangle around the nose

						for(x,y,w,h) in nose:
							cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
				cv2.imshow('Video Frame', frame)
				if(cv2.waitKey(1) > 0):break
		capture.release()
		cv2.destroyAllWindows()

else:
	print('Failed to opend video feed')
	sys.exit(0)
