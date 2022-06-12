# Identity-Authentication-System
FACE-RECOGNITION-CAPABLE VIDEO SURVEILLANCE SYSTEM

/*DESCRIPTION*/
A system that accepts video input from webcam or camera connected to the computer, perform face detection, face recognition, and identity authentication in real-time. User can monitor the real-time video input and identity authentication results, manage the identity database, and view identity authentication records.


To run system:
1.	Have Python installed in the local computer
2.	Setup MySQL in local system (Window: https://dev.mysql.com/downloads/installer/) 
3.	Install all required packages in requirements.txt (command: pip install -r /path/to/requirements.txt)
4.	Open the folder where the system python files at in an IDE 
5.	Run main.py

To process FDDB dataset for YOLOv5 training:
1.	Download FDDB dataset and annotation from http://vis-www.cs.umass.edu/fddb/ 
2.	Place fddb_preprocess.py, unzipped dataset and annotation in a same file directory
3.	Open fddb_preprocess.py in any IDE
4.	In first run, set data = “train” in main function
5.	In second run, set data = “val” in main function
6.	“datasets” folder will be created
7.	Zip the “datasets” folder

To perform YOLOv5 Training:
1.	Unzip yolov5_training.zip
2.	Upload the yolov5 folder inside which has fddb.yaml into Google Drive
3.	Upload the datasets.zip into the yolov5 folder in Google Drive
4.	Access the FYP_YOLOv5_Training.ipynb from Google Colab
5.	Run the code section by section
6.	Navigate to the folder based on the image below once the training is done, and download the best.pt, then rename it as yolov5_face.pt
7.	Place the yolov5_face.pt into the yolov5 folder extracted from the SYSTEM_SOURCE_CODE.zip (replace previous weight file if necessary)
