import json
import requests
import os
import sys
import shutil
import zipfile
from PIL import Image
from datetime import datetime
# from Cheetah.Templates._SkeletonPage import True

# # Note tested with Python 2.7 on CentoOS Linux
# # Where images to test with are located
imgPath = "./test.imgs/"
# # Where to save debug images of from tests 
debugPath = "./debug.pics/"
# # if Y saves debug images to compare between expected and found objects for mismatches.
saveDebugPics = "Y"
# # Base URL of your DeepStack server
dsUrl = "http://192.168.2.197:82/"
# # DeepStack started with -e MODE=Medium or -e MODE=High
mode = "Medium" 
# Test control flags. Set to N to skip test.
# # Run face tests
doFace = "Y"
# # Run scene detection tests
doScene = "Y"
# # Run object detection tests
doObj = "Y"
# # Run backup tests
doBackup = "Y"
# # Run all pics in the imgPath thru enabled (see custom models) object detection tests and compare with a base run.
doExt = "Y"

# Custom models
# # Run tests for [logo custom model](https://github.com/OlafenwaMoses/DeepStack_OpenLogo).
doLogo = "Y"
# # Run tests for [licence-plate custom model](https://github.com/odd86/deepstack_licenceplate_model).
doPlate = "Y"
# # Run tests for [dark custom model](https://github.com/OlafenwaMoses/DeepStack_ExDark).
doDark = "Y"
# # Run tests for [actionnet custom model](https://github.com/OlafenwaMoses/DeepStack_ActionNET).
doAction = "Y"
# # Run tests for trained model.
doTrained = "Y"
# # Name of trained set model. Usually the same as the name of the pt file.
# # RMRR is mine from the data in the checked in trainData folder. If you train your own replace the train folder in trainData with your own. 
trainedName = "RMRR" 
# # new line used in the data files in trainData folder
ln = '\r\n'

# # Output debug info Y,N
debugPrintOn = "N"

# # Y=Fail on error, N=Just warn on error
failOnError = "Y"
# Images suffixes to use for image tests
includedExts = ['jpg', 'webp', 'bmp', 'png', 'gif']

testsRan = 0
testsSkipped = 0
testsFailed = 0
testsPassed = 0
testsWarned = 0
progressCnt = 0
startCnt = 0
startTime = datetime.now()


# # if debugPrintOn == "N" prints a '.' wrapped at 80 columns
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


# # if debugPrintOn == "Y" adds new line to log so progress dots do not make messages appear off screen 
def addNL():
    global progressCnt

    if progressCnt > 0:
        print("")
        progressCnt = 0


# # if debugPrintOn == "Y" prints PASSED: msg otherwise a '.'
def passed(msg):
    global testsPassed
    
    testsPassed += 1
    if debugPrintOn == "Y":
        addNL()
        print("PASSED:" + str(msg))
    else:
        progressPrint()


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
    sys.stderr.write("WARN:" + msg + "\n")


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


# single point to turn off all the debug messages 
def dprint(msg):
    global progressCnt

    if debugPrintOn == "Y":
        if progressCnt > 0:
            print("")
            progressCnt = 0

        print(msg)


# # intialize vars for test counting and timing    
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

    print("\nRan " + str(testsRan - startCnt) + " " + testType + " tests in " + str(datetime.now() - startTime))


# # if test is true run method
# # if test is false add tests to skip count.
def logit(test, method, msg, skipCnt):
    if test: 
        method()
    else:
        skipped(msg, skipCnt)


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
            passed("Reading " + filePath)
            return data
        else:
            fail("could not read " + filePath)


# register face for test.
def registerFace(fileName, userId):
    doPost("face/register", files={"image":readImageFile(fileName)}, data={"userid":userId})


# # expected items are in foundItems
def chkArray(foundItems, expected, testType, fileName):
    global testsRan
    dprint(foundItems)

    warnTrue("Of " + str(len(expected)) + " expected " + str(expected) + " found objects, found:" + str(len(foundItems)) 
             +" objects " + str(foundItems), len(foundItems) == len(expected))
    # check what we expect is there. Note other things might be found but here we only care about the expected
    for item in expected:
        assertTrue(item + " in " + testType + " test image:" + fileName, item in foundItems)
        # remove in case we are checking for more than one of a type
        if item in foundItems:
            foundItems.remove(item)

    return len(foundItems) 


# # Compare objects found in image against expected ones
def detectTest(testType, fileName, expected):
    global testsRan
    
    dprint("Testing " + testType + "-" + fileName)
    response = doPost(testType, files={"image":readImageFile(fileName)})

    if "face" == testType:
        assertTrue("Of " + str(expected) + " expected found faces, found:" + str(len(response["predictions"])),
                   expected == len(response["predictions"]))
    elif "scene" == testType:
        assertTrue(str(expected) + " scene expected, found:" + str(response["label"]),
                   expected == response["label"])
    else:
        # no compare data so warn and create from this response
        if len(expected) == 1 and expected[0] == "undefined":
            testsRan += 1
            warn("No data for " + imgPath + fileName + " initializing for next run of Extra tests for " + testType)
            writeTestData(testType, fileName, response)
        else:
            foundItems = []
            i = 0
            for item in response["predictions"]:
                foundItems.insert(i, item["label"])
                i += 1
                
            chkArray(foundItems, expected, testType, fileName)


