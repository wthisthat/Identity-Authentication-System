import os
import cv2
import shutil

def fddb(data):
    # PARAMETERS
    if data =="train":
        max_images = 2000
        fold = [1,2,3,4,5,6,7,8]
    elif data == "val":
        max_images = 500
        fold = [9,10]

    # original dataset directory and bbox txt path
    image_dir = "./originalPics/"
    bbox_path = "./FDDB-folds/FDDB-folds/"

    # check if the folder exists
    dest_dir = "./datasets/FDDB_yolo/"
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    if data=="train":
        copy_img_dir = dest_dir + "images/train/"
        txt_dir = dest_dir + "labels/train/" 

    elif data=="val":
        copy_img_dir = dest_dir + "images/test/"
        txt_dir = dest_dir + "labels/test/"

    if not os.path.exists(copy_img_dir):
            os.makedirs(copy_img_dir)
    if not os.path.exists(txt_dir):
            os.makedirs(txt_dir)

    total_lines = []
    for f in fold:
        path = bbox_path+"FDDB-fold-"+str(f).zfill(2)+"-ellipseList.txt" # FDDB-fold-01-ellipseList.txt
        # read all lines in txt
        with open(path,"r") as f:
            lines = f.readlines()
        for l in lines:
            total_lines.append(l)

    img_count = 0
    face_count = 0
    # print(total_lines)
    for c,line in enumerate(total_lines):
        # search for .jpg indicate section for each image
        if img_count<max_images:
            if "img" in line:
                img_count += 1
                # img height & width
                ori_img_path = image_dir+line.strip()+".jpg"
                img = cv2.imread(ori_img_path)
                img_height = float(img.shape[0])
                img_width = float(img.shape[1])
                print(line.strip())

                # identify number of faces available
                num_face = int(total_lines[c+1].strip())
                # print(num_face)

                # identify all face bounding box
                bbx_start = c+2
                bbx_end = bbx_start+num_face

                bbx_list = []
                for i in range(bbx_start,bbx_end):
                    face_count += 1
                    bbx_split = total_lines[i].split(" ") #(major axis radius,minor axis radius, angle, center_x ,center_y, 1)
                    # get width,height,center x y
                    # for most face ellipse, y is major axis
                    w = float(bbx_split[1])*2
                    h = float(bbx_split[0])*2
                    # some cases x is major axis
                    if w > img_width or h > img_height:
                        w = float(bbx_split[0])*2
                        h = float(bbx_split[1])*2
                    center_x = float(bbx_split[3])
                    center_y =float(bbx_split[4])

                    # get relative x y w h
                    relative_x_center = str(center_x/img_width)
                    relative_y_center = str(center_y/img_height)
                    relative_w = str(w/img_width)
                    relative_h = str(h/img_height)

                    # get string
                    # Example: 0 0.46634615384615385 0.35096153846153844 0.18028846153846154 0.17548076923076922
                    # class x-center y-center width height
                    str_bbox = "0 " + relative_x_center + " " + relative_y_center + " " + relative_w + " " + relative_h
                    bbx_list.append(str_bbox)
            
                # copy img and rename
                copy_img_path = copy_img_dir + "fddb_" + str(img_count) + ".jpg"
                shutil.copy(ori_img_path,copy_img_path)

                # create responding bounding box txt file for the copied img
                txt_path = txt_dir + "fddb_" + str(img_count) + ".txt"
                with open(txt_path,"a") as f:
                    for bbx in bbx_list:
                        f.write(bbx + '\n')
        else:
            break

    print("total image:",img_count)
    print("total face:",face_count)

if __name__ == "__main__":
    data = "train" # train/val each once
    fddb(data)
