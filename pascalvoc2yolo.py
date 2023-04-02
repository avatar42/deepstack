""" 
Based on https://gist.github.com/Amir22010/a99f18ca19112bc7db0872a36a03a1ec#convert-pascalvoc-annotations-to-yolo
Convert a folder of pascalvoc label files to YOLOv5 files.
"""

import os
import shutil
import sys

from common import dprint, getImgNames, \
    skipped, mkdirs, passed, \
    incTestRan, readTextFile, writeList, \
    setPaths, getTestRan, getTestsPassed, getTestsSkipped
import config
import xml.etree.ElementTree as ET


class Pascalvoc2yolo():

    def convert(self, size, box):
        dw = 1. / (size[0])
        dh = 1. / (size[1])
        x = (box[0] + box[1]) / 2.0 - 1
        y = (box[2] + box[3]) / 2.0 - 1
        w = box[1] - box[0]
        h = box[3] - box[2]
        x = x * dw
        w = w * dw
        y = y * dh
        h = h * dh
        return (x, y, w, h)
    
    def convert_annotation(self, filename, classes):
        dprint("Converting:" + filename)
        idx = filename.rfind('.')
        basename = filename[0:idx]
    
        txt = config.labeled + basename + ".txt"
        xml = config.newPicPath + basename + ".xml"
    
        if os.path.exists(xml): 
            in_file = open(xml)
            tree = ET.parse(in_file)
            root = tree.getroot()
            size = root.find('size')
            w = int(size.find('width').text)
            h = int(size.find('height').text)
        
            with open(txt, "w") as fout:
                if fout.mode == "w":
                    for obj in root.iter('object'):
                        cls = obj.find('name').text
                        if cls not in classes:
                            classes.append(cls)
                        cls_id = classes.index(cls)
                        xmlbox = obj.find('bndbox')
                        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
                        bb = self.convert((w, h), b)
                        fout.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')
                        incTestRan()
                else:
                    raise ValueError("FAILED to open " + txt)
            
            shutil.copy(config.newPicPath + filename, config.labeled)
            passed(config.newPicPath + filename)
        else:
            skipped(config.newPicPath + filename, 1)
            shutil.copy(config.newPicPath + filename, config.unlabeled)
    
        return classes
        
    def run(self, argv=[]): 
        if len(argv) > 1: 
            if argv[1] == "-h":
                print("USAGE: pascalvoc2yolo [inputFolderPath] [outputFolderPath]")
                print(" where 'inputFolderPath' is the folder with images with their pascalvoc maps in it")
                print(" where 'outputFolderPath' is the folder where yolov5 maps will be put")
                print(" if 'inputFolderPath' is not passed then it uses the 'newPicPath' settings in common.py")
                print(" if 'outputFolderPath' is not passed then it uses inputFolderPath/../labeled")
                print(" if 'outputFolderPath' is passed then 'inputFolderPath' is required")
                return
            else:
                setPaths("", argv[1])
                
        if len(argv) > 2:
            config.labeled = argv[2]
            config.unlabeled = os.path.join(config.labeled, "../unlabeled")
            
        mkdirs(config.labeled)
        mkdirs(config.unlabeled)
        
        image_paths = getImgNames(config.newPicPath)
        if len(image_paths) > 0:
        
            classes = []
            if os.path.exists(config.labeled + "classes.txt"): 
                classes = readTextFile(config.labeled + "classes.txt").splitlines()
                
            for filename in image_paths:
                classes = self.convert_annotation(filename, classes)
                
            writeList(config.labeled , "classes.txt", classes)
                        
            print("\nconverted " + str(getTestRan()) + " labels in " + str(getTestsPassed()) + " images, " + str(getTestsSkipped()) + " had no mapping data so were skipped and placed in " + config.unlabeled)


Pascalvoc2yolo().run(sys.argv)
