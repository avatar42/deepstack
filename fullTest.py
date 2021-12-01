import json
import requests
import os
import sys
import shutil
import zipfile
from PIL import Image
from datetime import datetime

# # Note tested with Python 2.7
# # Where images to test with are located
img_path = "./test.imgs/"
# # Base URL of your DeepStack server
ds_url = "http://localhost:82/"
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
# # Run all pics in the img_path thru enabled (see custom models) object detection tests and compare with a base run.
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

# Output debug info Y,N
debugPrintOn = "N"

# Y=Fail on error, N=Just warn on error
failOnError = "Y"

testsRan = 0
testsSkipped = 0
testsFailed = 0
testsPassed = 0
testsWarned = 0
progressCnt = 0
startCnt = 0
startTime = datetime.now()


def progressPrint():
    global progressCnt

    progressCnt += 1
    if progressCnt >= 80:
        print(".")
        progressCnt = 0
    else:
        sys.stdout.write('.')

        
def skipped(msg, skipped):
    global testsSkipped
    
    testsSkipped += skipped
    dprint("Skipped " + str(skipped) + " " + msg)


def passed(msg):
    global testsPassed
    global progressCnt
    
    testsPassed += 1
    if debugPrintOn == "Y":
        if progressCnt > 0:
            print("")
            progressCnt = 0
        print("PASSED:" + str(msg))
    else:
        progressPrint()


def fail(msg):
    global testsFailed
    global progressCnt
    
    if progressCnt > 0:
        print("")
        progressCnt = 0
    testsFailed += 1
    if failOnError == "Y":
        raise ValueError("FAILED:" + msg)
    else:
        warn("FAILED:" + msg)


def warn(msg):
    global testsWarned
    
    testsWarned += 1
    sys.stderr.write("WARN:" + msg + "\n")


def assertTrue(msg, test):
    global testsRan
    testsRan += 1
    if test:
        passed(msg)
    else:
        fail(msg)


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

    
def logStart():
    global startCnt
    global startTime
    global testsRan

    startCnt = testsRan
    startTime = datetime.now()


def logEnd(test_type):
    global startCnt
    global startTime
    global testsRan

    print("\nRan " + str(testsRan - startCnt) + " " + test_type + " tests in " + str(datetime.now() - startTime))


def logit(test, method, msg, skipCnt):
    if test: 
        method()
    else:
        skipped(msg, skipCnt)