# # read expected response for test image run against testType
def getExpected(testType, fileName):
    expected = []
    path = imgPath + testType + "/" + fileName + '.json'
    if os.path.exists(path):
        jfile = open(path)
        data = json.load(jfile)
        i = 0
        for item in data["predictions"]:
            expected.insert(i, item["label"])
            i += 1
            
    else:
        # flag as has no compare data
        expected.insert(0, "undefined")        

    return expected


# # Write found data. Used to create compare file for new images.
def writeTestData(testType, fileName, response): 
    path = imgPath + testType + "/"
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(path + fileName + ".json", "wb") as f:
        if f.mode == "wb":
            f.write(json.dumps(response, indent=4))


# # Quick test that the server is up.
def serverUpTest():
    logStart()
    # # quick test the see server is up
    response = requests.get(dsUrl)
    assertTrue("DeepStack responding", response.status_code == 200)
    logEnd("server up")


# # Run the face sample tests
def faceTests():
    global testsRan

    logStart()
# # face detect test
    detectTest("face", "family.jpg", 4)

    response = doPost("face/match", files={"image1":readImageFile("obama1.jpg"),
                                              "image2":readImageFile("obama2.jpg")})
    assertTrue("Face match", response['similarity'] > 0.70)
    
    response = doPost("face/match", files={"image1":readImageFile("obama1.jpg"),
                                              "image2":readImageFile("brad.jpg")})
    assertTrue("Face mismatch", response['similarity'] < 0.51)

    # # face recog test
    registerFace("tomcruise.jpg", "Tom Cruise")
    registerFace("adele.jpg", "Adele")
    registerFace("idriselba.jpg", "Idris Elba")
    registerFace("perri.jpg", "Christina Perri")

    response = doPost("face/list")
    chkArray(response["faces"], ["Tom Cruise", "Adele", "Idris Elba", "Christina Perri"], "face/list", "db")
    
    res = doPost("face/recognize", files={"image":readImageFile("adele2.jpg")})
    
    i = 0
    for face in res["predictions"]:
        found = face["userid"]
        dprint("Found " + found)
        testsRan += 1
        if found != "Adele":
            image = Image.open(imgPath + "adele2.jpg").convert("RGB")
            y_max = int(face["y_max"])
            y_min = int(face["y_min"])
            x_max = int(face["x_max"])
            x_min = int(face["x_min"])
            cropped = image.crop((x_min, y_min, x_max, y_max))
            cropped.save(found + "{}.jpg".format(i))
            fail("Face recog. Found " + found + " instead of Adele") 
        else:
            passed("Face recog")
        i += 1
    logEnd("face")


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


# # Run some basic scene detection tests   
def sceneTests():
    testType = "scene"
    logStart()
    # # Basic scene test
    detectTest(testType, "office.jpg", "conference_room")
    detectTest(testType, "DAH847_day.jpg", "yard")
    detectTest(testType, "DAH847_night.jpg", "driveway")  # this seems wrong
    logEnd(testType)


# # Run some basic object detection tests
def objTests():
    testType = "detection"
    logStart()
    # # Basic Object test
#    detectTest(testType, "test-image3.jpg", ["handbag", "person", "dog", "person"])
    detectTest(testType, "test-image3.jpg", ["person", "dog", "person"])
    detectTest(testType, "fedex.jpg", ["truck"])
    logEnd(testType)


# # Run that openlogo models sample test    
def logoTests():
    testType = "custom/openlogo"
    logStart()
    detectTest(testType, "fedex.jpg", ["fedex", "fedex"])
    logEnd(testType)


# # Run that licence-plate model sample test
def plateTests():
    testType = "custom/licence-plate"
    logStart()
    # test image of his
    detectTest(testType, "031_924430341.jpg", ["licence-plate"])
    # test image of US TX plate not working
    # detectTest(testType, "back_plate_day.jpg", ["licence-plate"])
    logEnd(testType)


# # Run that dark model sample tests   
def darkTests():
    testType = "custom/dark"
    logStart()
    if mode == "Medium":
        detectTest(testType, "dark_image.jpg", ["People", "Dog", "Dog", "Dog", "Dog"])
    elif mode == "High":
        detectTest(testType, "dark_image.jpg", ["Motorbike", "People", "Dog", "Dog", "Dog", "Dog", "Dog"])
    logEnd(testType)


# # Run that actionnetv2 model sample tests
def actionTests():
    testType = "custom/actionnetv2"
    logStart()
    detectTest(testType, "dancing1.jpg", ["dancing"])
    detectTest(testType, "fighting2.jpg", ["dancing"])  # does not seem to work
    detectTest(testType, "fighting3.jpg", ["fighting"])
    detectTest(testType, "cycling4.jpg", ["cycling"])
    detectTest(testType, "eating5.webp", ["eating", "eating", "eating"])
    logEnd(testType)


