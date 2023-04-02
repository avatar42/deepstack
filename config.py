# # import for all vars

# Configuration options and common methods for DeepStack utils
"""Base URL of your DeepStack server
note trailing / on folder names"""
dsUrl = "http://10.10.2.197:82/"
# dsUrl = "http://192.168.2.197:82/"
"""DeepStack started with -e MODE=Medium or -e MODE=High"""
mode = "Medium" 
"""Where images to test with are located"""
imgPath = "test.imgs/"
"""Where to save debug images of from tests """
debugPath = "debug.pics/"
"""path to labeled training pics. (may be overwritten by some command line options)"""
trainPath = "train/"
"""path to labeled training pics. (may be overwritten by some command line options)"""
testPath = "test/"
"""path to labeled training pics. (may be overwritten by some command line options)"""
validPath = "valid/"
"""unlabeled / new file folder"""
# newPicPath = "D:/odrive/GD.video/cams/DeepStackWS/data/new/"
newPicPath = "new/"
"""Name of trained set model. Usually the same as the name of the pt file.
RMRR is mine from the data in the checked in trainData folder. If you train your own replace the train folder in trainData with your own. 
(may be overwritten by some command line options)"""
trainedName = "RMRR" 
# trainedName = "fire"  
"""folder where images with found objects and their mapping files are put by quickLabel and read by chkClasses"""
labeled = "labeled/"
"""folder where images with not found objects are put by quickLabel and read by chkClasses"""
unlabeled = "unlabeled/"
"""where LabelImg in installed /cloned relative to my deepstack repo"""
labelImgData = "../labelImg/data"
"""Number of columns to wrap progress dots at"""
maxProgressCnt = 256
"""Output debug info Y,N Note if Y also causes a copy instead of a move of some files"""
debugPrintOn = "Y"
"""if Y saves debug images to compare between expected and found objects for mismatches."""
saveDebugPics = "Y"
"""Y=Fail on error, N=Just warn on error"""
failOnError = "Y"
""" min confidence to use for model tests"""
min_confidence = 0.50
# Supported images suffixes to look for in folders"""
includedExts = ['jpg', 'webp', 'bmp', 'png', 'gif']

"""installed models to use to find objects
detection the built in model
[openlogo custom model](https://github.com/OlafenwaMoses/DeepStack_OpenLogo).
[licence-plate custom model](https://github.com/odd86/deepstack_licenceplate_model).
[dark custom model](https://github.com/OlafenwaMoses/DeepStack_ExDark).
[actionnetv2 custom model](https://github.com/OlafenwaMoses/DeepStack_ActionNET).
[RMRR my general custom model](https://github.com/avatar42/RMRR.model).
[RMRR my bird custom model](https://github.com/avatar42/RMRR.birds).
[RMRR my fire custom model](https://github.com/avatar42/RMRR.fire).
"""
# tests2Run = ["custom/"+trainedName] 
tests2Run = ["detection", "custom/openlogo", "custom/licence-plate", "custom/dark", "custom/actionnetv2", "custom/RMRR", "custom/birds", "custom/fire"] 

