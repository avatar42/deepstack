"""
Runs images passed against the models listed in tests2Run and generates a labeled copy for each with each model's labels in a diff color.
"""

import json
import os
import sys

from PIL import Image

from common import dprint, doPost, labelImg, warn, writeList, readTextFile, \
     readBinaryFile, getMapFileName
import config


class TestImg():

    def detect(self, color, testType, filePath, srcImg, mergeImg, classes):
        tags = []
        fileName = os.path.basename(filePath)
        dprint("Testing against " + testType + " with " + filePath + " in " + color)
        response = doPost(testType, files={"image":srcImg,"confidence": "0.20"})
        tidx = testType.rfind('/')
        if tidx > 0:
            testType = testType[tidx + 1:]
        dprint(response)
        if (len(response["predictions"]) > 0):
            with open(config.debugPath + fileName + "." + testType + ".json", "w") as f:
                if f.mode == "w":
                    s = json.dumps(response, indent=4)
                    dprint(s)
                    f.write(s)
    
        idx = fileName.rfind('.')
        outFile = config.debugPath + fileName[0:idx] + ".labeled" + fileName[idx:]
        w, h = mergeImg.size
        for item in response["predictions"]:
            y_max = int(item["y_max"])
            y_min = int(item["y_min"])
            x_max = int(item["x_max"])
            x_min = int(item["x_min"])
            # w, h = saveFound(item, testPath + f, None, config.debugPath + f)
            labelImg(outFile, mergeImg, item["label"] + ":" + testType, x_min, y_min, color , x_max, y_max)
            try:
                idx = classes.index(item["label"])
            except ValueError:
                warn(item["label"] + " not in " + config.trainPath + "classes.txt so adding")
                classes.append(item["label"])
                idx = classes.index(item["label"])

            x_center = (x_min + (x_max - x_min) / 2) / w   
            y_center = (y_min + (y_max - y_min) / 2) / h   
            x_width = (x_max - x_min) / w  
            y_height = (y_max - y_min) / h
            # Object ID    x_center    y_center    x_width    y_height
            tags.append(str(idx) + " " + str(round(x_center, 6)) + " " + str(round(y_center, 6)) + " " + str(round(x_width, 6)) + " " + str(round(y_height, 6)))
    
        if len(tags) > 0:
            expf = fileName[0:idx] + "." + testType + ".txt"
            # write tag file to labeled
            writeList(config.debugPath , expf, tags)
            mapName = getMapFileName("./", fileName)
            writeList(config.debugPath , mapName, tags, "a")  # append to master map
    
        return  outFile   

    def run(self, folder):
        if len(folder) < 2:
            print("USAGE: testImg imageFilePath [imageFilePath...]")
            return 
        
        # # colors = list(matplotlib.colors.cnames.keys())
        # from ['aliceblue', 'antiquewhite', 'aqua', 'aquamarine', 'azure', 'beige', 'bisque', 'black', 'blanchedalmond', 'blue', 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkgrey', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray', 'darkslategrey', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray', 'dimgrey', 'dodgerblue', 'firebrick', 'floralwhite', 'forestgreen', 'fuchsia', 'gainsboro', 'ghostwhite', 'gold', 'goldenrod', 'gray', 'green', 'greenyellow', 'grey', 'honeydew', 'hotpink', 'indianred', 'indigo', 'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan', 'lightgoldenrodyellow', 'lightgray', 'lightgreen', 'lightgrey', 'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightslategrey', 'lightsteelblue', 'lightyellow', 'lime', 'limegreen', 'linen', 'magenta', 'maroon', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'navy', 'oldlace', 'olive', 'olivedrab', 'orange', 'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'purple', 'rebeccapurple', 'red', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'silver', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'snow', 'springgreen', 'steelblue', 'tan', 'teal', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'white', 'whitesmoke', 'yellow', 'yellowgreen']
        colors = ['white', 'black', 'blue', 'brown', 'coral', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkgrey', 'darkmagenta', 'darkorange', 'darkred', 'dimgray', 'dimgrey', 'gold', 'goldenrod', 'gray', 'green', 'greenyellow', 'grey', 'indigo', 'magenta', 'maroon', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'navy', 'oldlace', 'olive', 'olivedrab', 'orange', 'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'purple', 'rebeccapurple', 'red', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'silver', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'snow', 'springgreen', 'steelblue', 'tan', 'teal', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'white', 'whitesmoke', 'yellow', 'yellowgreen']
        dprint(colors)
#        config.trainPath = "../RMRR.model/train/"
        classes = readTextFile(config.trainPath + "classes.txt").splitlines()
        dprint("Read:" + config.trainPath + "classes.txt")
        dprint(classes)
         
        i = 1
        # # try to avoid adjacent colors when using full matplotlib.colors.cnames.keys
        cstep = 1
        while i < len(folder):
            fileName = folder[i]
            mergeImg = Image.open(fileName).convert("RGB")
            srcImg = readBinaryFile(fileName)
            dprint("Checking:" + fileName)
            c = 0
        # # check popular models    
            for testType in config.tests2Run: 
                outFile = self.detect(colors[c], testType, fileName, srcImg, mergeImg, classes)
                c += cstep
            i += 1    
                    
            print ("marked up file written to " + outFile)

        writeList(config.debugPath , "classes.txt", classes)

#########################################################


TestImg().run(sys.argv)
