

"""
Unit test for these tools. Mostly quick and dirty just to make sure nothing broke from a change.
"""

import os
import shutil

from chkClasses import ChkClasses
from common import setPaths, getTestRan, getTestsPassed, \
     getTestsSkipped, resetTestCnts, chkTestCnts, getTestsWarned, getTestsFailed, \
    logEnd, clearFolder, clearDebugPics, chkFileCnt, skipped, getImgNames, \
    assertTrue, compareMapFiles, \
    readClassList
import config
from cpClasses import CpClasses
from dumpMaps import DumpMap
from pascalvoc2yolo import Pascalvoc2yolo
from testImg import TestImg


class TestSuite():
    testsRan = 0
    testsSkipped = 0
    testsFailed = 0
    testsPassed = 0
    testsWarned = 0

    """ Add tool's test counts to totals"""

    def addCnts(self, label):
        self.testsRan += getTestRan()
        self.testsSkipped += getTestsSkipped()
        self.testsFailed += getTestsFailed()
        self.testsPassed += getTestsPassed()
        self.testsWarned += getTestsWarned()
        # Some tools use getTestRan and testsPassed to return other values so added the diff here.
        otherTests = getTestRan() - getTestsPassed() - getTestsWarned() - getTestsFailed()
        self.testsPassed += otherTests
        logEnd(label)
       
    def pascalvoc2yoloTests(self):
        resetTestCnts("Starting pascalvoc2yolo tests")                
        Pascalvoc2yolo().run(["pascalvoc2yolo", "unit.tests/new"])
        # do simple checks that files were processed
        # images with label files plus copy of classes.txt from train
        chkFileCnt(config.labeled, [], 7)
        chkFileCnt(config.unlabeled, [], 1)
        imgNames = getImgNames(config.labeled)
        for fn in imgNames:
            compareMapFiles(config.labeled, config.validPath, fn)

        # expected skip is image without map file to test handler skips cleanly        
        chkTestCnts(48, 34, 1, 0, 0)
        self.addCnts("pascalvoc2yolo")
        
    def testImgTests(self):
        resetTestCnts("Starting testImg tests")        
        chkFileCnt(config.trainPath, [], 1)
        TestImg().run(["testImg", "unit.tests/train/DAH412.20220207_143917.3491506.3-1.jpg"])
        chkFileCnt(config.debugPath, [], 13)
        compareMapFiles(config.debugPath, config.validPath, "DAH412.20220207_143917.3491506.3-1.jpg")
        # expected skip and 9 warns are from there being no classes file in train at start   
        chkTestCnts(33, 32, 1, 0, 9)
        self.addCnts("testImg")
        # copy map for later tests
        shutil.copy(os.path.join(config.debugPath, "DAH412.20220207_143917.3491506.3-1.txt"), config.trainPath)
        shutil.copy(os.path.join(config.debugPath, "classes.txt"), config.trainPath)

    """ Needs RMRR.Fire project to run
    gets helicopter images from RMRR.Fire to merge into test set.
    """

    def cpClassesTests(self):
        fromPath = "../RMRR.fire/train"
        toPath = "./unit.tests/labeled/"
        testCnt = 593
        if os.path.exists(fromPath):
            resetTestCnts("Starting cpClasses tests")        
            # USAGE: cpClasses classNameSubString toPath [fromPath]
            CpClasses().run(["cpClasses", "heli", toPath, fromPath])
            chkFileCnt(config.debugPath, [], 13)
            chkFileCnt(toPath, [], 59)
            labeledClasses = readClassList("./unit.tests/train/")
            assertTrue("Merged classes missing helicopter", "helicopter" in labeledClasses)
            assertTrue("Labeled classes has clouds", not "clouds" in labeledClasses)
            labeledClasses = readClassList(toPath)
            assertTrue("Labeled classes missing clouds", "clouds" in labeledClasses)
            compareMapFiles(toPath, "./unit.tests/valid/", "HV411.20200819_190218_helicopter.00_00_05_08.Still003.txt")
            chkTestCnts(testCnt, testCnt, 0, 0, 0)
            self.addCnts("cpClasses")
        else:
            skipped(fromPath + " not found", testCnt)

    def dumpMapsTests(self):
        resetTestCnts("Starting dumpMaps tests")        
        # USAGE: dumpMap [-h] fromPath
        DumpMap().run(["dumpMap", "unit.tests/train"])
        chkFileCnt(config.debugPath, [], 21)
        chkTestCnts(32, 116, 0, 0, 0)
        self.addCnts("dumpMaps")

    def chkClassesTests(self):
        resetTestCnts("Starting chkClasses tests")        
        # run report mode
        ChkClasses().run(["chkClasses", "-1", "unit.tests/train"])
        chkFileCnt(config.debugPath, [], 12)
        chkTestCnts(1, 1, 0, 0, 0)
        self.addCnts("dumpMaps")

    """ Run all the unit tests.
    Note currently tests should be run in this order
    """

    def runAll(self): 
        # make sure test folders have just the files they should have and clean old output if there
        setPaths("", "unit.tests/new")
        chkFileCnt(config.newPicPath, [], 7)
        # chk test files we need are there
        clearFolder(config.labeled)
        clearFolder(config.unlabeled)
        clearDebugPics()
        oldFile = os.path.join(config.trainPath, "classes.txt")
        if os.path.exists(oldFile):
            os.remove(oldFile)
        oldFile = os.path.join(config.trainPath, "DAH412.20220207_143917.3491506.3-1.txt")
        if os.path.exists(oldFile):
            os.remove(oldFile)

        chkFileCnt(config.trainPath, [], 1)
        chkFileCnt(config.validPath, [], 4)
        self.addCnts("setup")

        self.pascalvoc2yoloTests()
        self.testImgTests() 
        self.cpClassesTests()
        self.dumpMapsTests()
        self.chkClassesTests()

        print("=====================================")
        print("Of " + str(self.testsRan + self.testsSkipped) + " total tests")
        print(" Ran:" + str(self.testsRan))
        print(" Skipped:" + str(self.testsSkipped))
        print(" Passed:" + str(self.testsPassed))
        print(" Warnings:" + str(self.testsWarned))
        print(" Failed:" + str(self.testsFailed))


TestSuite().runAll()
