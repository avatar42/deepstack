"""Copy images and maps that have certain objects in them from one dataset to another
Note tested with Python 3.9 on Windows
"""

import os
import shutil
import sys

from common import logStart, logEnd, dprint, setTrainPath, genFolder, readTextFile, getImgNames, writeList
import config


class CpClasses():

    def cpData(self, cpIDs, toPath, fromPath):
            
        logStart()
            
        imgNames = getImgNames(fromPath)
    
        cnt = 0
        for fn in imgNames:
            idx = fn.rfind('.')
            expf = os.path.join(fromPath, fn[0:idx] + ".txt")
            if os.path.exists(expf):
                data = readTextFile(expf).splitlines()
                dprint(data)
                for line in data:
                    idx = line.find(' ')
                    c = int(line[0:idx])
                    if c in cpIDs:
                        shutil.copy(os.path.join(fromPath, fn), toPath)
                        shutil.copy(expf, toPath)
                        cnt += 1
        
        logEnd("Copied " + str(cnt) + " images from " + fromPath + " to " + toPath + " with their mapping files")

    def run(self, findString, toPath):
        orgClasses = readTextFile(config.trainPath + "classes.txt").splitlines()
        if len(orgClasses) == 0:
            raise ValueError(config.trainPath + "classes.txt does not exist!")
        
        orgCnt = len(orgClasses)
        dprint(orgClasses)
        shutil.copy(os.path.join(config.trainPath, "classes.txt"), toPath)
        
        outPath = genFolder(toPath, "train/")  
        newClasses = readTextFile(os.path.join(outPath , "classes.txt")).splitlines()
        
    # # get set of IDs which include findString and build a reduced classes.txt in
        cpIDs = []
        for index in range(orgCnt):
            if orgClasses[index].find(findString) > -1:
                cpIDs.append(index)
                print("Found:"+orgClasses[index])
                if not orgClasses[index] in newClasses:
                    newClasses.append(orgClasses[index])
         
        writeList(outPath , "classes.txt", newClasses)   
        print("Updated " + os.path.join(outPath , "classes.txt") + " to:")
        print(newClasses)

        self.cpData(cpIDs, toPath, config.trainPath)
        self.cpData(cpIDs, toPath, config.testPath)
        self.cpData(cpIDs, toPath, config.validPath)


# # if no arg or -h then usage
if len(sys.argv) < 3:
    sys.argv[1] = "-h"
        
if sys.argv[1] == "-h":
    print("USAGE: cpClasses classNameSubString toPath [fromPath]")
    print("If 'fromPath' not passed then defaults to trainPath defined in common.py  ")
    print("Finds all the class IDs in 'fromPath'/train/classes.txt which have names that include 'classNameSubString'")
    print("Copies 'fromPath'/train/classes.txt to 'toPath'/train/classes.txt to use automated merge later")
    print("Creates or updates 'toPath'/train/classes.txt with the class names being used to copy")
    print("Then finds all the mapping files in 'fromPath'/train folder using those IDs and copies them and their matching image files to 'toPath'/labeled")
    print("Then finds all the mapping files in 'fromPath'/test folder using those IDs and copies them and their matching image files to 'toPath'/labeled")
    print("Then finds all the mapping files in 'fromPath'/valid folder using those IDs and copies them and their matching image files to 'toPath'/labeled")
    os._exit(1)

if len(sys.argv) > 3:
    setTrainPath(sys.argv[3])

if len(sys.argv) > 2:
    toPath = genFolder(sys.argv[2], "labeled/")
    
CpClasses().run(sys.argv[1], toPath)
