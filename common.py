from datetime import datetime
import json
import os
import shutil
import sys

from PIL import Image, ImageFont, ImageDraw
import requests

import config

testsRan = 0
testsSkipped = 0
testsFailed = 0
testsPassed = 0
testsWarned = 0
progressCnt = 0
startCnt = 0
startTime = datetime.now()

"""if config.debugPrintOn == "N" prints a '.' wrapped at maxProgressCnt columns"""


def progressPrint():
    global progressCnt
    
    progressCnt += 1
    if progressCnt >= config.maxProgressCnt:
        sys.stdout.write('\r')
        progressCnt = 0
    sys.stdout.write('.')


"""log tests as skipped"""        


def skipped(msg, skipped):
    global testsSkipped
    
    testsSkipped += skipped
    dprint("Skipped " + str(skipped) + " " + msg)


"""if config.debugPrintOn == "Y" adds new line to log so progress dots do not make messages appear off screen""" 


def addNL():
    global progressCnt

    if progressCnt > 0:
        print("")
        progressCnt = 0


"""single point to turn off all the debug messages or preappend a newline and reset progressCnt"""


def dprint(msg):
    global progressCnt

    if config.debugPrintOn == "Y":
        if progressCnt > 0:
            print("")
            progressCnt = 0

        print(msg)

"""if failOnError == "Y" ends testing with message
if failOnError == "N" calls warn with msg"""


def fail(msg):
    global testsFailed
    
    addNL()
    testsFailed += 1
    if config.failOnError == "Y":
        raise ValueError("FAILED:" + msg)
    else:
        addNL()    
        sys.stderr.write("\nFAILED:" + msg + "\n")


"""write msg to stderr"""


def warn(msg):
    global testsWarned
    
    addNL()    
    testsWarned += 1
#    sys.stderr.write("WARN:" + msg + "\n")
    sys.stderr.write("\n" + msg + "\n")


"""if config.debugPrintOn == "Y" prints PASSED: msg otherwise a '.'"""


def passed(msg):
    global testsPassed
    
    testsPassed += 1
    if config.debugPrintOn == "Y":
        addNL()
        print("PASSED:" )
        print(str(msg))
    else:
        progressPrint()

    dprint("testsPassed:" + str(testsPassed))


""" Increment testsRan """


def incTestRan():
    global testsRan
    testsRan += 1
    dprint("testsRan:" + str(testsRan))


""" Get testsRan """


def getTestRan():
    global testsRan
    return testsRan


""" Get testsPassed """


def getTestsPassed():
    global testsPassed
    return testsPassed


""" Get testsSkipped """


def getTestsSkipped():
    global testsSkipped
    return testsSkipped


""" Get testsFailed """


def getTestsFailed():
    global testsFailed
    return testsFailed


""" Get testsSkipped """


def getTestsWarned():
    global testsWarned
    return testsWarned


""" Reset test counters """


def resetTestCnts(text=None):
    global testsRan
    global testsSkipped
    global testsFailed
    global testsPassed
    global testsWarned
    global startCnt

    startCnt = 0
    testsRan = 0
    testsSkipped = 0
    testsFailed = 0
    testsPassed = 0
    testsWarned = 0
    logStart(text)


def chkTestCnts(ran, passed, skipped, failed, warned):
    global testsRan
    global testsSkipped
    global testsFailed
    global testsPassed
    global testsWarned
    
    assertEqual("TestRan", ran, testsRan)
    assertEqual("TestsPassed", passed + 1, testsPassed)
    assertEqual("TestsSkipped", skipped, testsSkipped)
    assertEqual("TestsFailed", failed, testsFailed)
    assertEqual("TestsWarned", warned, testsWarned)
    if skipped > 0:
        print("\n" + str(skipped) + " skipped tests expected")
    if failed > 0:
        print("\n" + str(failed) + " failed tests expected")
    if warned > 0:
        print("\n" + str(warned) + " warned tests expected")


"""initialize vars for test counting and timing"""


def logStart(text=None):
    global startCnt
    global startTime
    global testsRan

    startCnt = testsRan
    dprint("startCnt:" + str(startCnt))
    startTime = datetime.now()
    if not text == None:
        print(text)


"""output info about the test set just run"""


