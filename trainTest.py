import os
import sys

from PIL import Image
import numpy

from common import logStart, logEnd, dprint, setPaths, showConfig, readTextFile, getImgNames, writeList, \
    warn, doPost, readBinaryFile, appendDebugList, assertTrue, labelImg, \
    serverUpTest, clearDebugPics, saveLabels2labelImgData, showTestReport
import config

"""Runs all the training images against the model to see where weakness are to help in adjusting image maps and or removing classes and or images that reduce accuracy.
Note tested with Python 3.9 on Windows"""


class TrainTests():
    clsCnts = []
    classes = []
    clsCntTotal = 0
    expCntTotal = 0

    # # run tests for the trained custom model
    def trainTests(self, testPath):
        global classes
        global clsCnts
        imgCnt = 0
        
        if not os.path.exists(config.trainPath):
            print(config.trainPath + " does not exist, skipped")
            return 
    
        dprint("Checking " + testPath)
        clsCnt = len(classes)
        clsCnts = numpy.zeros(clsCnt)
        expCnts = numpy.zeros(clsCnt)
        confSum = numpy.zeros(clsCnt)
        confmin = numpy.ones((clsCnt,), dtype=float)
        confmax = numpy.zeros(clsCnt)
        
        imgNames = getImgNames(testPath)
    
        with open(testPath + "trainTest.results.txt", "w") as fout:
            if fout.mode == "w":
    
                for f in imgNames:
                    imgCnt += 1
                    dprint("Checking:" + testPath + f)
                    idx = f.rfind('.')
                    expf = f[0:idx] + ".txt"
                    if os.path.exists(testPath + expf):
                        dprint("against:" + testPath + expf)      
                        data = readTextFile(testPath + expf).splitlines()
                        dprint(data)
                        expected = []
                        
                        for line in data:
                            idx = line.find(' ')
                            try:
                                c = int(line[0:idx])
                                expected.append(classes[c])
                                expCnts[c] += 1
                            except ValueError:
                                warn("Could not process line:" + line + " in:" + data + " in file:" + f)
                            except IndexError:
                                warn("Do not have a class ID:" + str(c))
                                if not "Bad ID" in classes:
                                    classes.append("Bad ID")
                                    
                                c = classes.index("Bad ID")
                                expected.append(classes[c])
                                expCnts[c] += 1
                                                            
                        dprint(expected)
                
                        dprint("Testing " + config.trainedName + "-" + testPath + f)
    
                        response = doPost("custom/" + config.trainedName, files={"image":readBinaryFile(testPath + f)}, data={"min_confidence":str(config.min_confidence)})
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
                            appendDebugList(item["label"], f, confidence)
                            
                        dprint(foundItems)
                        
                        if len(foundItems) == 0:
                            appendDebugList("EMPTY", f, 0)
    
                        diff = len(foundItems) - len(expected)
                        # check what we expect is there. Note other things might be found but here we only care about the expected
                        for item in expected:
                            assertTrue("Expected object " + item + " not found in test image:" + f, item in foundItems)
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
                                # w, h = saveFound(item, testPath + f, None, config.debugPath + f)
                                labelImg(config.debugPath + f, mergeImg, item["label"] + ":" + str(i), x_min, y_min, "green", x_max, y_max)
                                x_center = (x_min + (x_max - x_min) / 2) / w   
                                y_center = (y_min + (y_max - y_min) / 2) / h   
                                x_width = (x_max - x_min) / w  
                                y_height = (y_max - y_min) / h
                                idx = classes.index(item["label"])
                                # Object ID    x_center    y_center    x_width    y_height
                                tags.append(str(idx) + " " + str(round(x_center, 6)) + " " + str(round(y_center, 6)) + " " + str(round(x_width, 6)) + " " + str(round(y_height, 6)))
                                i += 1
            
                            msg = "Of " + str(len(expected)) + " expected " + str(expected) + " found objects, found:" + str(len(foundItems)) + " objects " + str(foundItems) + " in " + f
                            ind = "-"
                            if (len(foundItems) > len(expected)):
                                warn(msg)
                                ind = "+"
                            fout.write(ind + msg + "\n")
                            idx = f.rfind('.')
                            expf = f[0:idx] + ".txt"
                            # write tag file to labeled
                            writeList(config.debugPath , expf, tags)
    
                        # save info for expected objects not found         
                            i = 0
                            for line in data:
                                idx = line.find(' ')
                                c = int(line[0:idx])
                                # saveExpected(line[idx:], testPath + f, None, config.debugPath + f, classes[c]+"-"+str(i))
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
                                labelImg(config.debugPath + f, mergeImg, classes[c] + "-" + str(i), x_min, y_min, "red", x_max, y_max)
                                i += 1
    
                            # labelImg(config.debugPath + f, mergeImg, ",".join(expected), 0, 0, "red")   
                            # labelImg(config.debugPath + f, mergeImg, ",".join(foundItems), 0, 20, "green")   
                    else:
                        msg = "Missing label file " + testPath + expf + ", skipping "
                        warn(msg)
                        fout.write(msg + "\n")
            
                if len(imgNames) > 0:
                    print("")
                    msg = "For images in:" + testPath + " with min_confidence set to " + "{:.02%}".format(config.min_confidence)
                    print(msg)
                    fout.write(msg + "\n")
                    for index in range(clsCnt):
                        avg = "0"
                        adjavg = "0"
                        try:
                            if clsCnts[index] > 0:
                                avg = "{:.02%}".format(confSum[index] / clsCnts[index])
                            if expCnts[index] > 0:
                                adjavg = "{:.02%}".format(confSum[index] / expCnts[index])
                        except RuntimeError as err:
                            warn("RuntimeError: {0}".format(err))
                        except OSError as err:
                            warn("OS error: {0}".format(err))
                        except ValueError:
                            warn("Could not convert data to a float.") 
        
                        self.clsCntTotal += clsCnts[index]
                        self.expCntTotal += expCnts[index]
                        msg = classes[index] + " found " + str(clsCnts[index]) + " of " + str(expCnts[index]) + " expected objects with an average confidence of " + avg + " min:" + "{:.02%}".format(confmin[index]) + " max:" + "{:.02%}".format(confmax[index]) + " adjusted avg:" + adjavg                                      
                        print(msg)
                        fout.write(msg + "\n")
                showTestReport(fout)
        return imgCnt

    def run(self):
        global classes
        
        serverUpTest()
        clearDebugPics()    
        logStart()
        classes = readTextFile(config.trainPath + "classes.txt").splitlines()
        dprint("Read:" + config.trainPath + "classes.txt")
        dprint(classes)
        # # to help with debug and tweaking of maps
        saveLabels2labelImgData(classes)
        
        imgCnt = 0
        imgCnt += self.trainTests(config.trainPath)
        imgCnt += self.trainTests(config.testPath)
        imgCnt += self.trainTests(config.validPath)
        
        print("Found " + str(self.clsCntTotal) + " of " + str(self.expCntTotal) + " expected objects in " + str(imgCnt) + " image folder")
        showTestReport()
        
        logEnd("trainTest")
        print("Check images in " + config.debugPath + " match the object in the file name.")
        print("Image folder that did not match are marked up with found in green and expected in red")
        print("Matching map folder matching the found data are saved to " + config.debugPath + " as well")
        print("Lastly image name and confidence list folder are created for each")
        print(" object class and 'EMPTY' (no objects in image) named [object class].lst.txt")


