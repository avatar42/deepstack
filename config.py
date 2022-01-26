import json
import sys
from datetime import datetime
import requests
import os
import shutil
from PIL import Image, ImageFont, ImageDraw

# Configuration options and common methods for DeepStack utils
# # note trailing / on folder names
# # Base URL of your DeepStack server
dsUrl = "http://localhost:82/"
# # DeepStack started with -e MODE=Medium or -e MODE=High
mode = "Medium" 
# # Where images to test with are located
imgPath = "test.imgs/"
# # Where to save debug images of from tests 
debugPath = "debug.pics/"
# # path to labeled training pics. (may be overwritten by some command line options)
trainPath = "train/"
# # unlabeled / new file folder
# newPicPath = "D:/odrive/GD.video/cams/DeepStackWS/data/new/"
newPicPath = "new/"
# # Name of trained set model. Usually the same as the name of the pt file.
# # RMRR is mine from the data in the checked in trainData folder. If you train your own replace the train folder in trainData with your own. 
# # (may be overwritten by some command line options)
# trainedName = "RMRR" 
trainedName = "fire"  
# # folder where images with found objects and their mapping files are put by quickLabel and read by chkClasses
labeled = "labeled/"
# # folder where images with not found objects are put by quickLabel and read by chkClasses
unlabeled = "unlabeled/"
# # where LabelImg in installed /cloned relative to my deepstack repo
labelImgData = "../labelImg/data"

# # Output debug info Y,N Note if Y also causes a copy instead of a move of some files
debugPrintOn = "N"
# # if Y saves debug images to compare between expected and found objects for mismatches.
saveDebugPics = "Y"
# # Y=Fail on error, N=Just warn on error
failOnError = "N"
# 
min_confidence = 0.50
# Supported images suffixes to look for in folders
includedExts = ['jpg', 'webp', 'bmp', 'png', 'gif']

# # installed models to use to find objects
# # detection the built in model
# # [openlogo custom model](https://github.com/OlafenwaMoses/DeepStack_OpenLogo).
# # [licence-plate custom model](https://github.com/odd86/deepstack_licenceplate_model).
# # [dark custom model](https://github.com/OlafenwaMoses/DeepStack_ExDark).
# # [actionnetv2 custom model](https://github.com/OlafenwaMoses/DeepStack_ActionNET).
#tests2Run = ["custom/"+trainedName] 
tests2Run = ["detection", "custom/openlogo", "custom/licence-plate", "custom/dark", "custom/actionnetv2"] 

imgCnt = 0
testsRan = 0
testsSkipped = 0
testsFailed = 0
testsPassed = 0
testsWarned = 0
progressCnt = 0
startCnt = 0
startTime = datetime.now()


# # if config.debugPrintOn == "N" prints a '.' wrapped at 80 columns
def progressPrint():
    global progressCnt

    progressCnt += 1
    # if progressCnt >= 80:
    #     sys.stdout.write('\r')
    #     progressCnt = 0
    sys.stdout.write('.')


# # log tests as skipped        
def skipped(msg, skipped):
    global testsSkipped
    
    testsSkipped += skipped
    dprint("Skipped " + str(skipped) + " " + msg)


# # if config.debugPrintOn == "Y" adds new line to log so progress dots do not make messages appear off screen 
def addNL():
    global progressCnt

    if progressCnt > 0:
        print("")
        progressCnt = 0


# single point to turn off all the debug messages 
def dprint(msg):
    global progressCnt

    if debugPrintOn == "Y":
        if progressCnt > 0:
            print("")
            progressCnt = 0

        print(msg)


# # if failOnError == "Y" ends testing with message
# # if failOnError == "N" calls warn with msg
def fail(msg):
    global testsFailed
    
    addNL()
    testsFailed += 1
    if failOnError == "Y":
        raise ValueError("FAILED:" + msg)
    else:
        addNL()    
        sys.stderr.write("\nFAILED:" + msg + "\n")


# # write msg to stderr
def warn(msg):
    global testsWarned
    
    addNL()    
    testsWarned += 1
#    sys.stderr.write("WARN:" + msg + "\n")
    sys.stderr.write("\n" + msg + "\n")


# # if config.debugPrintOn == "Y" prints PASSED: msg otherwise a '.'
def passed(msg):
    global testsPassed
    
    testsPassed += 1
    if debugPrintOn == "Y":
        addNL()
#        print("PASSED:" + str(msg))
        print(str(msg))
    else:
        progressPrint()


# # initialize vars for test counting and timing    
def logStart():
    global startCnt
    global startTime
    global testsRan

    startCnt = testsRan
    startTime = datetime.now()


# # output info about the test set just run
def logEnd(testType):
    global startCnt
    global startTime
    global testsRan
    global testsSkipped

    print("\nRan " + str(testsRan - startCnt) + " " + testType + " tests in " + str(datetime.now() - startTime))
    # print("\nProcessed " + str(testsRan) + " mapping files, " + str(testsSkipped) + " could not be processed in " + str(datetime.now() - startTime))


# # if test is true run method
# # if test is false add tests to skip count.
def logit(test, method, msg, skipCnt):
    if test: 
        method()
    else:
        skipped(msg, skipCnt)


# # if test is true call passed
# # if test is false call fail
def assertTrue(msg, test):
    global testsRan
    testsRan += 1
    if test:
        passed(msg)
    else:
        fail(msg)


# # if test is true call passed
# # if test is false call warn
def warnTrue(msg, test):
    global testsRan
    testsRan += 1
    if test:
        passed(msg)
    else:
        warn(msg)