def logEnd(text):
    global startCnt
    global startTime
    global testsRan
    global testsSkipped

    dprint("startCnt:" + str(startCnt))
    idx = text.rfind(' ')
    if idx == -1:
        print("\nRan " + str(testsRan - startCnt) + " " + text + " tests in " + str(datetime.now() - startTime))
        showTestReport()
    else:
        print("\n" + text + " in " + str(datetime.now() - startTime))
    # print("\nProcessed " + str(testsRan) + " mapping files, " + str(testsSkipped) + " could not be processed in " + str(datetime.now() - startTime))

"""if test is true run method
if test is false add tests to skip count."""


def logit(test, method, msg, skipCnt):
    if test: 
        method()
    else:
        skipped(msg, skipCnt)

"""if test is true call passed
if test is false call fail"""


def assertTrue(msg, test):
    incTestRan()
    if test:
        passed(msg)
    else:
        fail(msg)

"""if expected == found is true call passed
if expected == found is false call fail
"""


def assertEqual(msg, expected, found):
    incTestRan()
    if expected == found:
        passed(msg)
    else:
        fail(msg + ": expected:" + str(expected) + " but got:" + str(found))

"""if test is true call passed
if test is false call warn"""


def warnTrue(msg, test):
    incTestRan()
    if test:
        passed(msg)
    else:
        warn(msg)

"""send a command to DeepStack
:param testType: API part of URL that goes after v1/vision/ :class:`String` object.
:param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
:param \*\*kwargs: Optional arguments that ``request`` takes.
returns JSON object of response
"""


