import json
import sys
from datetime import datetime
import requests
import os
from PIL import Image

# Configuration options and common methods for DeepStack utils
# # Base URL of your DeepStack server
dsUrl = "http://localhost:82/"
# # DeepStack started with -e MODE=Medium or -e MODE=High
mode = "Medium" 
# # Where images to test with are located
imgPath = "test.imgs/"
# # Where to save debug images of from tests 
debugPath = "debug.pics/"
# # path to labeled training pics.
trainPath = "../RMRR.model/train/"
# # unlabeled / new file folder
# newPicPath = "D:/odrive/GD.video/cams/DeepStackWS/data/new/"
newPicPath = "new/"
# # Name of trained set model. Usually the same as the name of the pt file.
# # RMRR is mine from the data in the checked in trainData folder. If you train your own replace the train folder in trainData with your own. 
trainedName = "RMRR" 
# # folder where images with found objects and their mapping files are put by quickLabel and read by chkClasses
labeled = "labeled/"
# # folder where images with not found objects are put by quickLabel and read by chkClasses
unlabeled = "unlabeled/"

# # Output debug info Y,N
debugPrintOn = "Y"
# # if Y saves debug images to compare between expected and found objects for mismatches.
saveDebugPics = "Y"
# # Y=Fail on error, N=Just warn on error
failOnError = "N"

# Supported images suffixes to look for in folders
includedExts = ['jpg', 'webp', 'bmp', 'png', 'gif']

# # installed models to use to find objects
# # detection the built in model
# # [openlogo custom model](https://github.com/OlafenwaMoses/DeepStack_OpenLogo).
# # [licence-plate custom model](https://github.com/odd86/deepstack_licenceplate_model).
# # [dark custom model](https://github.com/OlafenwaMoses/DeepStack_ExDark).
# # [actionnetv2 custom model](https://github.com/OlafenwaMoses/DeepStack_ActionNET).
# tests2Run = ["custom/"+trainedName] 
tests2Run = ["detection", "custom/openlogo", "custom/licence-plate", "custom/dark", "custom/actionnetv2"] 

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
    if progressCnt >= 80:
        print(".")
        progressCnt = 0
    else:
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
        warn("FAILED:" + msg)


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
    return readBinaryFile(imgPath + fileName)


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
    with open(filePath, readType) as f:
        if f.mode == readType:
            data = f.read()
            passed(str(testsRan) + ":Reading " + filePath)
            return data
        else:
            fail(str(testsRan) + ":Ccould not read " + filePath)
#            skipped("could not read " + filePath, 1)


# # write list like classes.txt out
def writeList(path, filename, lines):
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(path + filename, "w") as fout:
        if fout.mode == "w":
            for line in lines:
                fout.write(line + "\n")


# # remove all the old debug files in config.debugPath
def clearDebugPics():
    for f in getImgNames(debugPath):
        os.remove(debugPath + f)

    txtNames = [fn for fn in os.listdir(debugPath)
                if fn.endswith(".txt")]
    
    for f in txtNames:
        os.remove(debugPath + f)


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


# # Save the cropped image that was found by object detection.
# # Mainly for checking extra objects found in tests. 
def saveFound(item, imgPath, savePath):
    image = Image.open(imgPath).convert("RGB")
    y_max = int(item["y_max"])
    y_min = int(item["y_min"])
    x_max = int(item["x_max"])
    x_min = int(item["x_min"])
    cropped = image.crop((x_min, y_min, x_max, y_max))
    cropped.save(savePath)
    return image.size


# # Save the cropped image that was mapped in training file.
# # Mainly for checking missed objects found in tests. 
def saveExpected(data, imgPath, savePath):
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
    cropped = image.crop((x_min, y_min, x_max, y_max))
    cropped.save(savePath)
    return image.size


def mkdirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)

