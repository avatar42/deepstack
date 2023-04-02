import sys
import os
import numpy
import shutil
import config
from common import logStart, logEnd, dprint, setPaths, showConfig, readTextFile, mv, getImgNames, writeList

"""Look at all the image maps and remove all the classes from classes.txt that are not used
Note tested with Python 3.9 on Windows"""


class MergeClasses():
    idxMap = []
    
    def genMap(self):
        global idxMap
        
        orgClasses = readTextFile(os.path.join(config.trainPath, "classes.txt.old")).splitlines()
        if len(orgClasses) == 0:
            raise ValueError(os.path.join(config.trainPath, "classes.txt.old") + " does not exist!")
        
        dprint(orgClasses)
    
        mapClasses = readTextFile(os.path.join(config.trainPath, "classes.txt")).splitlines()
        if len(orgClasses) == 0:
            raise ValueError(os.path.join(config.trainPath, "classes.txt") + " does not exist!")
        dprint(mapClasses)
        mv(os.path.join(config.trainPath, "classes.txt"), config.labeled)
        
        orgCnt = len(orgClasses)
        if not orgCnt == len(mapClasses):
            raise ValueError(config.trainPath + "classes.txt.old length does not match classes.txt")
        
        newClasses = []
        for cls in mapClasses:
            if not cls in newClasses:
                newClasses.append(cls)
        
        dprint(newClasses)
        writeList(config.trainPath , "classes.txt", newClasses)
        
        x = numpy.arange(orgCnt, dtype=int)
        idxMap = numpy.full_like(x, -2)
    
        with open(os.path.join(config.trainPath, "classes.map.txt"), "w") as fout:
            if fout.mode == "w":
                dprint("Creating mapping from classes.txt.old to classes.txt")
                for index in range(orgCnt):
                    i = newClasses.index(mapClasses[index])
                    idxMap[index] = i
                    msg = "Mapping:" + str(index) + ":" + orgClasses[index] + ", to " + str(i) + ":" + newClasses[i]
                    dprint(msg)
                    fout.write(msg + "\n")
    
    def mergeClasses(self, imgPath):
        global idxMap
            
        if not os.path.exists(imgPath):
            return 
        
        logStart()
        imgCnt = 0
        objCnt = 0
                   
        imgNames = getImgNames(imgPath)
        for fn in imgNames:
            idx = fn.rfind('.')
            expf = fn[0:idx] + ".txt"
            src = os.path.join(imgPath, expf)
            bak = os.path.join(config.labeled, expf)
            if os.path.exists(src):
                data = readTextFile(src).splitlines()
                dprint(data)
                tags = []
                for line in data:
                    idx = line.find(' ')
                    c = int(line[0:idx])
                    if (c > -1 and idxMap[c] > -1):
                        tags.append(str(idxMap[c]) + line[idx:])
                        
                    objCnt += 1
                        
                dprint(tags)
                dprint("Backing up " + src + " to " + config.labeled + bak)
                shutil.move(src, config.labeled)
                writeList(imgPath , expf, tags)
                imgCnt += 1
        
        logEnd("Remapped " + str(objCnt) + " objects in " + str(imgCnt) + " images in " + imgPath)

    def run(self):
        self.genMap()
        self.mergeClasses(config.trainPath)
        self.mergeClasses(config.testPath)
        self.mergeClasses(config.validPath)


# # if no arg 
if len(sys.argv) == 1:
    sys.argv.append("-h")
        
if sys.argv[1] == "-h":
    print("USAGE: " + sys.argv[0] + " [-h] trainPath")
    print("-h prints this help")
    print("Creates class ID mapping table between classes.txt and classes.txt.old then saves a copy to classes.map.txt in 'trainPath' folder")
    print("Remaps mappings in mapping files for classes names in classes.txt.old in classes.txt then saves a copy of classes.txt with dups removed to 'trainPath' folder.")
    print("Mainly used to merge classes like types of dog to just dog.")
    print("Note since this updates files directly there is no backup option.")
    os._exit(1)
else:
    if len(sys.argv) > 1:
        setPaths(sys.argv[1])
    else:
        showConfig()
        
    MergeClasses().run()
