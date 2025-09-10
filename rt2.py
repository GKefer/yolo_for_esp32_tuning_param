import cv2
import matplotlib.pyplot as plt
import cvlib as cv
import urllib.request
import numpy as np
from cvlib.object_detection import draw_bbox
import concurrent.futures
import time
import asyncio
import websockets
import json
import math
from PIL import Image, ImageGrab

url=['http://192.168.102.214/cam-hi.jpg','http://192.168.102.122/cam-hi.jpg']
im=None
last_hight = 0
last_wight = 0
last_cat_top = 0
last_cat_down = 0
last_cat_left = 0
last_cat_right = 0
targetrate = False
losecom = 0
fatchcom = 0

message={"label":["cat","mouse","red"],"bbox":[[1,2,3],[4,5,6],[7,8,9]],"server":'A'}


def calu(label,bbox,ser):
     shape=0
     global last_wight,last_hight,losecom,fatchcom,targetrate
     for i in label:
        if i=="cat":
             losecom = 0
             fatchcom += 1
             if targetrate:
                  if(fatchcom>1):
                       fatchcom=0
                       if(bbox[shape][2]-bbox[shape][0]>380 and bbox[shape][3]-bbox[shape][1]>480 ):
                            print("cat is near the cam,take care of your belongings")
                            print("------------")
                       if( ((bbox[shape][3]-bbox[shape][1])-last_wight)<=20 and ((bbox[shape][2]-bbox[shape][0])-last_hight)<=20 ) :
                            print("The cat is stand over there.")
                            print("------------")
                            continue
                       if(abs(bbox[shape][2]-bbox[shape][0]-last_wight)>50 or abs(bbox[shape][3]-bbox[shape][1]-last_hight)>50):
                            print("cat was moving")
                            print("------------")
                       if( (last_wight+last_hight) < (bbox[shape][3]-bbox[shape][1] + bbox[shape][2]-bbox[shape][0]) ):
                            print("cat is nearing the bottle.")
                            print("------------")
                       if( (last_wight+last_hight) > (bbox[shape][3]-bbox[shape][1] + bbox[shape][2]-bbox[shape][0]) ):
                            print("The cat is going away from the bottle.")
                            print("------------")
                       last_wight=bbox[shape][3]-bbox[shape][1]
                       last_hight=bbox[shape][2]-bbox[shape][0]
                            

             else:
                  targetrate = True
                  print("a cat detected on camera",ser)
        shape+=1     
     losecom+=1
     if targetrate and losecom>20:
          print("didn't detect the cat")
          losecom = 0
          targetrate = False




async def hello(uri,label,bbox,str):
	async with websockets.connect(uri) as websocket:
		await websocket.send(json.dumps({"label":label,"bbox":bbox,"server":str}))
		print("send to server")
		name = await websocket.recv()
		print(name)
 
'''def run1():
    cv2.namedWindow("live transmission", cv2.WINDOW_AUTOSIZE)
    while True:
        img_resp=urllib.request.urlopen(url)
        imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
        im = cv2.imdecode(imgnp,-1)
 
        cv2.imshow('live transmission',im)
        key=cv2.waitKey(5)
        if key==ord('q'):
            break
            
    cv2.destroyAllWindows()
'''
def run2():
    cv2.namedWindow("detection", cv2.WINDOW_AUTOSIZE)
    while True:
        img_resp=urllib.request.urlopen(url[0])
        imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
        im = cv2.imdecode(imgnp,-1)
        bbox, label, conf = cv.detect_common_objects(im)
        im = draw_bbox(im, bbox, label, conf)
        calu(label,bbox,"A")
        
        cv2.imshow('detection',im)
        #asyncio.get_event_loop().run_until_complete(hello('ws://192.168.102.219:8765',label,bbox,'A'))
        key=cv2.waitKey(5)
        if key==ord('q'):
            break
            
    cv2.destroyAllWindows()
    
 
def run3():
    cv2.namedWindow("detection", cv2.WINDOW_AUTOSIZE)
    while True:
        img_resp=urllib.request.urlopen(url[1])
        imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
        im = cv2.imdecode(imgnp,-1)
        bbox, label, conf = cv.detect_common_objects(im)
        im = draw_bbox(im, bbox, label, conf)
        calu(label,bbox,"B")

        cv2.imshow('detection',im)
        #asyncio.get_event_loop().run_until_complete(hello('ws://192.168.102.219:8765',label,bbox,'B'))
        key=cv2.waitKey(5)
        if key==ord('q'):
            break
            
    cv2.destroyAllWindows()


          



        
 
if __name__ == '__main__':
    print("started")
    with concurrent.futures.ProcessPoolExecutor() as executer:
            #f1= executer.submit(run1)
            f2= executer.submit(run2)
            f2= executer.submit(run3)
