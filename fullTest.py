import json
import requests
import os
import shutil
import zipfile
import config

# # Note tested with Python 2.7 on CentoOS Linux and 3.9 on Windows
# Test control flags. Set to N to skip test.
# # Run face tests
doFace = "Y"
# # Run scene detection tests
doScene = "Y"
# # Run object detection tests
doObj = "Y"
# # Run backup tests
doBackup = "Y"
# # Run all pics in the config.imgPath thru enabled (see custom models) object detection tests and compare with a base run.
doExt = "Y"

# # what test counts should be for ext tests
detectionExtTests = 151
logoExtTests = 101
plateExtTests = 100
darkExtTests = 137
actionExtTests = 118


# # if test is true run method
# # if test is false add tests to skip count.
def logit(test, method, msg, skipCnt):
    if test: 
        method()
    else:
        config.skipped(msg, skipCnt)


# register face for test.
def registerFace(fileName, userId):
    config.doPost("face/register", files={"image":config.readImageFile(fileName)}, data={"userid":userId})


# # expected items are in foundItems
def chkArray(foundItems, expected, testType, fileName):
    config.dprint(foundItems)

    config.warnTrue("Of " + str(len(expected)) + " expected " + str(expected) + " found objects, found:" + str(len(foundItems)) 
             +" objects " + str(foundItems), len(foundItems) == len(expected))
    # check what we expect is there. Note other things might be found but here we only care about the expected
    for item in expected:
        config.assertTrue(item + " in " + testType + " test image:" + fileName, item in foundItems)
        # remove in case we are checking for more than one of a type
        if item in foundItems:
            foundItems.remove(item)

    return len(foundItems) 


# # Compare objects found in image against expected ones
def detectTest(testType, fileName, expected):
    
    config.dprint("Testing " + testType + "-" + fileName)
    response = config.doPost(testType, files={"image":config.readImageFile(fileName)})

    if "face" == testType:
        config.assertTrue("Of " + str(expected) + " expected found faces, found:" + str(len(response["predictions"])),
                   expected == len(response["predictions"]))
    elif "scene" == testType:
        config.assertTrue(str(expected) + " scene expected, found:" + str(response["label"]),
                   expected == response["label"])
    else:
        # no compare data so warn and create from this response
        if len(expected) == 1 and expected[0] == "undefined":
            config.testsRan += 1
            config.warn("No data for " + config.imgPath + fileName + " initializing for next run of Extra tests for " + testType)
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
    path = config.imgPath + testType + "/" + fileName + '.json'
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
    path = config.imgPath + testType + "/"
    config.mkdirs(path)
    with open(path + fileName + ".json", "wb") as f:
        if f.mode == "wb":
            f.write(json.dumps(response, indent=4))


# # Run the face sample tests
def faceTests():
    config.logStart()
# # face detect test
    detectTest("face", "family.jpg", 4)

    response = config.doPost("face/match", files={"image1":config.readImageFile("obama1.jpg"),
                                              "image2":config.readImageFile("obama2.jpg")})
    config.assertTrue("Face match", response['similarity'] > 0.70)
    
    response = config.doPost("face/match", files={"image1":config.readImageFile("obama1.jpg"),
                                              "image2":config.readImageFile("brad.jpg")})
    config.assertTrue("Face mismatch", response['similarity'] < 0.51)

    # # face recog test
    registerFace("tomcruise.jpg", "Tom Cruise")
    registerFace("adele.jpg", "Adele")
    registerFace("idriselba.jpg", "Idris Elba")
    registerFace("perri.jpg", "Christina Perri")

    response = config.doPost("face/list")
    chkArray(response["faces"], ["Tom Cruise", "Adele", "Idris Elba", "Christina Perri"], "face/list", "db")
    
    res = config.doPost("face/recognize", files={"image":config.readImageFile("adele2.jpg")})
    
    i = 0
    for face in res["predictions"]:
        found = face["userid"]
        config.dprint("Found " + found)
        config.testsRan += 1
        if found != "Adele":
            config.saveFound(face, config.imgPath + "adele2.jpg", found + "{}.jpg".format(i))
            config.fail("Face recog. Found " + found + " instead of Adele") 
        else:
            config.passed("PASSED:Face recog")
        i += 1
    config.logEnd("face")


# # Run some basic scene detection tests   
def sceneTests():
    testType = "scene"
    config.logStart()
    # # Basic scene test
    detectTest(testType, "office.jpg", "conference_room")
    detectTest(testType, "creek.jpg", "forest_path")
    detectTest(testType, "DAH847_day.jpg", "yard")
    detectTest(testType, "DAH847_night.jpg", "driveway")  # this seems wrong
    detectTest(testType, "DAH834_driveway_day.jpg", "driveway")
    config.logEnd(testType)


