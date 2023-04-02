"""Finds all the class IDs in 'fromPath'(/train)/classes.txt
Creates cropped images for each label in the image file maps in 'fromPath'/train, 'fromPath'/labeled and 'fromPath'/test  to 'debugPath'/dump/label name
Note tested with Python 3.9 on Windows
"""

from datetime import datetime
import os
import sys

from common import dprint, setPaths, clearDebugPics, readTextFile, getImgNames, mkdirs, saveExpected, \
    genFolder, passed, fail   
import config


class DumpMap():

    def dumpMap(self, srcPath):
        
        if not os.path.exists(srcPath):
            return 

        imgCnt = 0
        objCnt = 0

        startTime = datetime.now()
        classes = []
        clsPath = os.path.join(srcPath, "classes.txt")
        if os.path.exists(clsPath):
            classes = readTextFile(clsPath).splitlines()
        else:
            clsPath = os.path.join(config.trainPath, "classes.txt")
            if os.path.exists(clsPath):
                classes = readTextFile(clsPath).splitlines()
        
        if len(classes) == 0:
            raise ValueError(config.trainPath + "classes.txt does not exist!")
        
        dprint(classes)
        
        imgNames = getImgNames(srcPath)
    
        for fn in imgNames:
            idx = fn.rfind('.')
            expf = fn[0:idx] + ".txt"
            txtPath = os.path.join(srcPath, expf)
            if not os.path.exists(txtPath):
                txtPath = os.path.join(srcPath, fn + ".detection.txt")

            if os.path.exists(txtPath):
                data = readTextFile(txtPath).splitlines()
                dprint(data)
                i = 0
                for line in data:
                    idx = line.find(' ')
                    c = int(line[0:idx])
                    try:
                        objPath = os.path.join(config.debugPath, classes[c])
                        mkdirs(objPath)
                        saveExpected(line[idx:], os.path.join(srcPath, fn), os.path.join(objPath, fn + "." + str(i) + ".jpg"))
                        i += 1
                        objCnt += 1   
                        passed("Dumped " + classes[c] + " image")                 
                    except IndexError:
                        fail("Error: Class ID %d in %s is out of range 0-%d" % (c, txtPath, len(classes)))
                imgCnt += 1
        
        print("\nDumped " + str(objCnt) + " objects from " + str(imgCnt) + " images in " + srcPath + " tests in " + str(datetime.now() - startTime))
        
    def run(self, argv=[]):
        global classes

        # if no arg or -h then usage
        if len(argv) < 2 or argv[1] == "-h":
            print("USAGE: dumpMap [-h] fromPath")
            print("-h prints this help")
            print("Finds all the class IDs in 'fromPath'(/train)/classes.txt")
            print("Creates cropped images for each label in the image file maps in 'fromPath'/train, 'fromPath'/labeled and 'fromPath'/test  to 'debugPath'/dump/label name")
        else: 
            setPaths(argv[1])    
            
            config.debugPath = genFolder(config.debugPath, "dump")
            clearDebugPics()
                        
            self.dumpMap(config.trainPath)        
            self.dumpMap(config.labeled)
            self.dumpMap(config.testPath)


#############################################################
DumpMap().run(sys.argv)