#########################################################
if len(sys.argv) > 1:
    if sys.argv[1] == "-h":
        print("USAGE: " + sys.argv[0] + " [-h] [trainedName] [trainPath]")
        print("-h prints this help")
        print("if 'trainedName' and or 'trainPath' are not passed then the values in config.py are used")
        print("if trainPath is passed, /train is appended if not there then updates testPath to 'trainPath'../test, validPath to 'trainPath'../valid, labeled to 'trainPath'../labeled, unlabeled to 'trainPath'../unlabeled and debugPath to 'trainPath'../debug.pics")
        print("Runs all the images in trainPath, testPath and validPath against the model (trainedName) to see where weakness are to help in adjusting image maps and or removing classes and or images that reduce accuracy.")
        print("Creates images in " + config.debugPath + " match the object in the file name.")
        print("Image files that did not match are marked up with found in green and expected in red")
        print("Matching map files matching the found data are saved to " + config.debugPath + " as well")
        print("Lastly image name and confidence list files are created for each")
        print(" object class and 'EMPTY' (no objects in image) named [object class].lst.txt")
        os._exit(1)
    else:
        config.trainedName = sys.argv[1]
        if len(sys.argv) > 2:
            setPaths(sys.argv[2])
        else:
            showConfig()

TrainTests().run()
