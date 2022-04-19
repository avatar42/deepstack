

"""
Unit test for these tools. Mostly quick and dirty.
"""

import os

from common import setPaths, getTestRan, getTestsPassed, \
     getTestsSkipped, resetTestCnts, chkTestCnts, getTestsWarned, getTestsFailed, \
    logStart, logEnd, clearFolder, clearDebugPics, chkFileCnt
import config
from dumpMaps import DumpMap
from pascalvoc2yolo import Pascalvoc2yolo
from testImg import TestImg


class TestSuite():
    testsRan = 0
    testsSkipped = 0
    testsFailed = 0
    testsPassed = 0
    testsWarned = 0

    """ Add tool's test counts to total"""

    def addCnts(self):
        self.testsRan += getTestRan()
        self.testsSkipped += getTestsSkipped()
        self.testsFailed += getTestsFailed()
        self.testsPassed += getTestsPassed()
        self.testsWarned += getTestsWarned()
        # Some tools use getTestRan and testsPassed to return other values so added the diff here.
        self.testsPassed += getTestRan() - getTestsPassed() - getTestsWarned() - getTestsPassed()
        
    def pascalvoc2yolo(self):
        resetTestCnts()        
        setPaths("", "unit.tests/new")
        # chk test files we need are there
        clearFolder(config.labeled)
        clearFolder(config.unlabeled)
        clearDebugPics()
        chkFileCnt(config.newPicPath, [], 7)
        
        Pascalvoc2yolo().run()
        # do simple checks that files were processed
        # images with label files plus copy of classes.txt from train
        chkFileCnt(config.labeled, [], 7)
        chkFileCnt(config.unlabeled, [], 1)
        chkTestCnts(18, 5, 1, 0, 0)
        self.addCnts()
        
    def testImg(self):
        resetTestCnts()
        setPaths("unit.tests/train", "")
        chkFileCnt(config.trainPath, [], 3)
        TestImg().run(["testImg", "unit.tests/train/DAH412.20220207_143917.3491506.3-1.jpg"])
        chkFileCnt(config.debugPath, [], 11)
        chkTestCnts(20, 19, 0, 0, 0)
        self.addCnts()

    def dumpMaps(self):
        resetTestCnts()
        setPaths("unit.tests/train", "")
        DumpMap().run()
        chkFileCnt(config.debugPath, [], 13)
        chkTestCnts(18, 19, 0, 0, 0)
        self.addCnts()

    """ Run all the unit tests.
    Note currently tests should be run in this order
    """

    def runAll(self): 
        logStart()
        self.pascalvoc2yolo()
        logEnd("pascalvoc2yolo")
        
        logStart()
        self.testImg()
        logEnd("testImg")
        
        logStart()
        self.dumpMaps()
        logEnd("dumpMaps")

        print("")
        print("Of " + str(self.testsRan + self.testsSkipped) + " total tests")
        print(" Ran:" + str(self.testsRan))
        print(" Skipped:" + str(self.testsSkipped))
        print(" Passed:" + str(self.testsPassed))
        print(" Warnings:" + str(self.testsWarned))
        print(" Failed:" + str(self.testsFailed))


TestSuite().runAll()
