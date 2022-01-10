# DeepStack utils.

Note I have moved the training data and sample model to [its own repo](https://github.com/avatar42/RMRR.model) to keep this one from becoming too large as I expand the model.

## Run DeepStack with Docker pulling new image if needed.
### Linux
**docker run -e VISION-FACE=True -e VISION-DETECTION=True -e VISION-SCENE=True -v localstorage:/datastore -e MODE=Medium -v /deepstack/mymodels:/modelstore/detection -v /deepstack/myfaces:/DeepStack/Faces --name DSfaces -p 82:5000 deepquestai/deepstack**
###Windows
**docker run -e VISION-FACE=True -e VISION-DETECTION=True -e VISION-SCENE=True -v localstorage:/datastore -e MODE=Medium -v C:\DeepStack\MyModels:/modelstore/detection -v C:\DeepStack/myfaces:/DeepStack/Faces -p 82:5000 deepquestai/deepstack**

Options are:
Option       | Means  
------------- |-------------
**-e VISION-FACE=True** | Do face detection
**-e VISION-DETECTION=True** | Do object detection
**-e VISION-SCENE=True** | Do scene detection
**-e MODE=Medium** | Mode to run in. Same as Blue Iris options (High/Medium/Low)
**-v /deepstack/mymodels:/modelstore/detection** | Where custom models are. Note maps local path outside of Docker **/deepstack/mymodels** to container path **/modelstore/detection**
**-v /deepstack/myfaces:/DeepStack/Faces** | Where known faces images are. Note maps local path outside of Docker
**-v localstorage:/datastore** | This specifies the local volume where DeepStack will store all temp data. Note maps local path in user space outside of Docker
**--name DSfaces** | Name to use to interact with image. Random name is assigned if not given. Note will fail it image with that name already exists on your system.
**-p 82:5000** | External port:internal one. Internal is always 5000 and 82 is assumed external port by BI.
**deepquestai/deepstack** | Name of cloud image to use.
**--gpus all deepquestai/deepstack:gpu** | If using the gpu version you will want to use.

## Windows local
**deepstack --VISION-FACE True --VISION-DETECTION True --VISION-SCENE True --MODE Medium --MODELSTORE-DETECTION "c:/DeepStack/MyModels" -PORT 82**
get install from [here](https://docs.deepstack.cc/index.html#installation-guide-for-cpu-version) and put all the custom models in c:\DeepStack\MyModels

# Unit tests
A quick Python 2.7 test to make sure your setup is working. Including the 4 custom models in the [DeepStack documentation](https://docs.deepstack.cc/custom-models-samples/index.html). **Note their online documentation has a lot of errors in it.**

Edit vars at top of fullTest.py for the server info and the tests you want to run. (See below) Then run with

**python fullTest.py**

It will exit with a message if/when an issue is found.

## Last tested on setup

DeepStack: Version 2021.09.01

v1/vision/custom/actionnetv2

v1/vision/custom/dark
 
v1/vision/custom/licence-plate

v1/vision/custom/openlogo

/v1/vision/face

/v1/vision/face/recognize

/v1/vision/face/register

/v1/vision/face/match

/v1/vision/face/list

/v1/vision/face/delete (not tested yet)

/v1/vision/detection

/v1/vision/scene

/v1/backup

/v1/restore (not tested yet)

# For further help/info [see this debug guide](https://securitycam101.rmrr42.com/2021/10/quick-blue-iris-with-deepstack-debug.html)


# Set these values as needed / to match your setup.
## Configuration options for DeepStack utils in config.py

```
# # Base URL of your DeepStack server
dsUrl = "http://localhost:82/"
# # DeepStack started with -e MODE=Medium or -e MODE=High
mode = "Medium" 
# # Where images to test with are located
imgPath = "test.imgs/"
# # Where to save debug images of from tests 
debugPath = "debug.pics/"
# # path to labeled training pics.
trainPath = "../RMRR.model/train/"
# # unlabeled / new file folder
newPicPath = "new/"
# # Name of trained set model. Usually the same as the name of the pt file.
# # RMRR is mine from the data in the checked in trainData folder. If you train your own replace the train folder in trainData with your own. 
trainedName = "RMRR" 
# # folder where images with found objects and their mapping files are put by quickLabel and read by chkClasses
labeled = "labeled/"
# # folder where images with not found objects are put by quickLabel and read by chkClasses
unlabeled = "unlabeled/"

# # Output debug info Y,N
debugPrintOn = "N"
# # if Y saves debug images to compare between expected and found objects for mismatches.
saveDebugPics = "Y"
# # Y=Fail on error, N=Just warn on error
failOnError = "Y"

# Supported images suffixes to look for in folders
includedExts = ['jpg', 'webp', 'bmp', 'png', 'gif']

# # installed models to use to find objects
# # detection the built in model
# # [openlogo custom model](https://github.com/OlafenwaMoses/DeepStack_OpenLogo).
# # [licence-plate custom model](https://github.com/odd86/deepstack_licenceplate_model).
# # [dark custom model](https://github.com/OlafenwaMoses/DeepStack_ExDark).
# # [actionnetv2 custom model](https://github.com/OlafenwaMoses/DeepStack_ActionNET).
tests2Run = ["detection", "custom/openlogo", "custom/licence-plate", "custom/dark", "custom/actionnetv2"] 
```
## in fullTest.py you can turn off some test if wanted
```
# Test control flags. Set to N to skip test.
# # Run face tests
doFace = "Y"
# # Run scene detection tests
doScene = "Y"
# # Run object detection tests
doObj = "Y"
# # Run backup tests
doBackup = "Y"
# # Run all pics in the config.imgPath thru enabled (see custom models) object detection tests and compare with a base run.
doExt = "Y"
```
# If you run all the tests you will see output like this

```
.
Ran 1 server up tests in 0:00:00.008001
.....................................
Ran 37 face tests in 0:00:02.019431
....................
Ran 20 scene tests in 0:00:00.987697
............
Ran 12 detection tests in 0:00:00.256550
.
Ran 1 backup tests in 0:00:00.014000
......
Ran 6 custom/openlogo tests in 0:00:00.304561
...
..
Ran 5 custom/licence-plate tests in 0:00:00.166108
.........
Ran 9 custom/dark tests in 0:00:00.289784
...........................
Ran 27 custom/actionnetv2 tests in 0:00:01.406866
..........................................
................................................................................
.............................
Ran 151 detection tests in 0:00:04.017401
...................................................
..................................................
Ran 101 custom/openlogo tests in 0:00:08.087629
..............................
......................................................................
Ran 100 custom/licence-plate tests in 0:00:04.009132
..........
................................................................................
...............................................
Ran 137 custom/dark tests in 0:00:07.948979
.................................
................................................................................
.....
Ran 118 custom/actionnetv2 tests in 0:00:08.022125

Of 725 tests
 Ran:725
 Skipped:0
 Passed:725
 Warnings:0
 Failed:0

```

# Other Utils
## startDeepStack.sh
shell script for starting DeepStack with params needed for running tests.
## updateDeepStack.sh
shell script for upfating then starting DeepStack with params needed for running tests. 
## testTorch.bat and testTorch.py
test that Torch setup is working and using your GPU ready to train.
## localColab.bat
bat file to bring up my Jupyter Notebook for training with local GPU.
## quickLabel.py
Runs pics in **newPicPath** against all the installed object detect models to generate tag files similar to what the **Label.exe** would produce along with a list of all found objects (classes.txt).

# My custom model
**RMRR.pt** is the model I created from the trainData data.

**RMRR_classes.txt** are the object types trained for.



