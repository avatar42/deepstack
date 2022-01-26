# # Based on https://gist.github.com/Amir22010/a99f18ca19112bc7db0872a36a03a1ec#convert-pascalvoc-annotations-to-yolo
import os
import xml.etree.ElementTree as ET
import shutil
import config


def convert(size, box):
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


def convert_annotation(filename, classes):
    config.dprint("Converting:" + filename)
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
                    bb = convert((w, h), b)
                    fout.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')
                    config.testsRan += 1
            else:
                raise ValueError("FAILED to open " + txt)
        
        shutil.copy(config.newPicPath + filename, config.labeled)
        config.passed(config.newPicPath + filename)
    else:
        config.skipped(config.newPicPath + filename, 1)
        shutil.copy(config.newPicPath + filename, config.unlabeled)

    return classes
    
    
config.logStart()
config.mkdirs(config.labeled)
config.mkdirs(config.unlabeled)

image_paths = config.getImgNames(config.newPicPath)

classes = []
if os.path.exists(config.labeled + "classes.txt"): 
    classes = config.readTextFile(config.labeled + "classes.txt").splitlines()
    
for filename in image_paths:
    classes = convert_annotation(filename, classes)
    
config.writeList(config.labeled , "classes.txt", classes)

config.logEnd("pascalvoc2yolo")

print("converted " + str(config.testsRan) + " labels in " + str(config.testsPassed) + " images, " + str(config.testsSkipped) + " had no mapping data so were skipped and placed in " + config.unlabeled)
