import os
import cv2
import numpy as np
import json

detect_path = '/prj0129/mil4012/glaucoma/Figure_segmentation/runs/detect/exp15/labels'
# save_path = '/prj0129/mil4012/glaucoma/Figure_segmentation/edema'
# jason_path = '/prj0129/mil4012/glaucoma/PMCFigureX/bioc3'
# detect_list = os.listdir(detect_path)

total =0
g = os.walk("/prj0129/mil4012/glaucoma/PMCFigureX/bioc3")
for path,d,filelist in g:
     for filename in filelist:
        if filename.endswith('jpg'):
            im = cv2.imread(os.path.join(path, filename))
            image_size = np.shape(im)
            #json file save path
            json_path = os.path.join(path, (filename[:-4]+'.json'))
            
            #load the detection result
            detect_inf = np.loadtxt(os.path.join(detect_path,(filename[:-4]+'.txt')),ndmin=2)
            
            outboxes = []
            for j in range(len(detect_inf)):
                detect_in = detect_inf[j]
                a = detect_in[1]
                b = detect_in[2]
                c = detect_in[3]
                d = detect_in[4]
                prob = detect_in[5]
                xtl = int(round((2*a - c) * image_size[1]))
                ytl = int(round((2*b - d) * image_size[0])) 
                w = int(round(c * image_size[1]))
                h = int(round(d * image_size[0]))
                outboxes.append({"x": xtl, "y": ytl, "w": w, "h": h, "conf": float(prob)})
            json.dump(outboxes, open(json_path, 'w'))
            total += 1
    
print('the total is', total)  

  