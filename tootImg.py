"""
Posts the latest flagged picture in the Alerts folder to you Mastodon account.
"""

import os
import sys
import glob
import re
import time
from toot import console, User, App, http, config
from PIL import Image

from common import doPost, labelImg, writeList, readBinaryFile, readTextFile, getMapFileName, dprint

class TootImg():

    debugPath = "debug.pics/"

    def detect(self, color, testtype, filePath, srcImg, mergeImg, classes):
        filename = os.path.basename(filePath)
        dprint("Checking " + filePath + " with " + testtype)

        ## Send to DeepStack
        response = doPost(testtype, files={"image":srcImg,"confidence": "0.70"})
        tidx = testtype.rfind('/')
        if tidx > 0:
            testtype = testtype[tidx + 1:]

        ## Nothing found
        if (len(response["predictions"]) == 0):
            return None
    
        idx = filename.rfind('.')
        description = "At the feeders:"

        outfile = self.debugPath + filename[0:idx] + ".labeled" + filename[idx:]
        dprint(outfile)
        ## Double check we have not done this one and the stamp changed or something else weird happened.
        if os.path.exists(outfile):
            print("Already posted:"+ outfile + "=" + time.strftime('%d %b %Y %H:%M:%S', time.localtime(os.path.getmtime(outfile))))
            return None
        dprint("Filtering")
##mouse,bird,cat,horse,sheep,cow,elephant,bear,zebra,giraffe,pig,raccoon,coyote,squirrel,bunny,cat_black,cat_grey,cat_orange,cat_tort,cat_calico,cow,deer,opossum
        ## See if there is a non dog critter in the pic    
        for item in response["predictions"]:
            try:
                idx = classes.index(item["label"])
            except ValueError:
                dprint("Filtering out:" + str(item["label"]))
                return None

            if "cat" in item["label"]:
                description  = description + " #cat"
           
            ## generate labled pic
            y_max = int(item["y_max"])
            y_min = int(item["y_min"])
            x_max = int(item["x_max"])
            x_min = int(item["x_min"])
            labelImg(outfile, mergeImg, item["label"] + ":" + testtype, x_min, y_min, color , x_max, y_max)

            # Object ID    x_center    y_center    x_width    y_height
            description  = description + " #" + str(item["label"]) + " " + str(round(float(item["confidence"]) * 100, 2)) + "%"    
    
        ## Send result to Mastodon
        args = []
        args.append("--debug")
        args.append("--verbose")
        args.append("-d")
        args.append(description)
        args.append("-m")
        args.append(outfile)
        args.append(description)
        print("Sending description:"+ description)
        user, app = config.get_active_user_app()
        console.run_command(app, user, 'post', args)
        
        ## return file to let caller know we found a goof one.
        return  outfile   

    def run(self, args):
        if len(args) < 2:
            print("USAGE: tootImg imageFolderExp")
            print(" imageFolderExp like E:\BlueIris\Alerts\HV420*.jpg")
            return 
        
        dprint(args[1])
        classes = readTextFile("classes.txt").splitlines()
        dprint("Read:./classes.txt")
        dprint(classes)
               
        list_of_files = glob.glob(args[1])
        try:
            list_of_files.sort(key=os.path.getmtime)
        except Exception as inst:
            print("Sort failed, doing slow way:"+inst)
            
        dprint(os.stat(self.debugPath))
        lastrun=os.path.getmtime(self.debugPath)
        print("Looking for images newer than "+ time.strftime('%d %b %Y %H:%M:%S', time.localtime(lastrun)))
        for filename in list_of_files:
            try:
                if os.path.getmtime(filename) > lastrun:
                    dprint(filename)
                    dprint(os.stat(filename))
                    mergeimg = Image.open(filename).convert("RGB")
                    srcimg = readBinaryFile(filename)
                    outfile = self.detect('cyan', "custom/RMRR", filename, srcimg, mergeimg,classes)
                    if outfile:         
                        print ("marked up file written to " + outfile)
                        return

            except Exception as inst:
                print(inst)
#########################################################


TootImg().run(sys.argv)
