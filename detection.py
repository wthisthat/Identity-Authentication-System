import torch
import cv2

class FaceDetector:

    def __init__(self, weights_path):
        self.model = torch.hub.load('yolov5', 'custom', path=weights_path, source='local', force_reload=True) 
        self.model.conf = 0.65 # Confidence threshold
        self.model.iou = 0.5 # IoU threshold
        self.model.max_det = 10 # Maximum number of detection

    def detect(self, frame):
        # apply yolov5 model
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.model(rgb_frame)

        # convert to dataframe
        res = results.pandas().xyxy[0]
        # face count and annotation
        det_face_count = "Face count: " + str(len(res))
        cv2.putText(frame, det_face_count, org=(10, 30), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0,255,0), thickness=2)

        # declare empty list
        bbox_list = []

        for index, row in res.iterrows():
            x1 = int(row.xmin)
            y1 = int(row.ymin)
            x2 = int(row.xmax)
            y2 = int(row.ymax)
            
            # append all available face into list
            bbox_list.append([x1,y1,x2,y2])

        return bbox_list