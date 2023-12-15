#Dependencies: yolov3_training_last.weights, yolov3_testing.cfg, coco.names
import cv2
import numpy as np


#Load Yolo with trained weights:
net = cv2.dnn.readNet("yolov3_training_last.weights", "yolov3_testing.cfg")

#Name custom object:
classes = ["sky"]

#Layer Details from weights file:
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))

#Loading video stream from URL - RPi Cam's live feed from mjpeg streamer:
# capture = cv2.VideoCapture("http://192.168.1.204:8080/?action=stream")
# capture = cv2.VideoCapture(0)
# capture.set(cv2.CAP_PROP_FRAME_WIDTH, 650)
# capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 750)


iter_no = 1
while True:
    print("Frame: ", iter_no)

    # ret, img = capture.read() #Reading frames from video stream
    img = cv2.imread(f"Test_Images/{iter_no}.jpg")
    img = cv2.resize(img, None, fx=0.8, fy=0.8)
    height, width, channels = img.shape

    #Detecting objects using blob detector in dnn module:
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

    if blob is None:
        print("Blob is empty")
    
    else:
        #Calculating confidence scores and bounding boxes for objects detected:
        net.setInput(blob)
        outs = net.forward(output_layers)

        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.3:
                    #Object detected
                    print(class_id)
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    #Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)


        #Removing overlapping boxes and displaying only one box for each object:
        #Also displaying label and confidence score for each object detected:
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        print(indexes)
        font = cv2.FONT_HERSHEY_PLAIN
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                color = [0, 0, 255]
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                cv2.putText(img, label, (x+30, y + 50), font, 1, color, 2)


        cv2.imshow("Image", img) #Displaying the image with detected objects
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

        cv2.waitKey(0)
        iter_no += 1
        
    

# capture.release()
cv2.destroyAllWindows()