import sys
import os
from common import logStart, logEnd, dprint, setTrainPath, clearDebugPics, readTextFile, getImgNames, mkdirs, saveExpected
import config

"""Finds all the class IDs in 'fromPath'(/train)/classes.txt
Creates cropped images for each label in the image file maps in 'fromPath'/train, 'fromPath'/labeled and 'fromPath'/test  to 'debugPath'/dump/label name
Note tested with Python 3.9 on Windows
"""
class DumpMap():
    
    classes = []

    def dumpMap(self, srcPath):
        global classes
        
        if not os.path.exists(srcPath):
            return 

        imgCnt = 0
        objCnt = 0

        logStart()
        
        dprint(classes)
        
        imgNames = getImgNames(srcPath)
    
        for fn in imgNames:
            idx = fn.rfind('.')
            expf = fn[0:idx] + ".txt"
            txtPath = os.path.join(srcPath, expf)
            if os.path.exists(txtPath):
                data = readTextFile(txtPath).splitlines()
                dprint(data)
                i = 0
                for line in data:
                    idx = line.find(' ')
                    c = int(line[0:idx])
                    objPath = os.path.join(config.debugPath, classes[c])
                    mkdirs(objPath)
                    saveExpected(line[idx:], os.path.join(srcPath, fn), os.path.join(objPath, fn + "." + str(i) + ".jpg"))
                    i += 1
                    objCnt += 1                    
                
                imgCnt += 1
        
        logEnd("Dumped " + str(objCnt) + " objects from " + str(imgCnt) + " images in " + srcPath)
        
    def run(self):
        global classes

        config.debugPath = os.path.join(config.debugPath, "dump")
        clearDebugPics()
        
        classes = readTextFile(config.trainPath + "classes.txt").splitlines()
        if len(classes) == 0:
            raise ValueError(config.trainPath + "classes.txt does not exist!")
        
        self.dumpMap(config.trainPath)        
        self.dumpMap(config.labeled)
        self.dumpMap(config.testPath)


# # if no arg or -h then usage
if len(sys.argv) < 2:
    sys.argv[1] = "-h"
        
if sys.argv[1] == "-h":
    print("USAGE: " + sys.argv[0] + " [-h] fromPath")
    print("-h prints this help")
    print("Finds all the class IDs in 'fromPath'(/train)/classes.txt")
    print("Creates cropped images for each label in the image file maps in 'fromPath'/train, 'fromPath'/labeled and 'fromPath'/test  to 'debugPath'/dump/label name")
    os._exit(1)

if len(sys.argv) > 1:
    setTrainPath(sys.argv[1])

DumpMap().run()
