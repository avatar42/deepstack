"""Copy images and maps that have certain objects in them from one dataset to another
Note tested with Python 3.9 on Windows
"""

import os
import shutil
import sys

from common import dprint, setPaths, genFolder, readTextFile, getImgNames, writeList, \
    getMapFileName, readClassList, assertTrue
import config


class CpClasses():

    def cpData(self, cpIDs, toPath, fromPath):
            
        imgNames = getImgNames(fromPath)
    
        cnt = 0
        for fn in imgNames:
            mapFn = getMapFileName(fromPath, fn)
            if os.path.exists(mapFn):
                data = readTextFile(mapFn).splitlines()
                dprint(data)
                doCp = False
                for line in data:
                    idx = line.find(' ')
                    c = int(line[0:idx])
                    if c in cpIDs:
                        doCp = True
                    
                if doCp: 
                    shutil.copy(os.path.join(fromPath, fn), toPath)
                    shutil.copy(mapFn, toPath)
                    cnt += 1
        
        print("Copied " + str(cnt) + " images from " + fromPath + " to " + toPath + " with their mapping files")

    def run(self, argv=[]):
        if len(argv) < 3:
            print("USAGE: cpClasses classNameSubString toPath [fromPath]")
            print("If 'fromPath' not passed then defaults to trainPath defined in common.py")
            print("Finds all the class IDs in 'fromPath'/train/classes.txt which have names that include 'classNameSubString'")
            print("Copies 'fromPath'/train/classes.txt to 'toPath'/labeled/classes.txt to use automated merge later")
            print("Note this overwrites 'toPath'/labeled/classes.txt.")
            print("Creates or updates 'toPath'/train/classes.txt with the class names being used to copy")
            print("Then finds all the mapping folder in 'fromPath'/train folder using those IDs and copies them and their matching image folder to 'toPath'/labeled")
            print("Then finds all the mapping folder in 'fromPath'/test folder using those IDs and copies them and their matching image folder to 'toPath'/labeled")
            print("Then finds all the mapping folder in 'fromPath'/valid folder using those IDs and copies them and their matching image folder to 'toPath'/labeled")
        else: 
            if len(argv) > 3:
                setPaths(argv[3])
            findString = argv[1]
            toPath = genFolder(argv[2], "labeled/")
            labeledClassFile = os.path.join(toPath, "classes.txt")
            assertTrue(labeledClassFile +" exists",os.path.exists(labeledClassFile))
                
            # read the class list of the folder we are importing
            orgClasses = readClassList(config.trainPath)
            if len(orgClasses) == 0:
                raise ValueError(config.trainPath + "classes.txt does not exist!")
            
            shutil.copy(os.path.join(config.trainPath, "classes.txt"), toPath)

            orgCnt = len(orgClasses)
            dprint(orgClasses)

            # read the class list in labeled folder if there is one.
            newClasses = readClassList(toPath)
            
        # # get set of IDs which include findString and append to classes.txt in toPath as needed
            cpIDs = []
            for index in range(orgCnt):
                if orgClasses[index].find(findString) > -1:
                    cpIDs.append(index)
                    print("Found:" + orgClasses[index])
                    if not orgClasses[index] in newClasses:
                        newClasses.append(orgClasses[index])
             
            writeList(genFolder(argv[2], "train/") , "classes.txt", newClasses)   
            print("Added to " + os.path.join(toPath , "classes.txt") + ":")
            print(newClasses)
    
            self.cpData(cpIDs, toPath, config.trainPath)
            self.cpData(cpIDs, toPath, config.testPath)
            self.cpData(cpIDs, toPath, config.validPath)

    
#############################################################    
CpClasses().run(sys.argv)
