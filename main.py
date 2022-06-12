from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import database, recognition, detection, user_interface
from sort import Sort

# Webcam Initialization
def webcam_init(width,height):
    cap = cv2.VideoCapture(0) # cv2.CAP_DSHOW
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    width  = cap.get(3)
    height = cap.get(4)
    print("Width: " + str(width),", Height: " + str(height))
    return cap

# Video Capturing
def video_capture():
    if cap.isOpened():
        test = True
        # capture frame by frame
        success, frame = cap.read()
        # clone frame for processing and display, original frame for obtaining clean image
        clone_frame = frame.copy()
        if success :
            # call detect function and obtain all bounding boxes of available faces
            bbox_list = face_detector.detect(clone_frame)
            det = []
            predict = []
            # recognition
            for bbox in bbox_list:
                # face bounding box
                x1,y1,x2,y2 = bbox[0],bbox[1],bbox[2],bbox[3]
                det.append((x1,y1,x2,y2,1))
            
            # check if face detected
            if det:
                # feed in detected face list as input to sort function
                predict=tracker.update(np.array(det))
                for pre in predict:
                    # extract bounding box, and tracking id generated using sort
                    x1, y1, x2, y2, track_id=int(pre[0]),int(pre[1]),int(pre[2]),int(pre[3]),int(pre[4])
                    # draw rectangle on face and display tracking id
                    cv2.rectangle(clone_frame,(x1,y1) ,(x2,y2), (0,255,0), 2)
                    cv2.putText(clone_frame, str(track_id), (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                    # if current tracking id is not authenticated before, perform identity authentication
                    if track_id not in recognized_list:
                        try:
                            # crop face
                            crop_face = frame[y1:y2, x1:x2]
                            # resize 
                            resized_crop_face = cv2.resize(crop_face,(85,85))
                            # obtain encoding for detected face
                            encoding = face_recognition.encoding(crop_face)
                            # call recognizer to authenticate identity
                            id, name, distance, timestamp, recognized= face_recognition.recognizer(encoding)
                            recognized_list.append(track_id)
                            # add authentication record and display results on dashboard
                            db.add_record(timestamp,recognized,distance,id)
                            gui.disp_recog_results(resized_crop_face,name,distance,timestamp)
                        except:
                            continue

            # display processed webcam frame
            img = Image.fromarray(cv2.cvtColor(clone_frame, cv2.COLOR_BGR2RGB))
            # set delay time to decrease the frames per second (1000ms/125ms = 8 fps)
            cv2.waitKey(0)
    else:
        test = False
        black = np.zeros((720,1280,3),np.uint8)
        img = Image.fromarray(cv2.cvtColor(black, cv2.COLOR_BGR2RGB))
    
    # set label image to display real-time video
    imgtk = ImageTk.PhotoImage(image=img)
    disp.imgtk = imgtk
    disp.configure(image=imgtk)
    if test:
        gui.window.after(1, video_capture)
    else:
        messagebox.showwarning("Warning","No camera detected! Real-time identity authentication will be disabled.")

if __name__ == "__main__":
    # empty recognized list for face-tracked authentication
    recognized_list = []
    # Sort Instantiation
    tracker = Sort()
    # Database Instantiation
    db = database.Database()
    # Yolov5 Instantiation
    face_detector = detection.FaceDetector(r'yolov5\yolov5_face.pt')
    # FaceNet Instantiation
    face_recognition = recognition.FaceRecognizer(db=db)
    # GUI Instantiation
    gui = user_interface.GUI(face_detector=face_detector,face_recognition=face_recognition,db=db)
    disp = gui.dashboard()
    # Webcam Initialization
    cap = webcam_init(width=1280,height=720) # 640x480
    # Real-time webcam capturing with face detector and recognition
    video_capture()
    # GUI loop
    gui.window.mainloop()
