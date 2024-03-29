import numpy as np
import cv2


# Create a VideoCapture object
cap = cv2.VideoCapture(1)
#This is a function form opencv that is used for capturing video from camera
#The parameter 1 specifies which camera to use (O would also be possible for a single camera)


#This is the Width-Height-Threshold parameter,
whT = 320
confThreshold = 0.5
nmsThreshold = 0.3

classesFile = 'coco.names'  #File that contains the names of the objects that can be detected

classNames = []

#Opening the text file for reading (rt)
with open(classesFile,'rt') as f:  
    classNames = f.read().rstrip('\n').split('\n')
#print(classNames)
#print(len(classNames))

modelConfiguration = 'yolov3-320.cfg' #This config is a yolov3 model with a image size of 320x320
modelWeights = 'yolov3.weights'

#net : the loaded model
net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights) # This loads and initializes a deep neural network model from Darknet
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU) # The target is the hardware (CPU) platform that is used to perform computations for the DNN model. 

def findObjects(outputs, img):
    hT, wT, cT = img.shape
    bbox = []

    classIds = []
    confs = []

    for output in outputs:
        for det in output:
            scores = det[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confThreshold:
                w,h = int(det[2]*wT) , int(det[3]*hT)
                x,y = int((det[0]*wT) - w/2), int((det[1]*hT) - h/2)
                bbox.append([x,y,w,h])
                classIds.append(classId)
                confs.append(float(confidence))
    indices = cv2.dnn.NMSBoxes(bbox,confs,confThreshold,nmsThreshold)
    l=[]
    for i in indices:
        i = i[0]
        box = bbox[i]
        x,y,w,h = box[0],box[1],box[2],box[3]
        if classNames[classIds[i]] == 'person':
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,255),2)
            cv2.putText(img,f'{classNames[classIds[i]].upper()} {int(confs[i]*100)}%',
                        (x,y-10),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,0,255),2)
            l.append(i)
    cv2.putText(img, f'le nombre de personnes est : {len(l)}',
                (10, 450), cv2.FONT_ITALIC, 0.6, (255, 255, 255), 2)



while True:
    succeess, img = cap.read()

    blob = cv2.dnn.blobFromImage(img, 1/255, (whT,whT),[0,0,0],1,crop=False)
    net.setInput(blob)

    layerNames = net.getLayerNames()
    #print(layerNames)
    outputNames = [layerNames[i[0]-1] for i in net.getUnconnectedOutLayers()]
    #print(outputNames)

    outputs = net.forward(outputNames)
    #print(type(outputs[0].shape))
    #print(type(outputs[1].shape))
    #print(outputs[0][0])
    findObjects(outputs,img)






    cv2.imshow('Image',img)
    cv2.waitKey(1)
    #cv2.destroyAllWindows()
    if cv2.getWindowProperty("Image", 1) == -1:
        break
