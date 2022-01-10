import os
import sys
import numpy
import config

# # Note tested with Python 3.9 on Windows
clsCnt = []


def cntUsed(folder):
    global clsCnt

    imgNames = config.getImgNames(folder)

    for fn in imgNames:
        idx = fn.rfind('.')
        expf = fn[0:idx] + ".txt"
        if os.path.exists(folder + expf):
            data = config.readTextFile(folder + expf).splitlines()
            config.dprint(data)
            for line in data:
                idx = line.find(' ')
                c = int(line[0:idx])
                if c > -1:
                    clsCnt[c] += 1
            config.testsRan += 1 
        else:
            config.skipped("Missing label file " + folder + expf + ", skipping ", 1)
    
    return imgNames


# # Look at all the image maps and remove all the classes from classes.txt that are not used more than minCnt times
def doChk(minCnt):
    global clsCnt
        
    config.logStart()

    orgClasses = config.readTextFile(config.trainPath + "classes.txt").splitlines()
    config.dprint(orgClasses)

    newClasses = config.readTextFile(config.labeled + "classes.txt").splitlines()
    config.dprint(newClasses)
    
    newCnt = len(newClasses)
    clsCnt = numpy.zeros(newCnt)
    x = numpy.arange(newCnt, dtype=int)
    idxMap = numpy.full_like(x, 1)
    
    imgNames = config.getImgNames(config.unlabeled)
    for fn in imgNames:
        os.rename(config.unlabeled + fn, config.labeled + fn)

    imgNames = cntUsed(config.trainPath)
    imgNames = cntUsed(config.labeled)

    if minCnt == -1:
        for index in range(newCnt):
            print(str(index) + ":" + newClasses[index] + " used " + str(clsCnt[index]) + " times.")
    else:
        with open(config.labeled + "classes.map.txt", "w") as fout:
            if fout.mode == "w":
                clsOut = []
                i = 0
                config.dprint("Removing classes with less than " + str(minCnt) + " training images")
                for index in range(newCnt):
                    if clsCnt[index] >= minCnt:
                        idxMap[index] = i
                        clsOut.append(newClasses[index])
                        config.passed("Mapping:" + str(index) + ":" + newClasses[index] + " used " + str(clsCnt[index]) + " times to " + str(i) + ":" + clsOut[i])
                        fout.write("Mapping:" + str(index) + ":" + newClasses[index] + " used " + str(clsCnt[index]) + " times to " + str(i) + ":" + clsOut[i] + "\n")
                        i += 1
                    else:
                        idxMap[index] = -1
                        config.warn("Tossing:" + str(index) + ":" + newClasses[index] + " used " + str(clsCnt[index]) + " times")
         
        config.writeList(config.trainPath , "classes.txt", clsOut)
  
        print("\nKept " + str(config.testsPassed) + " classes and tossed " + str(config.testsWarned))
        
        for fn in imgNames:
            idx = fn.rfind('.')
            expf = fn[0:idx] + ".txt"
            if os.path.exists(config.labeled + expf):
                data = config.readTextFile(config.labeled + expf).splitlines()
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
                    os.rename(config.labeled + fn, config.trainPath + fn)
                    os.remove(config.labeled + expf)                    
    config.logEnd("doChk")


# # if no arg or -1 then just report
if len(sys.argv) == 1:
    sys.argv.append("-1")
        
config.dprint ('Number of arguments:' + str(len(sys.argv)) + 'arguments.')
config.dprint ('Argument List:' + str(sys.argv))

if sys.argv[1] == "-h":
    print("USAGE: chkClasses [minCount]")
    print(" where 'minCount' is the minimum number of training images required to keep a class")
    print(" if 'minCount' is -1 or omitted only a report is performed.")
    print("\nif not in report only mode does the following")
    print("At start moves images in 'unlabeled' to 'labeled' folder")
    print("Creates new classes file with those not meeting 'minCount' removed")
    print("Creates class ID mapping table and saves a copy to classes.map.txt in 'labeled' folder")
    print("Images and maps that do not use the unfiltered classes are remapped to the new class IDs and moved to 'trainPath'")
    print("The unaltered classes.txt plus images and maps that do use the unfiltered classes are left in the labeled' folder in case needed later")
else:
    doChk(int(sys.argv[1]))