# # send a command to DeepStack
def doPost(testType, data=None, **kwargs):
    """Sends a POST request, gets clean response and checks it for success

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    response = requests.post(dsUrl + "v1/vision/" + testType, data=data, **kwargs)
    assertTrue(dsUrl + "v1/vision/" + testType + " returned " + str(response.status_code),
               response.status_code == 200)
    if response.status_code == 200:
        jres = response.json()
    # deserializes into dict and returns dict.
    # note needs this to clean up or will fail when reading some responses.
        jres = json.loads(json.dumps(jres))
        dprint("jres string = " + str(jres))
        assertTrue(jres, jres["success"])    
        return jres
    else:  # Since we have not json to return fake some up in case we are not failing on errors.
        return json.loads('{ "duration": 0, "predictions": [], "success": true }')


# read in binary file and return
def readImageFile(fileName):
    return readBinaryFile(os.path.join(imgPath , fileName))


# read in binary file and return
def readBinaryFile(filePath):
    return readFile(filePath, "rb")


# read in binary file and return
def readTextFile(filePath):
    return readFile(filePath, "r")


# read in binary file and return
def readFile(filePath, readType):
    global testsRan
    
    testsRan += 1
    # with closes on section exit
    if os.path.exists(filePath):
        with open(filePath, readType) as f:
            if f.mode == readType:
                data = f.read()
                passed(str(testsRan) + ":Reading " + filePath)
                return data
            else:
                skipped(str(testsRan) + ":Could not read " + filePath, 1)
    else:
        skipped(str(testsRan) + ":Could not find " + filePath, 1)
        
    return ""


# # write list like classes.txt out
def writeList(path, filename, lines):
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(os.path.join(path, filename), "w") as fout:
        if fout.mode == "w":
            for line in lines:
                fout.write(line + "\n")
        else:
            raise ValueError("FAILED to write to " + os.path.join(path , filename))


# # add an image filename and object's confidence to to a list file named objName+".lst.txt" in the debug files folder 
# #so we can easily find files with objects of a type or no objects in them
def appendDebugList(objName, filename, confidence):
    with open(os.path.join(debugPath, objName + ".lst.txt"), "a") as fout:
        if fout.mode == "a":
                fout.write(filename + " " + str(confidence) + "\n")
        else:
            raise ValueError("FAILED to write to " + os.path.join(debugPath , objName + ".lst.txt"))


# # remove all the old debug files in config.debugPath
def clearDebugPics():
    try:
        shutil.rmtree(debugPath)
        os.mkdir(debugPath)
    except OSError as e:
        warn("Error: %s : %s" % (debugPath, e.strerror))


# # Quick test that the server is up.
def serverUpTest():
    logStart()
    # # quick test the see server is up
    response = requests.get(dsUrl)
    assertTrue("DeepStack responding", response.status_code == 200)
    logEnd("server up")


def getImgNames(folder):
        imgNames = [fn for fn in os.listdir(folder)
        if any(fn.endswith(ext) for ext in includedExts)]
        return imgNames


# # If savePath != None Save the cropped image that was found by object detection.
# # if mergePath != None the marks up image with rectangle around and label on found object
# # Mainly for checking extra objects found in tests. 
def saveFound(item, imgPath, savePath=None, mergePath=None):
    image = Image.open(imgPath).convert("RGB")
    y_max = int(item["y_max"])
    y_min = int(item["y_min"])
    x_max = int(item["x_max"])
    x_min = int(item["x_min"])
    # Save the cropped image that was found by object detection.
    if not savePath == None:
        cropped = image.crop((x_min, y_min, x_max, y_max))
        cropped.save(savePath)
        
    # highlight found object on debug image
    if not mergePath == None:
        if os.path.exists(mergePath):
            image = Image.open(mergePath).convert("RGB")
            labelImg(mergePath, image, item["label"], x_min, y_min, "green", x_max, y_max)
            
    return image.size


def labelImg(mergePath, image, text, x_min, y_min, color="black", x_max=-1, y_max=-1):

        draw = ImageDraw.Draw(image)
        if x_max > -1 and y_max > -1:
            # xy – Two points to define the bounding box. Sequence of either [(x0, y0), (x1, y1)] or [x0, y0, x1, y1]. The second point is just outside the drawn
            draw.rectangle((x_min, y_min, x_max, y_max), fill=None, outline=color)

        font = ImageFont.truetype("arial", size=20)
        # get text size
        draw.text((x_min, y_min), text, font=font, fill=color)
        image.save(mergePath)
        
        return image


# # If savePath != None Save the cropped image that was mapped in training file.
# # Mainly for checking missed objects found in tests. 
def saveExpected(data, imgPath, savePath=None, mergePath=None, text=""):
    image = Image.open(imgPath).convert("RGB")
    w, h = image.size

    # Object ID    x_center    y_center    x_width    y_height
    xy = data.split()
    x_center = float(xy[0]) * w
    y_center = float(xy[1]) * h
    x_width = float(xy[2]) * w
    y_height = float(xy[3]) * h
    y_max = int(y_center + y_height / 2)
    y_min = int(y_center - y_height / 2)
    x_max = int(x_center + x_width / 2)
    x_min = int(x_center - x_width / 2)
    # Save the cropped image that was found by object detection.
    if not savePath == None:
        cropped = image.crop((x_min, y_min, x_max, y_max))
        cropped.save(savePath)
        
    # highlight found object on debug image
    if not mergePath == None:
        if os.path.exists(mergePath):
            image = Image.open(mergePath).convert("RGB")

        labelImg(mergePath, image, text, x_min, y_min, "red", x_max, y_max)
        
    return image.size


# # to help with debug and tweaking of maps update the class lists for debugPath and lableImg
def saveLabels2labelImgData(classList):
    writeList(debugPath , "classes.txt", classList)

    if os.path.exists(labelImgData):
        writeList(labelImgData , "predefined_classes.txt", classList)


def mkdirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)

