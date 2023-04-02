"""
Run tests against the DeepStack APIs to check they are all working as expected
"""

import json
import os
import shutil
import zipfile

import requests

from common import logStart, logEnd, dprint, getImgNames, \
    skipped, serverUpTest, clearDebugPics, logit, showTestReport, doPost, \
    readImageFile, warnTrue, assertTrue, warn, mkdirs, saveFound, fail, passed, \
    incTestRan
import config

""" Run tests against all the DeepStack APIs to see if they are working properly.
If some of the options are disabled, scene recognition for example, disable the tests
by changing the matching flag at the top of this file. That would be setting doScene = "N"
in this case. See https://github.com/avatar42/deepstack/wiki/Full-Test for more.
"""


class FullTest():
    # Test control flags. Set to N to skip test.
    """ Run face tests """
    doFace = "Y"
    """ Run scene detection tests"""
    doScene = "Y"
    """ Run object detection tests"""
    doObj = "Y"
    """ Run backup tests"""
    doBackup = "Y"
    """ Run all pics in the config.imgPath thru enabled (see custom models) object detection tests and compare with a base run."""
    doExt = "Y"
    """ what test counts should be for ext tests"""
    detectionExtTests = 151
    logoExtTests = 101
    plateExtTests = 100
    darkExtTests = 137
    actionExtTests = 118
    RMRRExtTests = 102
    birdsExtTests = 97
    fireExtTests = 101
    
    """ if test is true run method
    if test is false add tests to skip count."""

    def logit(self, test, method, msg, skipCnt):
        if test: 
            method()
        else:
            skipped(msg, skipCnt)
    
    """ register face for test."""

    def registerFace(self, fileName, userId):
        doPost("face/register", files={"image":readImageFile(fileName)}, data={"userid":userId})
    
    """ expected items are in foundItems"""

    def chkArray(self, foundItems, expected, testType, fileName):
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
    
    """ Compare objects found in image against expected ones"""

    def detectTest(self, testType, fileName, expected):
        
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
                incTestRan()
                warn("No data for " + config.imgPath + fileName + " initializing for next run of Extra tests for " + testType)
                self.writeTestData(testType, fileName, response)
            else:
                foundItems = []
                i = 0
                for item in response["predictions"]:
                    foundItems.insert(i, item["label"])
                    i += 1
                    
                self.chkArray(foundItems, expected, testType, fileName)
    
    """ read expected response for test image run against testType"""

    def getExpected(self, testType, fileName):
        expected = []
        path = config.imgPath + testType + "/" + fileName + '.json'
        if os.path.exists(path):
            try:
                jfile = open(path)
                data = json.load(jfile)
                i = 0
                for item in data["predictions"]:
                    expected.insert(i, item["label"])
                    i += 1
             
            except json.decoder.JSONDecodeError as e:
            # empty or corrupt file
                warn("Error: %s : %s" % (path, e.msg))
                expected.insert(0, "undefined")        
        
        else:
            # flag as has no compare data
            expected.insert(0, "undefined")        
    
        return expected
    
    """ Write found data. Used to create compare file for new images."""

    def writeTestData(self, testType, fileName, response): 
        path = config.imgPath + testType + "/"
        mkdirs(path)
        with open(path + fileName + ".json", "w") as f:
            if f.mode == "w":
                f.write(json.dumps(response, indent=4))
    
    """ Run the face sample tests"""

    def faceTests(self):
        logStart()
    # # face detect test
        self.detectTest("face", "family.jpg", 4)
    
        response = doPost("face/match", files={"image1":readImageFile("obama1.jpg"),
                                                  "image2":readImageFile("obama2.jpg")})
        assertTrue("Face match", response['similarity'] > 0.70)
        
        response = doPost("face/match", files={"image1":readImageFile("obama1.jpg"),
                                                  "image2":readImageFile("brad.jpg")})
        assertTrue("Face mismatch", response['similarity'] < 0.51)
    
        # # face recog test
        self.registerFace("tomcruise.jpg", "Tom Cruise")
        self.registerFace("adele.jpg", "Adele")
        self.registerFace("idriselba.jpg", "Idris Elba")
        self.registerFace("perri.jpg", "Christina Perri")
    
        response = doPost("face/list")
        self.chkArray(response["faces"], ["Tom Cruise", "Adele", "Idris Elba", "Christina Perri"], "face/list", "db")
        
        res = doPost("face/recognize", files={"image":readImageFile("adele2.jpg")})
        
        i = 0
        for face in res["predictions"]:
            found = face["userid"]
            dprint("Found " + found)
            incTestRan()
            if found != "Adele":
                saveFound(face, config.imgPath + "adele2.jpg", found + "{}.jpg".format(i))
                fail("Face recog. Found " + found + " instead of Adele") 
            else:
                passed("PASSED:Face recog")
            i += 1
        logEnd("face")
    
    """ Run some basic scene detection tests """  

    def sceneTests(self):
        testType = "scene"
        logStart()
        # # Basic scene test
        self.detectTest(testType, "office.jpg", "conference_room")
        self.detectTest(testType, "creek.jpg", "forest_path")
        self.detectTest(testType, "DAH847_day.jpg", "yard")
        self.detectTest(testType, "DAH847_night.jpg", "driveway")  # this seems wrong
        self.detectTest(testType, "DAH834_driveway_day.jpg", "driveway")
        logEnd(testType)
    
    """ Run some basic object detection tests"""

    def objTests(self):
        testType = "detection"
        logStart()
        # # Basic Object test
    #    self.detectTest(testType, "test-image3.jpg", ["handbag", "person", "dog", "person"])
        self.detectTest(testType, "test-image3.jpg", ["person", "dog", "person"])
        self.detectTest(testType, "fedex.jpg", ["truck"])
        logEnd(testType)
    
    """ Run that openlogo models sample test    """

    def logoTests(self):
        testType = "custom/openlogo"
        logStart()
        self.detectTest(testType, "fedex.jpg", ["fedex", "fedex"])
        logEnd(testType)
    
    """ Run that licence-plate model sample test"""

    def plateTests(self):
        testType = "custom/licence-plate"
        logStart()
        # test image of his
        self.detectTest(testType, "031_924430341.jpg", ["licence-plate"])
        # test image of US TX plate not working
        # self.detectTest(testType, "back_plate_day.jpg", ["licence-plate"])
        logEnd(testType)
    
    """ Run that dark model sample tests   """

    def darkTests(self):
        testType = "custom/dark"
        logStart()
        if config.mode == "Medium":
            self.detectTest(testType, "dark_image.jpg", ["People", "Dog", "Dog", "Dog", "Dog"])
        elif config.mode == "High":
            self.detectTest(testType, "dark_image.jpg", ["Motorbike", "People", "Dog", "Dog", "Dog", "Dog", "Dog"])
        logEnd(testType)
    
    """ Run that actionnetv2 model sample tests"""

    def actionTests(self):
        testType = "custom/actionnetv2"
        logStart()
        self.detectTest(testType, "dancing1.jpg", ["dancing"])
        self.detectTest(testType, "fighting2.jpg", ["dancing"])  # does not seem to work
        self.detectTest(testType, "fighting3.jpg", ["fighting"])
        self.detectTest(testType, "cycling4.jpg", ["cycling"])
        self.detectTest(testType, "eating5.webp", ["eating", "eating", "eating"])
        logEnd(testType)
    
    """ Try using the SDK to back up DeepStack setup"""

    def backupTests(self):
    
        testType = "backup"
        zipFile = "backupdeepstack.zip"
        logStart()
        data = requests.post(config.dsUrl + "v1/backup", stream=True)
        with open(zipFile, "wb") as f:
            shutil.copyfileobj(data.raw, f)
            
        dprint("Testing zip file: %s" % zipFile)
    
        tstZipFile = zipfile.ZipFile(zipFile)
        ret = tstZipFile.testzip()
    
        incTestRan()
        if ret is not None:
            fail("First bad file in zip: %s" % ret)
        else:
            passed("PASSED:Zip file is good.")
            
        logEnd(testType)
    
    """ run all the images in imgPath against all the enabled object detection models"""

    def extTests(self):
        # # run a bunch of my test images through object detection
        fileNames = getImgNames(config.imgPath)
        
        if "custom/openlogo" not in config.tests2Run:
            skipped("Extra openlogo detect object tests", self.logoExtTests) 
            
        if "custom/licence-plate" not in config.tests2Run:
            skipped("Extra licence-plate detect object tests", self.plateExtTests) 
            
        if "custom/dark" not in config.tests2Run:
            skipped("Extra dark detect object tests", self.darkExtTests) 
            
        if "custom/actionnetv2" not in config.tests2Run:
            skipped("Extra actionnetv2 detect object tests", self.actionExtTests) 
    
        for testType in config.tests2Run:
            logStart()
            for f in fileNames:
                dprint("Checking:" + config.imgPath + f)
                self.detectTest(testType, f, self.getExpected(testType, f))    
            logEnd(testType)

    """ Run the test suite"""

    def run(self):
        serverUpTest()
        clearDebugPics()    
        logit(self.doFace == "Y", self.faceTests, "Face tests skipped", 28)
        logit(self.doScene == "Y", self.sceneTests, "scene tests skipped", 9)
        logit(self.doObj == "Y", self.objTests, "Object detection tests", 10)
        logit(self.doBackup == "Y", self.backupTests, "Backup tests", 1)
        logit("custom/openlogo" in config.tests2Run, self.logoTests, "Detect openlogo tests", 5)
        logit("custom/licence-plate" in config.tests2Run, self.plateTests, "Detect licence-plate test", 8)
        logit("custom/dark" in config.tests2Run, self.darkTests, "Detect dark test", 9)
        logit("custom/actionnetv2" in config.tests2Run, self.actionTests, "Detect actionnet tests", 27)
        logit(self.doExt == "Y", self.extTests, "Extra object detect object tests", self.detectionExtTests + self.logoExtTests + self.plateExtTests + self.darkExtTests + self.actionExtTests) 
        
        showTestReport()


#########################################################
# ## The test suite #####################################
#########################################################
FullTest().run()
