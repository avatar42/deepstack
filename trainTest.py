import os
import numpy
import config

# # Note tested with Python 2.7 on CentoOS Linux and 3.9 on Windows
clsCnts = []


# # run tests for the trained custom model
def trainTests():
    
    config.logStart()
    classes = config.readTextFile(config.trainPath + "classes.txt").splitlines()
    config.dprint(classes)
    clsCnt = len(classes)
    clsCnts = numpy.zeros(clsCnt)
    expCnts = numpy.zeros(clsCnt)
    confSum = numpy.zeros(clsCnt)

    imgNames = config.getImgNames(config.trainPath)

    with open(config.trainPath + "trainTest.results.txt", "w") as fout:
        if fout.mode == "w":
            for f in imgNames:
                config.dprint("Checking:" + config.trainPath + f)
                idx = f.rfind('.')
                expf = f[0:idx] + ".txt"
                if os.path.exists(config.trainPath + expf):
                    config.dprint("against:" + config.trainPath + expf)      
                    data = config.readTextFile(config.trainPath + expf).splitlines()
                    config.dprint(data)
                    expected = []
                    for line in data:
                        idx = line.find(' ')
                        c = int(line[0:idx])
                        expected.append(classes[c])
                        expCnts[c] += 1
        
                    config.dprint(expected)
            
                    config.dprint("Testing " + config.trainedName + "-" + config.trainPath + f)
                    response = config.doPost("custom/" + config.trainedName, files={"image":config.readBinaryFile(config.trainPath + f)})
                    foundItems = []
                    tags = []
                    i = 0
                    for item in response["predictions"]:
                        foundItems.insert(i, item["label"])
                        index = classes.index(item["label"])
                        clsCnts[index] += 1
                        confSum[index] += float(item["confidence"])
                        i += 1
                        
                    config.dprint(foundItems)
                
                    config.warnTrue("Of " + str(len(expected)) + " expected " + str(expected) + " found objects, found:" + str(len(foundItems)) 
                             +" objects " + str(foundItems), len(foundItems) == len(expected))
                    diff = len(foundItems) - len(expected)
                    # check what we expect is there. Note other things might be found but here we only care about the expected
                    for item in expected:
                        config.assertTrue(item + " in test image:" + f, item in foundItems)
                        # remove in case we are checking for more than one of a type
                        if item in foundItems:
                            foundItems.remove(item)
                            
                    # save debug info for mismatched objects found.        
                    if diff != 0:
                        i = 0
                        foundItems = []
                        for item in response["predictions"]:
                            foundItems.insert(i, item["label"])
                            w, h = config.saveFound(item, config.trainPath + f, config.debugPath + f + "." + item["label"] + "." + str(i) + "." + str(item["confidence"]) + ".jpg")
                            y_max = int(item["y_max"])
                            y_min = int(item["y_min"])
                            x_max = int(item["x_max"])
                            x_min = int(item["x_min"])
                            x_center = (x_min + (x_max - x_min) / 2) / w   
                            y_center = (y_min + (y_max - y_min) / 2) / h   
                            x_width = (x_max - x_min) / w  
                            y_height = (y_max - y_min) / h
                            # Object ID    x_center    y_center    x_width    y_height
                            tags.append(str(idx) + " " + str(round(x_center, 6)) + " " + str(round(y_center, 6)) + " " + str(round(x_width, 6)) + " " + str(round(y_height, 6)))
                            i += 1
        
                        fout.write("Of " + str(len(expected)) + " expected " + str(expected) + " objects, found:" + str(len(foundItems)) 
                            +" objects " + str(foundItems) + " in " + f + "\n")
                        idx = f.rfind('.')
                        expf = f[0:idx] + "." + str(diff) + ".txt"
                        # write tag file to labeled
                        config.writeList(config.debugPath , expf, tags)

                    # save info for expected objects not found         
                    if diff < 0:
                        for line in data:
                            idx = line.find(' ')
                            c = int(line[0:idx])
                            if not classes[c] in foundItems:
                                config.saveExpected(line[idx:], config.trainPath + f, config.debugPath + f + "." + classes[c] + ".expected.jpg")
        
                else:
                    config.warn("Missing label file " + config.trainPath + expf + ", skipping ")
        
            print("")
            for index in range(clsCnt):
                avg = "0"
                try:
                    if clsCnts[index] > 0:
                        avg = str(confSum[index] / clsCnts[index])
                except RuntimeError as err:
                    config.warn("RuntimeError: {0}".format(err))
                except OSError as err:
                    config.warn("OS error: {0}".format(err))
                except ValueError:
                    config.warn("Could not convert data to a float.") 
                                       
                print(classes[index] + " found " + str(clsCnts[index]) + " of " + str(expCnts[index]) + " expected times with an average confidence of " + avg)
                fout.write(classes[index] + " found " + str(clsCnts[index]) + " of " + str(expCnts[index]) + " expected times with an average confidence of " + avg + "\n")
            fout.write("\n")
            fout.write("Of " + str(config.testsRan + config.testsSkipped) + " tests\n")
            fout.write(" Ran:" + str(config.testsRan) + "\n")
            fout.write(" Skipped:" + str(config.testsSkipped) + "\n")
            fout.write(" Passed:" + str(config.testsPassed) + "\n")
            fout.write(" Warnings:" + str(config.testsWarned) + "\n")
            fout.write(" Failed:" + str(config.testsFailed) + "\n")
            print("")
            print("Of " + str(config.testsRan + config.testsSkipped) + " tests")
            print(" Ran:" + str(config.testsRan))
            print(" Skipped:" + str(config.testsSkipped))
            print(" Passed:" + str(config.testsPassed))
            print(" Warnings:" + str(config.testsWarned))
            print(" Failed:" + str(config.testsFailed))

    config.logEnd(config.trainedName)
    print("Check images in " + config.debugPath + " match the object in the file name.")
    print("Files are named filename.item['label'].objectNumber.item['confidence'].jpg")
    
    
#########################################################
# ## The test suite #####################################
#########################################################
config.serverUpTest()
config.clearDebugPics()    
trainTests() 