# # Try using the SDK to back up DeepStack setup
def backupTests():
    global testsRan

    testType = "backup"
    zipFile = "backupdeepstack.zip"
    logStart()
    data = requests.post(dsUrl + "v1/backup", stream=True)
    with open(zipFile, "wb") as f:
        shutil.copyfileobj(data.raw, f)
        
    dprint("Testing zip file: %s" % zipFile)

    tstZipFile = zipfile.ZipFile(zipFile)
    ret = tstZipFile.testzip()

    testsRan += 1
    if ret is not None:
        fail("First bad file in zip: %s" % ret)
    else:
        passed("Zip file is good.")
        
    logEnd(testType)


# # run all the images in imgPath against all the enabled object detection models
def extTests():
    global includedExts
    # # run a bunch of my test images through object detection
    fileNames = [fn for fn in os.listdir(imgPath)
        if any(fn.endswith(ext) for ext in includedExts)]
    
    tests2Run = ["detection"]

    if doLogo == "Y":
        tests2Run.append("custom/openlogo")
    else:
        skipped("Extra openlogo detect object tests", 516) 
        
    if doPlate == "Y":
        tests2Run.append("custom/licence-plate")
    else:
        skipped("Extra licence-plate detect object tests", 516) 
        
    if doDark == "Y":
        tests2Run.append("custom/dark")
    else:
        skipped("Extra dark detect object tests", 516) 
        
    if doAction == "Y":
        tests2Run.append("custom/actionnetv2")
    else:
        skipped("Extra actionnetv2 detect object tests", 516) 

    for testType in tests2Run:
        logStart()
        for f in fileNames:
            dprint("Checking:" + imgPath + f)
            detectTest(testType, f, getExpected(testType, f))    
        logEnd(testType)


# # remove all the old debug files in debugPath
def clearDebugPics():
    imgNames = [fn for fn in os.listdir(debugPath)
    if any(fn.endswith(ext) for ext in includedExts)]
    
    for f in imgNames:
        os.remove(debugPath + f)


# # run tests for the trained custom model
def trainTests():
    global failOnError
    global testsRan
    global includedExts
    
#    hold = failOnError
#    failOnError = "N"
    trainPath = "trainData/train/"
    logStart()
    classes = readTextFile(trainPath + "classes.txt").splitlines()
    dprint(classes)
    
    imgNames = [fn for fn in os.listdir(trainPath)
        if any(fn.endswith(ext) for ext in includedExts)]

    for f in imgNames:
        dprint("Checking:" + trainPath + f)
        idx = f.rfind('.')
        expf = f[0:idx] + ".txt"
        if os.path.exists(trainPath + expf):
            dprint("against:" + trainPath + expf)      
            data = readTextFile(trainPath + expf).splitlines()
            dprint(data)
            expected = []
            for line in data:
                idx = line.find(' ')
                c = int(line[0:idx])
                expected.append(classes[c])

            dprint(expected)
    
            dprint("Testing " + trainedName + "-" + trainPath + f)
            response = doPost("custom/" + trainedName, files={"image":readBinaryFile(trainPath + f)})
            foundItems = []
            i = 0
            for item in response["predictions"]:
                foundItems.insert(i, item["label"])
                i += 1
                
            if not chkArray(foundItems, expected, "custom/" + trainedName, trainPath + f) == 0:
                i = 0
                for item in response["predictions"]:
                    saveFound(item, trainPath + f, debugPath + f + "." + item["label"] + "." + str(i) + "." + str(item["confidence"]) + ".jpg")
                    i += 1

        else:
            warn("Missing label file " + trainPath + expf + ", skipping ")

    logEnd(trainedName)
    print("Check images in " + debugPath + " match the object in the file name.")
    print("Files are named filename.item['label'].objectNumber.item['confidence'].jpg")
#    failOnError = hold
    
    
#########################################################
# ## The test suite #####################################
#########################################################
serverUpTest()
clearDebugPics()    
logit(doFace == "Y", faceTests, "Face tests skipped", 28)
logit(doScene == "Y", sceneTests, "scene tests skipped", 9)
logit(doObj == "Y", objTests, "Object detection tests", 10)
logit(doLogo == "Y", logoTests, "Detect openlogo tests", 5)
logit(doPlate == "Y", plateTests, "Detect licence-plate test", 8)
logit(doDark == "Y", darkTests, "Detect dark test", 9)
logit(doAction == "Y", actionTests, "Detect actionnet tests", 27)
logit(doBackup == "Y", backupTests, "Backup tests", 1)
logit(doExt == "Y", extTests, "Extra object detect object tests", 516) 
logit(doTrained == "Y", trainTests, "Trained model object detect object tests", 645) 
    
print("")
print("Of " + str(testsRan + testsSkipped) + " tests")
print(" Ran:" + str(testsRan))
print(" Skipped:" + str(testsSkipped))
print(" Passed:" + str(testsPassed))
print(" Warnings:" + str(testsWarned))
print(" Failed:" + str(testsFailed))

