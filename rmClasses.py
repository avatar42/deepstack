import sys
import os
import numpy
import common

# # Note tested with Python 3.9 on Windows

# # Look at all the image maps and remove all the classes from classes.txt that are not used
def rmCls():
        
    common.logStart()

    orgClasses = common.readTextFile(common.trainPath + "classes.txt.old").splitlines()
    if len(orgClasses) == 0:
        raise ValueError(common.trainPath + "classes.txt.old does not exist!")
    
    common.dprint(orgClasses)

    newClasses = common.readTextFile(common.trainPath + "classes.txt").splitlines()
    common.dprint(newClasses)
    
    orgCnt = len(orgClasses)
    x = numpy.arange(orgCnt, dtype=int)
    idxMap = numpy.full_like(x, -2)  

    with open(common.trainPath + "classes.map.txt", "w") as fout:
        if fout.mode == "w":
            i = 0
            common.dprint("Creating mapping from classes.txt.old to classes.txt")
            for index in range(orgCnt):
                if orgClasses[index] in newClasses:
                    idxMap[index] = i
                    common.passed("Mapping:" + str(index) + ":" + orgClasses[index] + " wanted, to " + str(i) + ":" + newClasses[i])
                    fout.write("Mapping:" + str(index) + ":" + orgClasses[index] + " wanted, to " + str(i) + ":" + newClasses[i] + "\n")
                    i += 1
                else:
                    idxMap[index] = -1
                    common.warn("Unmapping:" + str(index) + ":" + orgClasses[index])
                    fout.write("Unmapping:" + str(index) + ":" + orgClasses[index] + "\n")
               
    imgNames = common.getImgNames(common.trainPath)
    for fn in imgNames:
        idx = fn.rfind('.')
        expf = fn[0:idx] + ".txt"
        if os.path.exists(common.trainPath + expf):
            data = common.readTextFile(common.trainPath + expf).splitlines()
            common.dprint(data)
            tags = []
            for line in data:
                idx = line.find(' ')
                c = int(line[0:idx])
                if (c > -1 and idxMap[c] > -1):
                    tags.append(str(idxMap[c]) + line[idx:])
                    
            common.dprint(tags)
            common.dprint("Backing up " + common.trainPath + expf + " to " + common.labeled + expf)
            os.rename(common.trainPath + expf, common.labeled + expf)
            # if no training objects left move image to labeled as well
            if len(tags) == 0:
                common.dprint("Moving unused " + common.trainPath + fn + " to " + common.labeled + fn)
                os.rename(common.trainPath + fn, common.labeled + fn)
            else:
                common.writeList(common.trainPath , expf, tags)
    
    common.logEnd("rmCls")


# # if no arg or -1 then just report
if len(sys.argv) == 1:
    sys.argv.append("-h")
        
if sys.argv[1] == "-h":
    print("USAGE: rmClasses [-h] trainPath")
    print("Creates class ID mapping table between classes.txt and classes.txt.old then saves a copy to classes.map.txt in 'trainPath' folder")
    print("Removes mappings from mapping files for classes not in classes.txt and removes mapping and image files if no training objects are left mapped.")
    print("Note since this updates files there is no backup option.")
else:
    if len(sys.argv) > 1:
        common.setPaths(sys.argv[1])

    rmCls()

