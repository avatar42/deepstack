import os
import sys

import numpy

from common import logStart, logEnd, dprint, setPaths, readTextFile, getImgNames, appendDebugList, clearDebugLists, \
    warn, skipped, passed, writeList, saveLabels2labelImgData
import config

"""
Remap map files in labeled to use the classes.txt in train
Or report what classes are used in dataset's folders
Note tested with Python 3.9 on Windows
"""


class ChkClasses():

    clsCnt = []
    mergedClasses = []
    idxMap = []
    keptCls = 0
    tossCls = 0
    
    def cntUsed(self, folder, classes):
    
        imgNames = getImgNames(folder)
    
        for fn in imgNames:
            idx = fn.rfind('.')
            expf = fn[0:idx] + ".txt"
            fpath = os.path.join(folder, expf)
            if os.path.exists(fpath):
                data = readTextFile(fpath).splitlines()
                dprint(data)
                for line in data:
                    idx = line.find(' ')
                    c = int(line[0:idx])
                    if c > -1:
                        try:
                            name = classes[c]
                        except IndexError:
                            name = "class" + str(len(classes))
                            classes.append(name)
                        try:
                            i = self.mergedClasses.index(name)
                            self.clsCnt[i] += 1
                        except ValueError:
                            warn(name + " not in mergedClasses adding from " + fn)
                            self.mergedClasses.append(name)
                            i = self.mergedClasses.index(name)
                            self.clsCnt[i] = 1
                    appendDebugList(name, fn, 0)
            else:
                skipped("Missing label file " + fpath + ", skipping ", 1)
        
        return imgNames
    
    """create map between class IDs used in labeled and trainPath folders"""

    def genMap(self, minCnt, newClasses):
        with open(os.path.join(config.labeled, "classes.map.txt"), "w") as fout:
            if fout.mode == "w":
                clsOut = []
                i = 0
                if (minCnt > -1):
                    dprint("Removing classes with less than " + str(minCnt) + " training images")
                    
                for index in range(len(self.mergedClasses)):
                    name = self.mergedClasses[index]
                    if self.clsCnt[index] >= minCnt:
                        # add name to classes list
                        clsOut.append(self.mergedClasses[index])
                        srcdId = "train only"
                        # if in new classes add to map
                        try:
                            srcdId = newClasses.index(name)
                            self.idxMap[srcdId] = clsOut.index(name)
                            line = "Mapping:" + str(srcdId) + ":" + name + " used " + str(self.clsCnt[index]) + " times to " + str(self.idxMap[srcdId]) + ":" + clsOut[self.idxMap[srcdId]]
                            passed(line)
                            fout.write(line + "\n")
                            self.keptCls += 1
                        except ValueError:
                            line = "Not mapping:" + str(index) + ":" + name + " used " + str(self.clsCnt[index]) + " times, since only in " + config.trainPath
                            passed(line)
                            fout.write(line + "\n")
                            self.keptCls += 1
                           
                        i += 1
                    else:
                        self.idxMap[index] = -1
                        warn("Tossing:" + str(index) + ":" + self.mergedClasses[index] + " used " + str(self.clsCnt[index]) + " times")
                        self.tossCls += 1
        return clsOut
    
    """"Look at all the image maps and remove all the classes from classes.txt that are not used more than minCnt times"""

    def doChk(self, minCnt):
        dprint("minCnt:" + str(minCnt))
        logStart()
    
        orgClasses = readTextFile(os.path.join(config.trainPath, "classes.txt")).splitlines()
        dprint(orgClasses)
    
        newClasses = readTextFile(os.path.join(config.labeled, "classes.txt")).splitlines()
        dprint(newClasses)
        
        for cls in orgClasses:
            self.mergedClasses.append(cls)
    
        for cls in newClasses:
            if not cls in self.mergedClasses:
                self.mergedClasses.append(cls)
    
        newCnt = len(self.mergedClasses) + len(orgClasses)
        self.clsCnt = numpy.zeros(newCnt)
        x = numpy.arange(newCnt, dtype=int)
        self.idxMap = numpy.full_like(x, 1)
        
        orgCnt = []
        self.cntUsed(config.trainPath, orgClasses)
        if minCnt == -1:
            print("\nIn " + config.trainPath + " from mapping files")
            for index in range(len(self.mergedClasses)):
                print(str(index) + ":" + self.mergedClasses[index] + " used " + str(self.clsCnt[index]) + " times.")
            
            testPath = os.path.join(config.trainPath, "../test")
            if os.path.exists(testPath):
                orgCnt = self.clsCnt
                self.clsCnt = numpy.zeros(newCnt)
                self.cntUsed(testPath, orgClasses)
                print("\nIn " + testPath + " from mapping files")
                for index in range(len(self.mergedClasses)):
                    print(str(index) + ":" + self.mergedClasses[index] + " used " + str(self.clsCnt[index]) + " times.")
                
            orgCnt = self.clsCnt
            self.clsCnt = numpy.zeros(newCnt)
            if os.path.exists(config.labeled):
                orgCnt = self.clsCnt
                self.clsCnt = numpy.zeros(newCnt)
                imgNames = self.cntUsed(config.labeled, newClasses)
                if len(imgNames) > 0:
                    print("\nIn " + config.labeled + " from mapping files")
                    for index in range(len(self.mergedClasses)):
                        print(str(index) + ":" + self.mergedClasses[index] + " used " + str(self.clsCnt[index]) + " times.")
                        self.clsCnt[index] += orgCnt[index]
            
            writeList(config.debugPath , "classes.txt", self.mergedClasses)
        else:
            # move images in unlabeled to labeled
            imgNames = getImgNames(config.unlabeled)
            for fn in imgNames:
                os.rename(os.path.join(config.unlabeled, fn), os.path.join(config.labeled, fn))
            imgNames = self.cntUsed(config.labeled, newClasses)
    
        clsOut = self.genMap(minCnt, newClasses) 
                
        if minCnt > -1:
            writeList(config.trainPath , "classes.txt", clsOut)
            saveLabels2labelImgData(clsOut)
      
            print("\nKept " + str(self.keptCls) + " classes and tossed " + str(self.tossCls))
            
            for fn in imgNames:
                idx = fn.rfind('.')
                expf = fn[0:idx] + ".txt"
                fpath = os.path.join(config.labeled, expf)
                if os.path.exists(fpath):
                    data = readTextFile(fpath).splitlines()
                    dprint(data)
                    tags = []
                    ok2write = True
                    for line in data:
                        idx = line.find(' ')
                        c = int(line[0:idx])
                        if (c == -1 or self.idxMap[c] == -1):
                            ok2write = False
                        else:
                            tags.append(str(self.idxMap[c]) + line[idx:])
                    dprint(tags)
                    if ok2write:
                        writeList(config.trainPath , expf, tags)
                        if (config.debugPrintOn == "N"):
                            os.remove(os.path.join(config.labeled , expf))                    
                        os.rename(os.path.join(config.labeled , fn), os.path.join(config.trainPath , fn))
        logEnd("classes")

    def run(self, argv=[]):
        if len(argv) < 2 or argv[1] == "-h":
            print("USAGE: chkClasses [-h] minCount [trainPath]")
            print(" where 'minCount' is the minimum number of training images required to keep a class")
            print(" if 'minCount' is -1 only a report is performed on trainPath.")
            print(" if 'trainPath' is passed then it overrides the settings for 'trainPath', 'labeled', 'unlabeled' and 'debugPath' in common.py to have the same parent as 'trainPath'")
            print("\nUpdates file using object lists objName+'.lst.txt' in 'debugPath'")
            print("\nif not in 'report only; mode does the following:")
            print("At start moves images in 'unlabeled' to 'labeled' folder")
            print("Creates new merged classes file with those not meeting 'minCount' removed")
            print("Creates class ID mapping table and saves a copy to classes.map.txt in 'labeled' folder")
            print("Images and maps that do not use the filtered classes are remapped to the new class IDs and moved to 'trainPath'")
            print("The unaltered classes.txt plus images and maps that do use the filtered classes are left in the labeled' folder in case needed later")
        else:
            if len(argv) > 2:
                setPaths(argv[2])
            if len(argv) > 1:
                clearDebugLists()       
                self.doChk(int(argv[1]))
    
ChkClasses().run(sys.argv)