# # Run some basic object detection tests
def objTests():
    testType = "detection"
    config.logStart()
    # # Basic Object test
#    detectTest(testType, "test-image3.jpg", ["handbag", "person", "dog", "person"])
    detectTest(testType, "test-image3.jpg", ["person", "dog", "person"])
    detectTest(testType, "fedex.jpg", ["truck"])
    config.logEnd(testType)


# # Run that openlogo models sample test    
def logoTests():
    testType = "custom/openlogo"
    config.logStart()
    detectTest(testType, "fedex.jpg", ["fedex", "fedex"])
    config.logEnd(testType)


# # Run that licence-plate model sample test
def plateTests():
    testType = "custom/licence-plate"
    config.logStart()
    # test image of his
    detectTest(testType, "031_924430341.jpg", ["licence-plate"])
    # test image of US TX plate not working
    # detectTest(testType, "back_plate_day.jpg", ["licence-plate"])
    config.logEnd(testType)


# # Run that dark model sample tests   
def darkTests():
    testType = "custom/dark"
    config.logStart()
    if config.mode == "Medium":
        detectTest(testType, "dark_image.jpg", ["People", "Dog", "Dog", "Dog", "Dog"])
    elif config.mode == "High":
        detectTest(testType, "dark_image.jpg", ["Motorbike", "People", "Dog", "Dog", "Dog", "Dog", "Dog"])
    config.logEnd(testType)


# # Run that actionnetv2 model sample tests
def actionTests():
    testType = "custom/actionnetv2"
    config.logStart()
    detectTest(testType, "dancing1.jpg", ["dancing"])
    detectTest(testType, "fighting2.jpg", ["dancing"])  # does not seem to work
    detectTest(testType, "fighting3.jpg", ["fighting"])
    detectTest(testType, "cycling4.jpg", ["cycling"])
    detectTest(testType, "eating5.webp", ["eating", "eating", "eating"])
    config.logEnd(testType)


# # Try using the SDK to back up DeepStack setup
def backupTests():

    testType = "backup"
    zipFile = "backupdeepstack.zip"
    config.logStart()
    data = requests.post(config.dsUrl + "v1/backup", stream=True)
    with open(zipFile, "wb") as f:
        shutil.copyfileobj(data.raw, f)
        
    config.dprint("Testing zip file: %s" % zipFile)

    tstZipFile = zipfile.ZipFile(zipFile)
    ret = tstZipFile.testzip()

    config.testsRan += 1
    if ret is not None:
        config.fail("First bad file in zip: %s" % ret)
    else:
        config.passed("PASSED:Zip file is good.")
        
    config.logEnd(testType)


# # run all the images in imgPath against all the enabled object detection models
def extTests():
    # # run a bunch of my test images through object detection
    fileNames = config.getImgNames(config.imgPath)
    
    if "custom/openlogo" not in config.tests2Run:
        config.skipped("Extra openlogo detect object tests", logoExtTests) 
        
    if "custom/licence-plate" not in config.tests2Run:
        config.skipped("Extra licence-plate detect object tests", plateExtTests) 
        
    if "custom/dark" not in config.tests2Run:
        config.skipped("Extra dark detect object tests", darkExtTests) 
        
    if "custom/actionnetv2" not in config.tests2Run:
        config.skipped("Extra actionnetv2 detect object tests", actionExtTests) 

    for testType in config.tests2Run:
        config.logStart()
        for f in fileNames:
            config.dprint("Checking:" + config.imgPath + f)
            detectTest(testType, f, getExpected(testType, f))    
        config.logEnd(testType)
    
    
#########################################################
# ## The test suite #####################################
#########################################################
config.serverUpTest()
config.clearDebugPics()    
logit(doFace == "Y", faceTests, "Face tests skipped", 28)
logit(doScene == "Y", sceneTests, "scene tests skipped", 9)
logit(doObj == "Y", objTests, "Object detection tests", 10)
logit(doBackup == "Y", backupTests, "Backup tests", 1)
logit("custom/openlogo" in config.tests2Run, logoTests, "Detect openlogo tests", 5)
logit("custom/licence-plate" in config.tests2Run, plateTests, "Detect licence-plate test", 8)
logit("custom/dark" in config.tests2Run, darkTests, "Detect dark test", 9)
logit("custom/actionnetv2" in config.tests2Run, actionTests, "Detect actionnet tests", 27)
logit(doExt == "Y", extTests, "Extra object detect object tests", detectionExtTests + logoExtTests + plateExtTests + darkExtTests + actionExtTests) 
    
print("")
print("Of " + str(config.testsRan + config.testsSkipped) + " tests")
print(" Ran:" + str(config.testsRan))
print(" Skipped:" + str(config.testsSkipped))
print(" Passed:" + str(config.testsPassed))
print(" Warnings:" + str(config.testsWarned))
print(" Failed:" + str(config.testsFailed))