def doPost(testType, data=None, **kwargs):
    """Sends a POST request, gets clean response and checks it for success

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    response = requests.post(config.dsUrl + "v1/vision/" + testType, data=data, **kwargs)
    assertTrue(config.dsUrl + "v1/vision/" + testType + " returned " + str(response.status_code),
               response.status_code == 200)
    if response.status_code == 200:
        jres = response.json()
    # deserializes into dict and returns dict.
    # note needs this to clean up or will fail when reading some responses.
        jres = json.loads(json.dumps(jres))
        dprint("jres string = " + str(jres))
        assertTrue(jres, jres["success"])    
        return jres
    else:  # Since we have no json to return fake some up in case we are not failing on errors.
        return json.loads('{ "duration": 0, "predictions": [], "success": true }')


"""read in binary file and return"""


def readImageFile(fileName):
    return readBinaryFile(os.path.join(config.imgPath , fileName))


"""read in binary file and return"""


def readBinaryFile(filePath):
    return readFile(filePath, "rb")


"""read in binary file and return"""


def readTextFile(filePath):
    return readFile(filePath, "r")


"""read in binary file and return"""


def readFile(filePath, readType):
    incTestRan()
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


"""write list like classes.txt out"""


def writeList(path, filename, lines, mode="w"):
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(os.path.join(path, filename), mode) as fout:
        if fout.mode == mode:
            for line in lines:
                fout.write(line + "\n")
        else:
            raise ValueError("FAILED to write to " + os.path.join(path , filename))

""" read the classes.txt file in folder and return lines as a list.
If classes.txt does not exist, returns empty list
"""


def readClassList(folder):
    rtn = readTextFile(os.path.join(folder , "classes.txt"))
    if rtn == "":
        return []
    else:
        return rtn.splitlines()

"""add an image filename and object's confidence to to a list file named objName+".lst.txt" in the debug files folder 
so we can easily find files with objects of a type or no objects in them"""


def appendDebugList(objName, filename, confidence):
    with open(os.path.join(config.debugPath, objName + ".lst.txt"), "a") as fout:
        if fout.mode == "a":
                fout.write(filename + " " + str(confidence) + "\n")
        else:
            raise ValueError("FAILED to write to " + os.path.join(config.debugPath , objName + ".lst.txt"))


"""remove all the old debug files in config.debugPath"""


def clearDebugPics():
    clearFolder(config.debugPath)

    
"""remove all the files in folder"""


def clearFolder(folder):
    try:
        shutil.rmtree(folder)
        os.mkdir(folder)
    except OSError as e:
        warn("Error: %s : %s" % (folder, e.strerror))


def clearDebugLists():
    try:
        for fn in os.listdir(config.debugPath):
            if fn.endswith(".lst.txt"):
                os.remove(os.path.join(config.debugPath, fn)) 
    except OSError as e:
        warn("Error: %s : %s" % (config.debugPath, e.strerror))


"""Quick test that the server is up."""


def serverUpTest():
    logStart()
    response = requests.get(config.dsUrl)
    if not response.status_code == 200:
        raise ValueError("FAILED:DeepStack respond with:" + str(response.status_code))

    logEnd("server up")


""" generate a map file path from the folder and imgName by swapping the extension with '.txt' """


def getMapFileName(folder, imgName):
    idx = imgName.rfind('.')
    return os.path.join(folder, imgName[0:idx] + ".txt")


""" Get the names of all the image files in folder """


def getImgNames(folder):
        return getfileNames(folder, config.includedExts)


""" Get the names of all the files in folder with an extension in includedExts """


def getfileNames(folder, includedExts=config.includedExts):
        imgNames = [fn for fn in os.listdir(folder)
        if any(fn.endswith(ext) for ext in includedExts)]
        return imgNames


def genMap(fromFolder, toFolder):
    with open(os.path.join(toFolder, "classes.map.txt"), "w") as fout:
        if fout.mode == "w":
            fromClasses = readClassList(os.path.join(fromFolder, "classes.txt"))  
            toClasses = readClassList(os.path.join(toFolder, "classes.txt"))  
            clsOut = []
            for index in range(len(fromClasses)):
                name = fromClasses[index]
                if not name in toClasses:
                    toClasses.append(name)
                
                clsOut.append(toClasses.index(name))    
                srcdId = newClasses.index(name)
                self.idxMap[srcdId] = clsOut.index(name)
                line = "Mapping:" + str(srcdId) + ":" + name + " used " + str(self.clsCnt[index]) + " times to " + str(self.idxMap[srcdId]) + ":" + clsOut[self.idxMap[srcdId]]
                passed(line)
                fout.write(line + "\n")
    return clsOut

""" Check the number of files of a type are in folder
Pass [] as includedExts to look at all files.
"""


def chkFileCnt(folder, includedExts, expectedCnt):
    if len(includedExts) > 0: 
        imgNames = [fn for fn in os.listdir(folder)
        if any(fn.endswith(ext) for ext in config.includedExts)]
        return imgNames
    else:
        imgNames = os.listdir(folder)
       
    assertEqual("Files in " + folder + ":\n" + str(imgNames) + "\n", expectedCnt, len(imgNames)) 


""" Compare generated map file for imgFilename in srcFolder with saved expected file in expectedFolder """


def compareMapFiles(srcFolder, expectedFolder, imgFilename):
    gennedMap = getMapFileName(srcFolder, imgFilename)
    assertTrue("No generated map found for " + imgFilename, os.path.exists(gennedMap))
    createdData = readTextFile(gennedMap).splitlines()
    expectedMap = getMapFileName(expectedFolder, imgFilename)
    assertTrue("No expected map found for " + imgFilename, os.path.exists(gennedMap))
    expectedData = readTextFile(expectedMap).splitlines()
    for index in range(len(expectedData)):
        assertEqual("Map data mismatch", expectedData[index], createdData[index])


""" Compare generated file with saved expected file """


def compareTextFiles(createdFilePath, expectedFilePath):
    assertTrue("No generated file found " + createdFilePath, os.path.exists(createdFilePath))
    createdData = readTextFile(createdFilePath)
    assertTrue("No expected file found " + expectedFilePath, os.path.exists(expectedFilePath))
    expectedData = readTextFile(expectedFilePath)
    assertEqual("Map data", expectedData, createdData)

"""If savePath != None Save the cropped image that was found by object detection.
if mergePath != None the marks up image with rectangle around and label on found object
Mainly for checking extra objects found in tests. """


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

"""If savePath != None Save the cropped image that was mapped in training file.
Mainly for checking missed objects found in tests. """


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


"""to help with debug and tweaking of maps update the class lists for debugPath and lableImg"""


def saveLabels2labelImgData(classList):
    writeList(config.debugPath , "classes.txt", classList)

    if os.path.exists(config.labelImgData):
        writeList(config.labelImgData , "predefined_classes.txt", classList)
        writeList(config.labelImgData , "predefined_classes." + config.trainedName + ".txt", classList)

"""
Creates path if needed
Throws ValueError if path already exists and is not a folder
"""        


def mkdirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.isdir(path):
        raise ValueError(path + " exists and is not a folder!")

"""
Moves or copies as allowed srcFile to dstFolder
Creates dstFolder if needed
Note throws Error if file already exists and overwrite is not True
"""        


def mv(srcFile, dstFolder, overwrite=None):
    mkdirs(dstFolder)
    if (overwrite):
        dstFolder = os.path.join(dstFolder, shutil._basename(srcFile))
    shutil.move(srcFile, dstFolder)

"""
Show config options being used
"""        


def showConfig():
    print("Using folders:")
    print("trainPath:" + config.trainPath)
    print("testPath:" + config.testPath)
    print("validPath:" + config.validPath)
    print("labeled:" + config.labeled)
    print("unlabeled:" + config.unlabeled)
    print("newPicPath:" + config.newPicPath)
    print("debugPath:" + config.debugPath)
    print("\nimgPath:" + config.imgPath)
    print("labelImgData:" + config.labelImgData)
    
    print("\nUsing options:")
    print("dsUrl:" + config.dsUrl)
    print("mode:" + config.mode) 
    print("trainedName:" + config.trainedName) 
    print("maxProgressCnt:" + str(config.maxProgressCnt))
    print("debugPrintOn:" + config.debugPrintOn)
    print("saveDebugPics:" + config.saveDebugPics)
    print("failOnError:" + config.failOnError)
    print("min_confidence:" + str(config.min_confidence))
    print("includedExts:" + str(config.includedExts))
    print("tests2Run:" + str(config.tests2Run)) 

"""
Sets trainPath to path and sets testPath, vaildPath, labeled, unlabeled and debugPath relative to it.
Effectively changes from using the deepstack folder to a models folder.
if newPath is not empty then sets paths relative to it instead.
"""        


def setPaths(path="", newPath=""): 
    if len(path) > 0:
        config.trainPath = path.replace("\\", "/")
    
    if len(newPath) > 0:
        newPath = newPath.replace("\\", "/")
        if not newPath.endswith("/"):
            newPath = newPath + "/"
        config.newPicPath = newPath
        config.trainPath = os.path.join(newPath, "../train")
        mkdirs(config.trainPath)
    
    if not config.trainPath.endswith("/"):
        config.trainPath = config.trainPath + "/"
        
    if not config.trainPath.endswith("train/"):
        config.trainPath = os.path.join(config.trainPath, "train/")
    
    if not os.path.exists(config.trainPath):
        raise ValueError(config.trainPath + " does not exist")
    
    config.testPath = config.trainPath.replace("train/", "test/")
    mkdirs(config.testPath)
    config.validPath = config.trainPath.replace("train/", "valid/")
    mkdirs(config.validPath)
    config.labeled = config.trainPath.replace("train/", "labeled/")
    mkdirs(config.labeled)
    config.unlabeled = config.trainPath.replace("train/", "unlabeled/")
    mkdirs(config.unlabeled)
    config.debugPath = config.trainPath.replace("train/", "debug.pics/")  
    mkdirs(config.debugPath)
    
    if config.debugPrintOn == "Y":
        showConfig()
    
"""
Check toPath ends with subFolder
if not adds subFolder to toPath
Then creates toPath if needed.
"""


def genFolder(toPath, subFolder):
    if not toPath.endswith("/"):
        toPath = toPath + "/"
        
    if not subFolder.endswith("/"):
        subFolder = subFolder + "/"
        
    if not toPath.endswith(subFolder):
        toPath = os.path.join(toPath, subFolder)
    
    if not os.path.exists(toPath):
        os.mkdir(toPath)
        
    return toPath

""" If fout is not None write test report summary to a file
Otherwise to the screen
"""


def showTestReport(fout=None):
    if fout == None:
        print("")
        otherPassed = testsRan - testsPassed - testsWarned - testsFailed
        print("Of " + str(testsRan + testsSkipped) + " tests")
        print(" Ran:" + str(testsRan))
        print(" Skipped:" + str(testsSkipped))
        print(" Passed:" + str(testsPassed + otherPassed))
        print(" Warnings:" + str(testsWarned))
        print(" Failed:" + str(testsFailed))
    else:
        fout.write("\n")
        fout.write("Of " + str(testsRan + testsSkipped) + " tests\n")
        fout.write(" Ran:" + str(testsRan) + "\n")
        fout.write(" Skipped:" + str(testsSkipped) + "\n")
        fout.write(" Passed:" + str(testsPassed) + "\n")
        fout.write(" Warnings:" + str(testsWarned) + "\n")
        fout.write(" Failed:" + str(testsFailed) + "\n")
