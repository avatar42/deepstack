import json
import shutil
import os
from PIL import Image
import config

# # Note tested with Python 3.9 on Windows
imgCnt = 0
skippedCnt = 0
labeledCnt = 0
unlabeledCnt = 0


# # do detect on each pic in config.newPicPath, 
# # if has objects add to label file and move to labeled folder. 
# # If found objects do not exist in config.trainPath + "classes.txt" then they will get added.
# # If no objects found with any model then stick in unlabeled folder for manual processing.
def lablePics():
    global imgCnt
    global labeledCnt
    global unlabeledCnt
    global skippedCnt
        
    config.logStart()
    config.mkdirs(config.labeled)
    config.mkdirs(config.unlabeled)

    if os.path.exists(config.labeled + "classes.txt"): 
        classes = config.readTextFile(config.labeled + "classes.txt").splitlines()
    else:
        classes = config.readTextFile(config.trainPath + "classes.txt").splitlines()
    config.dprint(classes)
    
    imgNames = config.getImgNames(config.newPicPath)

    for fn in imgNames:
        newPicName = config.newPicPath + fn
        config.dprint("Checking:" + newPicName)
        if os.path.exists(config.trainPath + fn): 
            skippedCnt += 1
            config.skipped(newPicName, 1)
        else:
            tags = []
            for testType in config.tests2Run:
                response = config.doPost(testType, files={"image":config.readBinaryFile(newPicName)})
                config.dprint(response)
                if len(response["predictions"]) > 0:
                    path = config.debugPath + testType + "/"
                    config.mkdirs(path)
                    with open(path + fn + ".json", "w") as fout:
                        if fout.mode == "w":
                            fout.write(json.dumps(response, indent=4))

                    image = Image.open(newPicName).convert("RGB")
                    w, h = image.size
                    i = 0
                    for item in response["predictions"]:
                        label = item["label"].lower()
                        try:
                            idx = classes.index(label)
                        except ValueError:
                            classes.append(label)
                            idx = classes.index(label)
                            
                        y_max = int(item["y_max"])
                        y_min = int(item["y_min"])
                        x_max = int(item["x_max"])
                        x_min = int(item["x_min"])
                        x_center = (x_min + (x_max - x_min) / 2) / w   
                        y_center = (y_min + (y_max - y_min) / 2) / h   
                        x_width = (x_max - x_min) / w  
                        y_height = (y_max - y_min) / h
                        # Object ID    x_center    y_center    x_width    y_height
                        tags.append(str(idx) + " " + str(round(x_center, 6)) + " " + str(round(y_center, 6)) + " " + str(round(x_width, 6)) + " " + str(round(y_height, 6)))
                        if (config.saveDebugPics == "Y"):
                            config.labelImg(config.debugPath + fn, image, item["label"] + ":" + str(i), x_min, y_min, "green", x_max, y_max)
                            cropped = image.crop((x_min, y_min, x_max, y_max))
                            cropped.save(config.debugPath + fn + "." + label + "." + str(i) + "." + str(item["confidence"]) + ".jpg")

                        i += 1
 
            config.dprint(tags)
            if len(tags) > 0:
                imgCnt += 1
                labeledCnt += len(tags)
                idx = fn.rfind('.')
                expf = fn[0:idx] + ".txt"
                # write tag file to labeled
                config.writeList(config.labeled , expf, tags)
                # move image to labeled
                config.passed(newPicName)
                shutil.copy(newPicName, config.labeled)
                if (config.debugPrintOn == "N"):
                    os.remove(newPicName)                    
            else:
                unlabeledCnt += 1
                config.warn("no objects found in " + newPicName + ", moving to config.unlabeled for manual processing")
                # move image to labeled
                shutil.copy(newPicName, config.unlabeled)
                if (config.debugPrintOn == "N"):
                    os.remove(newPicName)                    
                
    config.writeList(config.labeled , "classes.txt", classes)
    config.writeList("../labelImg/data/" , "predefined_classes.txt", classes)
                
    config.logEnd(config.newPicPath)
    print("Check images in " + config.labeled + " have been labeled automatically.")
    print("Images in " + config.unlabeled + " will have to be labeled manually.")

    
config.serverUpTest()
config.clearDebugPics()
lablePics()
print("")
print("Of " + str(imgCnt + skippedCnt + unlabeledCnt) + " pics in " + config.newPicPath)
print(" Ignored dup files:" + str(skippedCnt))
print(" Labeled:" + str(labeledCnt) + " objects in " + str(imgCnt) + " files.")
print(" Unlabeled:" + str(unlabeledCnt) + " files.")
print(" Failures:" + str(config.testsFailed))
