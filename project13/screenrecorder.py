import cv2 
import pyautogui 
from win32api import GetSystemMetrics 
import numpy as np 
import time 
width = GetSystemMetrics(0)
height = GetSystemMetrics(1)
dimension = (width,height)
format = cv2.VideoWriter_fourcc(*"XVID")
output = cv2.VideoWriter("test.mp4",format,30.0,dimension)
now_time = time.time()
dur = 10
end_time = now_time+dur 
while True:
    image = pyautogui.screenshot()
    frame_1 = np.array(image)
    frame = cv2.cvtColor(frame_1,cv2.COLOR_BGR2RGB)    
    output.write(frame)
    curr_time = time.time()
    if curr_time > end_time :
        break   
output.release()
print("---SaVe---")    
