from datetime import datetime
from facenet_pytorch import InceptionResnetV1
from sklearn.neighbors import NearestNeighbors
import torchvision.transforms as transforms
import joblib
import pickle
import numpy as np
import cv2

class FaceRecognizer:

    def __init__(self,db):
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval()
        self.transform = transforms.ToTensor() # to pytorch tensor
        # database class instantiation
        self.db = db

    def encoding(self, crop_face):
        # resize 
        resized_crop_face = cv2.resize(crop_face,(160,160))
        # to pytorch tensor
        crop_tensor = self.transform(resized_crop_face)
        # obtain encoding
        encoding = self.resnet(crop_tensor.unsqueeze(0))
        # convert to numpy
        np_encoding = encoding.detach().numpy()
        
        return np_encoding
    
    def recognizer(self, detected_encoding):
        # load Nearest Neighbor model from local file
        nn = joblib.load('nn.joblib')
        # obtain all data in identity table
        res = self.db.load_identity()
        # set default values
        id = None
        name = "Unknown"
        distance = None
        recognized = False
        
        # check database is not empty
        if res:
            # return the identity with minimum distance
            dist, index = nn.kneighbors(detected_encoding)
            # extract numerical values from 2d list
            dist = dist[0][0]
            ind = index[0][0]
            print(f"distance: {dist}, index: {index}")
            # set face recognition threshold
            if dist < 0.95:
                id = res[ind][0]
                name = res[ind][1]
                distance = round(float(dist),4)
                recognized = True
        # timestamp
        timestamp = datetime.now()
        
        return id, name, distance, timestamp, recognized

    def nn_train(self):
        # load data from identity table
        res = self.db.load_identity()
        # check res is not empty
        if res:
            encodings = []
            # extract encoding data from every row and append accordingly
            for r in res:
                depickled = pickle.loads(r[3])
                encodings.append(depickled.flatten())
            
            # convert list to numpy array
            data = np.array(encodings)
            # initiliaze Nearest Neighbor model with k value=1
            neigh = NearestNeighbors(n_neighbors=1)
            # fit in training data
            neigh.fit(data)
            # download model locally
            joblib.dump(neigh, 'nn.joblib')
