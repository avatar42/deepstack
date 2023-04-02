import json
import time
import sys
import shutil
import os
from PIL import Image
import common

# # Note tested with Python 3.9 on Windows
imgCnt = 0
skippedCnt = 0
labeledCnt = 0
unlabeledCnt = 0


# # move files in unlabeled back to new to run again against diff model
def moveLabeled2New():
    imgNames = common.getImgNames(common.unlabeled)
    for fn in imgNames:
        moveNoDebug(common.unlabeled, fn, common.newPicPath)


def moveNoDebug(srcPath, filename, toPath): 
    try:
        if (common.debugPrintOn == "Y"):
            shutil.copy(os.path.join(srcPath, filename), toPath)
        else:
            shutil.move(os.path.join(srcPath, filename), os.path.join(toPath, filename))      
    except PermissionError:
        # in case is race condition try once more
        time.sleep(1)
        if (common.debugPrintOn == "Y"):
            shutil.copy(os.path.join(srcPath, filename), toPath)
        else:
            shutil.move(os.path.join(srcPath, filename), os.path.join(toPath, filename))      
        
        
# # do detect on each pic in common.newPicPath, 
# # if has objects add to label file and move to labeled folder. 
# # If found objects do not exist in common.trainPath + "classes.txt" then they will get added.
# # If no objects found with any model then stick in unlabeled folder for manual processing.
def lablePics():
    global imgCnt
    global labeledCnt
    global unlabeledCnt
    global skippedCnt
        
    common.logStart()
    common.mkdirs(common.labeled)
    common.mkdirs(common.unlabeled)

    if os.path.exists(os.path.join(common.labeled, "classes.txt")): 
        classes = common.readTextFile(os.path.join(common.labeled , "classes.txt")).splitlines()
    else:
        classes = common.readTextFile(os.path.join(common.trainPath , "classes.txt")).splitlines()
    common.dprint(classes)
    
    imgNames = common.getImgNames(common.newPicPath)

    for fn in imgNames:
        newPicName = os.path.join(common.newPicPath , fn)
        common.dprint("Checking:" + newPicName)
        if os.path.exists(os.path.join(common.trainPath, fn)): 
            skippedCnt += 1
            common.skipped(newPicName, 1)
        else:
            tags = []
            for testType in common.tests2Run:
                response = common.doPost(testType, files={"image":common.readBinaryFile(newPicName)})
                common.dprint(response)
                if len(response["predictions"]) > 0:
                    path = os.path.join(common.debugPath, testType + "/")
                    common.mkdirs(path)
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
                        if (common.saveDebugPics == "Y"):
                            common.labelImg(os.path.join(common.debugPath , fn), image, item["label"] + ":" + str(i), x_min, y_min, "green", x_max, y_max)
                            cropped = image.crop((x_min, y_min, x_max, y_max))
                            cropped.save(os.path.join(common.debugPath , fn + "." + label + "." + str(i) + "." + str(item["confidence"]) + ".jpg"))

                        i += 1
 
            common.dprint(tags)
            if len(tags) > 0:
                imgCnt += 1
                labeledCnt += len(tags)
                idx = fn.rfind('.')
                expf = fn[0:idx] + ".txt"
                # write tag file to labeled
                common.writeList(common.labeled , expf, tags)
                # move image to labeled
                common.passed(newPicName)
                moveNoDebug(common.newPicPath , fn, common.labeled)
            else:
                unlabeledCnt += 1
                common.warn("no objects found in " + newPicName + ", moving to common.unlabeled for manual processing")
                # move image to labeled
                moveNoDebug(common.newPicPath , fn, common.unlabeled)
                
    common.writeList(common.labeled , "classes.txt", classes)
    common.writeList("../labelImg/data/" , "predefined_classes.txt", classes)
                
    common.logEnd(common.newPicPath)
    print("Check images in " + common.labeled + " have been labeled automatically.")
    print("Images in " + common.unlabeled + " will have to be labeled manually.")


if len(sys.argv) > 1: 
    if sys.argv[1] == "-h":
        print("USAGE: quickLabel [modelName] [trainPath]")
        print(" where 'modelName' is the model to test images against")
        print(" 'modelName' is required if 'trainPath' is passed.")
        print(" if 'modelName' is passed then it overrides the trainedName and tests2Run settings in common.py")
        print(" if 'trainPath' is passed then it overrides the setting in common.py")
        print("\nDoes the following:")
        print("Checks to see if image is already in 'trainPath', if not then")
        print("Runs the images 'newPath' against the model(s) in tests2Run")
        print("If objects are detected creates a map file for the image in the 'labeled' and moves the file there")
        print("If objects are not detected moves the file to 'unlabeled'")
        print("\nif 'modelName' is passed then also does")
        print(" Runs any images without an object found against detection, openlogo and licence-plate models")
        print(" Runs any images still without an object found against the dark model")
        os._exit(1)
    else:
        common.trainedName = sys.argv[1]
        common.tests2Run = ["custom/" + sys.argv[1]]
        
if len(sys.argv) > 2:
    common.trainPath = sys.argv[2]
    
if not common.trainPath.endswith("/"):
    common.trainPath = common.trainPath + "/"
    
if not common.trainPath.endswith("train/"):
    common.trainPath = os.path.join(common.trainPath, "train/")

if not os.path.exists(common.trainPath):
    raise ValueError(common.trainPath + " does not exist")

print("Using model(s) " + str(common.tests2Run) + " and training files in " + common.trainPath)

if len(sys.argv) > 2:
    common.newPicPath = os.path.join(common.trainPath, "../new/")
    common.labeled = os.path.join(common.trainPath, "../labeled/")
    common.unlabeled = os.path.join(common.trainPath, "../unlabeled/")

print("labeling files in " + common.newPicPath + " and outputing to " + common.labeled + " and " + common.unlabeled)

common.serverUpTest()
common.clearDebugPics()
lablePics()

# # if model passed as arg1 then run images without a detected object against other models
if len(sys.argv) > 1:
    # looks for common objects 
    # common.tests2Run = ["detection", "custom/openlogo", "custom/licence-plate"] 
    common.tests2Run = ["custom/licence-plate"] 
    moveLabeled2New()
    print("Using model(s) " + str(common.tests2Run) + " and training files in " + common.trainPath)
    lablePics()

    ## look for dark objects in what is left
    # common.tests2Run = ["custom/dark"] 
    # moveLabeled2New()
    # print("Using model(s) " + str(common.tests2Run) + " and training files in " + common.trainPath)
    # lablePics()

print("")
print("Of " + str(imgCnt + skippedCnt + unlabeledCnt) + " pics in " + common.newPicPath)
print(" Ignored dup files:" + str(skippedCnt))
print(" Labeled:" + str(labeledCnt) + " objects in " + str(imgCnt) + " files.")
print(" Unlabeled:" + str(unlabeledCnt) + " files.")
print(" Failures:" + str(common.testsFailed))
