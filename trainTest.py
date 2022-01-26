import os
import sys
import numpy
import config
from PIL import Image

# # Note tested with Python 2.7 on CentoOS Linux and 3.9 on Windows
clsCnts = []
classes = []
clsCntTotal = 0
expCntTotal = 0


# # run tests for the trained custom model
def trainTests(testPath):
    global clsCntTotal
    global expCntTotal
    
    config.dprint("Checking " + testPath)
    clsCnt = len(classes)
    clsCnts = numpy.zeros(clsCnt)
    expCnts = numpy.zeros(clsCnt)
    confSum = numpy.zeros(clsCnt)
    confmin = numpy.ones((clsCnt,), dtype=float)
    confmax = numpy.zeros(clsCnt)
    
    imgNames = config.getImgNames(testPath)

    with open(testPath + "trainTest.results.txt", "w") as fout:
        if fout.mode == "w":

            for f in imgNames:
                config.imgCnt += 1
                config.dprint("Checking:" + testPath + f)
                idx = f.rfind('.')
                expf = f[0:idx] + ".txt"
                if os.path.exists(testPath + expf):
                    config.dprint("against:" + testPath + expf)      
                    data = config.readTextFile(testPath + expf).splitlines()
                    config.dprint(data)
                    expected = []
                    
                    for line in data:
                        idx = line.find(' ')
                        c = int(line[0:idx])
                        expected.append(classes[c])
                        expCnts[c] += 1
        
                    config.dprint(expected)
            
                    config.dprint("Testing " + config.trainedName + "-" + testPath + f)

                    response = config.doPost("custom/" + config.trainedName, files={"image":config.readBinaryFile(testPath + f)}, data={"min_confidence":str(config.min_confidence)})
                    foundItems = []
                    tags = []
                    i = 0
                    for item in response["predictions"]:
                        foundItems.insert(i, item["label"])
                        try:
                            index = classes.index(item["label"])
                        except ValueError:
                            # found object know to model but not in train set so add tracking
                            classes.append(item["label"])
                            index = classes.index(item["label"])
                            clsCnts = numpy.append(clsCnts, 0)
                            expCnts = numpy.append(expCnts, 0)
                            confSum = numpy.append(confSum, 0.0)
                            confmin = numpy.append(confmin, 1.0)
                            confmax = numpy.append(confmax, 0.0)
                            
                        clsCnts[index] += 1
                        confidence = float(item["confidence"])
                        confSum[index] += confidence
                        if (confmin[index] > confidence):
                            confmin[index] = confidence
                        if (confmax[index] < confidence):
                            confmax[index] = confidence
                        i += 1
                        config.appendDebugList(item["label"], f, confidence)
                        
                    config.dprint(foundItems)
                    
                    if len(foundItems) == 0:
                        config.appendDebugList("EMPTY", f, 0)

                    diff = len(foundItems) - len(expected)
                    # check what we expect is there. Note other things might be found but here we only care about the expected
                    for item in expected:
                        config.assertTrue("Expected object " + item + " not found in test image:" + f, item in foundItems)
                        # remove in case we are checking for more than one of a type
                        if item in foundItems:
                            foundItems.remove(item)
                        else:
                            print(foundItems)
                    matches = diff == 0 and len(foundItems) == 0
                            
                    # save debug info for mismatched objects found.        
                    if not matches:
                        i = 0
                        foundItems = []
                        mergeImg = Image.open(testPath + f).convert("RGB")
                        w, h = mergeImg.size
                        for item in response["predictions"]:
                            foundItems.insert(i, item["label"])
                            y_max = int(item["y_max"])
                            y_min = int(item["y_min"])
                            x_max = int(item["x_max"])
                            x_min = int(item["x_min"])
                            # w, h = config.saveFound(item, testPath + f, None, config.debugPath + f)
                            config.labelImg(config.debugPath + f, mergeImg, item["label"] + ":" + str(i), x_min, y_min, "green", x_max, y_max)
                            x_center = (x_min + (x_max - x_min) / 2) / w   
                            y_center = (y_min + (y_max - y_min) / 2) / h   
                            x_width = (x_max - x_min) / w  
                            y_height = (y_max - y_min) / h
                            idx = classes.index(item["label"])
                            # Object ID    x_center    y_center    x_width    y_height
                            tags.append(str(idx) + " " + str(round(x_center, 6)) + " " + str(round(y_center, 6)) + " " + str(round(x_width, 6)) + " " + str(round(y_height, 6)))
                            i += 1
        
                        msg = "Of " + str(len(expected)) + " expected " + str(expected) + " found objects, found:" + str(len(foundItems)) + " objects " + str(foundItems) + " in " + f
                        if (len(foundItems) > len(expected)):
                            config.warn(msg)
                        fout.write(msg + "\n")
                        idx = f.rfind('.')
                        expf = f[0:idx] + ".txt"
                        # write tag file to labeled
                        config.writeList(config.debugPath , expf, tags)

                    # save info for expected objects not found         
                        i = 0
                        for line in data:
                            idx = line.find(' ')
                            c = int(line[0:idx])
                            # config.saveExpected(line[idx:], testPath + f, None, config.debugPath + f, classes[c]+"-"+str(i))
                            # Object ID    x_center    y_center    x_width    y_height
                            xy = line[idx:].split()
                            x_center = float(xy[0]) * w
                            y_center = float(xy[1]) * h
                            x_width = float(xy[2]) * w
                            y_height = float(xy[3]) * h
                            y_max = int(y_center + y_height / 2)
                            y_min = int(y_center - y_height / 2)
                            x_max = int(x_center + x_width / 2)
                            x_min = int(x_center - x_width / 2)
                            config.labelImg(config.debugPath + f, mergeImg, classes[c] + "-" + str(i), x_min, y_min, "red", x_max, y_max)
                            i += 1

                        # config.labelImg(config.debugPath + f, mergeImg, ",".join(expected), 0, 0, "red")   
                        # config.labelImg(config.debugPath + f, mergeImg, ",".join(foundItems), 0, 20, "green")   
                else:
                    config.warn("Missing label file " + testPath + expf + ", skipping ")
        
            if len(imgNames) > 0:
                print("")
                print("For images in:" + testPath + " with min_confidence set to " + "{:.02%}".format(config.min_confidence))
                fout.write("For images in:" + testPath + " with min_confidence set to " + str(config.min_confidence) + "\n")
                for index in range(clsCnt):
                    avg = "0"
                    adjavg = "0"
                    try:
                        if clsCnts[index] > 0:
                            avg = "{:.02%}".format(confSum[index] / clsCnts[index])
                        if expCnts[index] > 0:
                            adjavg = "{:.02%}".format(confSum[index] / expCnts[index])
                    except RuntimeError as err:
                        config.warn("RuntimeError: {0}".format(err))
                    except OSError as err:
                        config.warn("OS error: {0}".format(err))
                    except ValueError:
                        config.warn("Could not convert data to a float.") 
    
                    clsCntTotal += clsCnts[index]
                    expCntTotal += expCnts[index]
                    msg = classes[index] + " found " + str(clsCnts[index]) + " of " + str(expCnts[index]) + " expected objects with an average confidence of " + avg + " min:" + "{:.02%}".format(confmin[index]) + " max:" + "{:.02%}".format(confmax[index]) + " adjusted avg:" + adjavg                                      
                    print(msg)
                    fout.write(msg)
            fout.write("\n")
            fout.write("Of " + str(config.testsRan + config.testsSkipped) + " tests\n")
            fout.write(" Ran:" + str(config.testsRan) + "\n")
            fout.write(" Skipped:" + str(config.testsSkipped) + "\n")
            fout.write(" Passed:" + str(config.testsPassed) + "\n")
            fout.write(" Warnings:" + str(config.testsWarned) + "\n")
            fout.write(" Failed:" + str(config.testsFailed) + "\n")
    