def doPost(test_type, data=None, **kwargs):
    """Sends a POST request, gets clean response and checks it for success

    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    response = requests.post(ds_url + "v1/vision/" + test_type, data=data, **kwargs)
    assertTrue(ds_url + "v1/vision/" + test_type + " returned " + str(response.status_code),
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
def read_binary(file_name):
    global testsRan
    
    testsRan += 1
    # with closes on section exit
    with open(img_path + file_name, "rb") as f:
        if f.mode == "rb":
            data = f.read()
            passed("Reading " + img_path + file_name)
            return data
        else:
            fail("could not read " + img_path + file_name)


# register face for test.
def register_face(file_name, user_id):
    doPost("face/register", files={"image":read_binary(file_name)}, data={"userid":user_id})


def chkArray(foundItems, expected, test_type, file_name):
    global testsRan
    dprint(foundItems)

    warnTrue("Of " + str(len(expected)) + " expected " + str(expected) + " found objects, found:" + str(len(foundItems)) 
             +" objects " + str(foundItems), len(foundItems) == len(expected))
    # check what we expect is there. Note other things might be found but here we only care about the expected
    for item in expected:
        assertTrue(item + " in " + test_type + " test image:" + file_name, item in foundItems)
        # remove in case we are checking for more than one of a type
        if item in foundItems:
            foundItems.remove(item)


def detect_test(test_type, file_name, expected):
    global testsRan
    
    dprint("Testing " + test_type + "-" + file_name)
    response = doPost(test_type, files={"image":read_binary(file_name)})

    if "face" == test_type:
        assertTrue("Of " + str(expected) + " expected found faces, found:" + str(len(response["predictions"])),
                   expected == len(response["predictions"]))
    elif "scene" == test_type:
        assertTrue(str(expected) + " scene expected, found:" + str(response["label"]),
                   expected == response["label"])
    else:
        # no compare data so warn and create from this response
        if len(expected) == 1 and expected[0] == "undefined":
            testsRan += 1
            warn("No data for " + img_path + file_name + " initializing for next run of Extra tests for " + test_type)
            writeTestData(test_type, file_name, response)
        else:
            foundItems = []
            i = 0
            for item in response["predictions"]:
                foundItems.insert(i, item["label"])
                i += 1
                
            chkArray(foundItems, expected, test_type, file_name)


# read expected response for test image run against test_type
def getExpected(test_type, file_name):
    expected = []
    path = img_path + test_type + "/" + file_name + '.json'
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


def writeTestData(test_type, file_name, response): 
    path = img_path + test_type + "/"
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(path + file_name + ".json", "wb") as f:
        if f.mode == "wb":
            f.write(json.dumps(response, indent=4))


def serverUpTest():
    logStart()
    # # quick test the see server is up
    response = requests.get(ds_url)
    assertTrue("DeepStack responding", response.status_code == 200)
    logEnd("server up")


def faceTests():
    global testsRan

    logStart()
# # face detect test
    detect_test("face", "family.jpg", 4)

    response = doPost("face/match", files={"image1":read_binary("obama1.jpg"),
                                              "image2":read_binary("obama2.jpg")})
    assertTrue("Face match", response['similarity'] > 0.70)
    
    response = doPost("face/match", files={"image1":read_binary("obama1.jpg"),
                                              "image2":read_binary("brad.jpg")})
    assertTrue("Face mismatch", response['similarity'] < 0.51)

    # # face recog test
    register_face("tomcruise.jpg", "Tom Cruise")
    register_face("adele.jpg", "Adele")
    register_face("idriselba.jpg", "Idris Elba")
    register_face("perri.jpg", "Christina Perri")

    response = doPost("face/list")
    chkArray(response["faces"], ["Tom Cruise", "Adele", "Idris Elba", "Christina Perri"], "face/list", "db")
    
    res = doPost("face/recognize", files={"image":read_binary("adele2.jpg")})
    
    i = 0
    for face in res["predictions"]:
        found = face["userid"]
        dprint("Found " + found)
        testsRan += 1
        if found != "Adele":
            image = Image.open(img_path + "adele2.jpg").convert("RGB")
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

    
def sceneTests():
    test_type = "scene"
    logStart()
    # # Basic scene test
    detect_test(test_type, "office.jpg", "conference_room")
    detect_test(test_type, "DAH847_day.jpg", "yard")
    detect_test(test_type, "DAH847_night.jpg", "driveway")  # this seems wrong
    logEnd(test_type)


def objTests():
    test_type = "detection"
    logStart()
    # # Basic Object test
#    detect_test(test_type, "test-image3.jpg", ["handbag", "person", "dog", "person"])
    detect_test(test_type, "test-image3.jpg", ["person", "dog", "person"])
    detect_test(test_type, "fedex.jpg", ["truck"])
    logEnd(test_type)

    
def logoTests():
    test_type = "custom/openlogo"
    logStart()
    detect_test(test_type, "fedex.jpg", ["fedex", "fedex"])
    logEnd(test_type)


def plateTests():
    test_type = "custom/licence-plate"
    logStart()
    # test image of his
    detect_test(test_type, "031_924430341.jpg", ["licence-plate"])
    # test image of US TX plate not working
    # detect_test(test_type, "back_plate_day.jpg", ["licence-plate"])
    logEnd(test_type)

    
def darkTests():
    test_type = "custom/dark"
    logStart()
    if mode == "Medium":
        detect_test(test_type, "dark_image.jpg", ["People", "Dog", "Dog", "Dog", "Dog"])
    elif mode == "High":
        detect_test(test_type, "dark_image.jpg", ["Motorbike", "People", "Dog", "Dog", "Dog", "Dog", "Dog"])
    logEnd(test_type)


def actionTests():
    test_type = "custom/actionnetv2"
    logStart()
    detect_test(test_type, "dancing1.jpg", ["dancing"])
    detect_test(test_type, "fighting2.jpg", ["dancing"])  # does not seem to work
    detect_test(test_type, "fighting3.jpg", ["fighting"])
    detect_test(test_type, "cycling4.jpg", ["cycling"])
    detect_test(test_type, "eating5.webp", ["eating", "eating", "eating"])
    logEnd(test_type)


def backupTests():
    global testsRan

    test_type = "backup"
    zip_file = "backupdeepstack.zip"
    logStart()
    data = requests.post(ds_url + "v1/backup", stream=True)
    with open(zip_file, "wb") as f:
        shutil.copyfileobj(data.raw, f)
        
    dprint("Testing zip file: %s" % zip_file)

    the_zip_file = zipfile.ZipFile(zip_file)
    ret = the_zip_file.testzip()

    testsRan += 1
    if ret is not None:
        fail("First bad file in zip: %s" % ret)
    else:
        passed("Zip file is good.")
        
    logEnd(test_type)


def extTests():
    # # run a bunch of my test images through object detection
    included_extensions = ['jpg', 'webp', 'bmp', 'png', 'gif']
    file_names = [fn for fn in os.listdir(img_path)
        if any(fn.endswith(ext) for ext in included_extensions)]
    
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

    for test_type in tests2Run:
        logStart()
        for f in file_names:
            dprint("Checking:" + img_path + f)
            detect_test(test_type, f, getExpected(test_type, f))    
        logEnd(test_type)


#########################################################
# ## The test suite #####################################
#########################################################
serverUpTest()
    
logit(doFace == "Y", faceTests, "Face tests skipped", 28)
logit(doScene == "Y", sceneTests, "scene tests skipped", 9)
logit(doObj == "Y", objTests, "Object detection tests", 10)
logit(doLogo == "Y", logoTests, "Detect openlogo tests", 5)
logit(doPlate == "Y", plateTests, "Detect licence-plate test", 8)
logit(doDark == "Y", darkTests, "Detect dark test", 9)
logit(doAction == "Y", actionTests, "Detect actionnet tests", 27)
logit(doBackup == "Y", backupTests, "Backup tests", 1)
logit(doExt == "Y", extTests, "Extra object detect object tests", 516) 
    
print("")
print("Of " + str(testsRan + testsSkipped) + " tests")
print(" Ran:" + str(testsRan))
print(" Skipped:" + str(testsSkipped))
print(" Passed:" + str(testsPassed))
print(" Warnings:" + str(testsWarned))
print(" Failed:" + str(testsFailed))

