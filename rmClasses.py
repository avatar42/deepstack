import sys
import os
import numpy
import config

# # Note tested with Python 3.9 on Windows


# # Look at all the image maps and remove all the classes from classes.txt that are not used more than minCnt times
def rmCls(minCnt):
        
    config.logStart()

    orgClasses = config.readTextFile(config.trainPath + "classes.txt.old").splitlines()
    if len(orgClasses) == 0:
        raise ValueError(config.trainPath + "classes.txt.old does not exist!")
    
    config.dprint(orgClasses)

    newClasses = config.readTextFile(config.trainPath + "classes.txt").splitlines()
    config.dprint(newClasses)
    
    orgCnt = len(orgClasses)
    x = numpy.arange(orgCnt, dtype=int)
    idxMap = numpy.full_like(x, -2)
    
    imgNames = config.getImgNames(config.trainPath)

    with open(config.trainPath + "classes.map.txt", "w") as fout:
        if fout.mode == "w":
            i = 0
            config.dprint("Creating mapping from classes.txt.old to classes.txt")
            for index in range(orgCnt):
                if orgClasses[index] in newClasses:
                    idxMap[index] = i
                    config.passed("Mapping:" + str(index) + ":" + orgClasses[index] + " wanted, to " + str(i) + ":" + newClasses[i])
                    fout.write("Mapping:" + str(index) + ":" + orgClasses[index] + " wanted, to " + str(i) + ":" + newClasses[i] + "\n")
                    i += 1
                else:
                    idxMap[index] = -1
                    config.warn("Unmapping:" + str(index) + ":" + orgClasses[index])
                    fout.write("Unmapping:" + str(index) + ":" + orgClasses[index] + "\n")
               
    for fn in imgNames:
        idx = fn.rfind('.')
        expf = fn[0:idx] + ".txt"
        if os.path.exists(config.trainPath + expf):
            data = config.readTextFile(config.trainPath + expf).splitlines()
            config.dprint(data)
            tags = []
            for line in data:
                idx = line.find(' ')
                c = int(line[0:idx])
                if (c > -1 and idxMap[c] > -1):
                    tags.append(str(idxMap[c]) + line[idx:])
                    
            config.dprint(tags)
            config.dprint("Backing up " + config.trainPath + expf + " to " + config.labeled + expf)
            os.rename(config.trainPath + expf, config.labeled + expf)
            # if no training objects left move image to labeled as well
            if len(tags) == 0:
                config.dprint("Moving unused " + config.trainPath + fn + " to " + config.labeled + fn)
                os.rename(config.trainPath + fn, config.labeled + fn)
            else:
                config.writeList(config.trainPath , expf, tags)
    
    config.logEnd("rmCls")


# # if no arg or -1 then just report
if len(sys.argv) == 1:
    sys.argv.append("-1")
        
config.dprint ('Number of arguments:' + str(len(sys.argv)) + 'arguments.')
config.dprint ('Argument List:' + str(sys.argv))

if sys.argv[1] == "-h":
    print("USAGE: rmClasses ")
    print("Creates class ID mapping table between classes.txt and classes.txt.old then saves a copy to classes.map.txt in 'trainPath' folder")
    print("Removes mappings from mapping files for classes not in classes.txt and removes mapping and image files if not training objects are left mapped.")
    print("Note since this updates files there is no backup option.")
else:
    rmCls(int(sys.argv[1]))