#########################################################
# ## The test suite #####################################
#########################################################
if len(sys.argv) > 1:
    config.trainedName = sys.argv[1]
if len(sys.argv) > 2:
    config.trainPath = sys.argv[2]

if not config.trainPath.endswith("train/"):
    config.trainPath = os.path.join(config.trainPath, "train/")

if not os.path.exists(config.trainPath):
    raise ValueError(config.trainPath + " does not exist")

config.serverUpTest()
config.clearDebugPics()    
config.logStart()
classes = config.readTextFile(config.trainPath + "classes.txt").splitlines()
config.dprint("Read:" + config.trainPath + "classes.txt")
config.dprint(classes)
# # to help with debug and tweaking of maps
config.saveLabels2labelImgData(classes)

trainTests(config.trainPath) 

config.trainPath = config.trainPath.replace("train/", "test/")
if os.path.exists(config.trainPath):
    trainTests(config.trainPath)
else:
    print(config.trainPath + " does not exist, skipped") 

config.trainPath = config.trainPath.replace("test/", "valid/")
if os.path.exists(config.trainPath):
    trainTests(config.trainPath)
else:
    print(config.trainPath + " does not exist, skipped") 

print("Found " + str(clsCntTotal) + " of " + str(expCntTotal) + " expected objects in " + str(config.imgCnt) + " image files")
print("")
print("Of " + str(config.testsRan + config.testsSkipped) + " tests")
print(" Ran:" + str(config.testsRan))
print(" Skipped:" + str(config.testsSkipped))
print(" Passed:" + str(config.testsPassed))
print(" Warnings:" + str(config.testsWarned))
print(" Failed:" + str(config.testsFailed))

config.logEnd("trainTest")
print("Check images in " + config.debugPath + " match the object in the file name.")
print("Image files that did not match are marked up with found in green and expected in red")
print("Matching map files matching the found data are saved to " + config.debugPath + " as well")
print("Lastly image name and confidence list files are created for each")
print(" object class and 'EMPTY' (no objects in image) named [object class].lst.txt")

