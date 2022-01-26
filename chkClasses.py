import os
import sys
import numpy
import config

# # Note tested with Python 3.9 on Windows
clsCnt = []
mergedClasses = []
idxMap = []


def cntUsed(folder, classes):
    global clsCnt

    imgNames = config.getImgNames(folder)

    for fn in imgNames:
        idx = fn.rfind('.')
        expf = fn[0:idx] + ".txt"
        fpath = os.path.join(folder, expf)
        if os.path.exists(fpath):
            data = config.readTextFile(fpath).splitlines()
            config.dprint(data)
            for line in data:
                idx = line.find(' ')
                c = int(line[0:idx])
                if c > -1:
                    name = classes[c]
                    try:
                        i = mergedClasses.index(name)
                        clsCnt[i] += 1
                    except ValueError:
                        config.fail(name + " not in mergedClasses")
            config.testsRan += 1 
        else:
            config.skipped("Missing label file " + fpath + ", skipping ", 1)
    
    return imgNames


def genMap(minCnt, newCnt, newClasses):
    with open(os.path.join(config.labeled, "classes.map.txt"), "w") as fout:
        if fout.mode == "w":
            clsOut = []
            i = 0
            if (minCnt > -1):
                config.dprint("Removing classes with less than " + str(minCnt) + " training images")
                
            for index in range(newCnt):
                name = mergedClasses[index]
                if clsCnt[index] >= minCnt:
                    # add name to classes list
                    clsOut.append(mergedClasses[index])
                    srcdId = "train only"
                    # if in new classes add to map
                    try:
                        srcdId = newClasses.index(name)
                        idxMap[srcdId] = clsOut.index(name)
                        line = "Mapping:" + str(srcdId) + ":" + name + " used " + str(clsCnt[index]) + " times to " + str(idxMap[srcdId]) + ":" + clsOut[idxMap[srcdId]]
                        config.passed(line)
                        fout.write(line + "\n")
                    except ValueError:
                        line = "Not mapping:" + str(index) + ":" + name + " used " + str(clsCnt[index]) + " times, since only in " + config.trainPath
                        config.passed(line)
                        fout.write(line + "\n")
                       
                    i += 1
                else:
                    idxMap[index] = -1
                    config.warn("Tossing:" + str(index) + ":" + mergedClasses[index] + " used " + str(clsCnt[index]) + " times")
    return clsOut


# # Look at all the image maps and remove all the classes from classes.txt that are not used more than minCnt times
def doChk(minCnt):
    global clsCnt
    global mergedClasses
    global idxMap
        
    config.logStart()

    orgClasses = config.readTextFile(os.path.join(config.trainPath, "classes.txt")).splitlines()
    config.dprint(orgClasses)

    newClasses = config.readTextFile(os.path.join(config.labeled, "classes.txt")).splitlines()
    config.dprint(newClasses)
    
    for cls in orgClasses:
        mergedClasses.append(cls)

    for cls in newClasses:
        if not cls in mergedClasses:
            mergedClasses.append(cls)

    newCnt = len(mergedClasses)
    clsCnt = numpy.zeros(newCnt)
    x = numpy.arange(newCnt, dtype=int)
    idxMap = numpy.full_like(x, 1)
    
    # move images in unlabeled to labeled
    imgNames = config.getImgNames(config.unlabeled)
    for fn in imgNames:
        os.rename(os.path.join(config.unlabeled, fn), os.path.join(config.labeled, fn))

    orgCnt = []
    cntUsed(config.trainPath, orgClasses)
    if minCnt == -1:
        print("\nIn " + config.trainPath + " from mapping files")
        for index in range(newCnt):
            print(str(index) + ":" + mergedClasses[index] + " used " + str(clsCnt[index]) + " times.")
        
        orgCnt = clsCnt
        clsCnt = numpy.zeros(newCnt)
        testPath = os.path.join(config.trainPath, "../test")
        cntUsed(testPath, orgClasses)
        print("\nIn " + testPath + " from mapping files")
        for index in range(newCnt):
            print(str(index) + ":" + mergedClasses[index] + " used " + str(clsCnt[index]) + " times.")
            
        orgCnt = clsCnt
        clsCnt = numpy.zeros(newCnt)
        imgNames = cntUsed(config.labeled, newClasses)
        if len(imgNames) > 0:
            print("\nIn " + config.labeled + " from mapping files")
            for index in range(newCnt):
                print(str(index) + ":" + mergedClasses[index] + " used " + str(clsCnt[index]) + " times.")
                clsCnt[index] += orgCnt[index]
    else:
        imgNames = cntUsed(config.labeled, newClasses)

    clsOut = genMap(minCnt, newCnt, newClasses) 
            
    if minCnt > -1:
        config.writeList(config.trainPath , "classes.txt", clsOut)
        config.saveLabels2labelImgData( clsOut)
  
        print("\nKept " + str(config.testsPassed) + " classes and tossed " + str(config.testsWarned))
        
        for fn in imgNames:
            idx = fn.rfind('.')
            expf = fn[0:idx] + ".txt"
            fpath = os.path.join(config.labeled, expf)
            if os.path.exists(fpath):
                data = config.readTextFile(fpath).splitlines()
                config.dprint(data)
                tags = []
                ok2write = True
                for line in data:
                    idx = line.find(' ')
                    c = int(line[0:idx])
                    if (c == -1 or idxMap[c] == -1):
                        ok2write = False
                    else:
                        tags.append(str(idxMap[c]) + line[idx:])
                config.dprint(tags)
                if ok2write:
                    config.writeList(config.trainPath , expf, tags)
                    if (config.debugPrintOn == "N"):
                        os.remove(os.path.join(config.labeled , expf))                    
                    os.rename(os.path.join(config.labeled , fn), os.path.join(config.trainPath , fn))
    config.logEnd("classes")


# # if no arg or -1 then just report
if len(sys.argv) == 1:
    sys.argv.append("-1")
        
if sys.argv[1] == "-h":
    print("USAGE: chkClasses [minCount] [trainPath]")
    print(" where 'minCount' is the minimum number of training images required to keep a class")
    print(" if 'minCount' is -1 or no args passed, only a report is performed on trainPath.")
    print(" 'minCount' is required if 'trainPath' is passed.")
    print(" if 'trainPath' is passed then it overrides the setting in config.py")
    print("\nif not in 'report only; mode does the following:")
    print("At start moves images in 'unlabeled' to 'labeled' folder")
    print("Creates new merged classes file with those not meeting 'minCount' removed")
    print("Creates class ID mapping table and saves a copy to classes.map.txt in 'labeled' folder")
    print("Images and maps that do not use the filtered classes are remapped to the new class IDs and moved to 'trainPath'")
    print("The unaltered classes.txt plus images and maps that do use the filtered classes are left in the labeled' folder in case needed later")
else:
    if len(sys.argv) > 2:
        config.trainPath = sys.argv[2]
    if not config.trainPath.endswith("train/"):
        config.trainPath = os.path.join(config.trainPath, "train/")
    
    if not os.path.exists(config.trainPath):
        raise ValueError(config.trainPath + " does not exist")

    doChk(int(sys.argv[1]))

