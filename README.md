# DeepStack utils.

## Run DeepStack pulling new image if needed.

**docker run -e VISION-FACE=True -e VISION-DETECTION=True -e VISION-SCENE=True -v localstorage:/datastore -e MODE=Medium -v /deepstack/mymodels:/modelstore/detection -v /deepstack/myfaces:/DeepStack/Faces --name DSfaces -p 82:5000 deepquestai/deepstack**


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

```
### Note tested with Python 2.7 on CentoOS Linux
### Where images to test with are located
imgPath = "./test.imgs/"
### Where to save debug images of from tests 
debugPath = "./debug.pics/"
### if Y saves debug images to compare between expected and found objects for mismatches.
saveDebugPics = "Y"
### Base URL of your DeepStack server
dsUrl = "http://localhost:82/"
### DeepStack started with -e MODE=Medium or -e MODE=High
mode = "Medium" 
# Test control flags. Set to N to skip test.
### Run face tests
doFace = "Y"
### Run scene detection tests
doScene = "Y"
### Run object detection tests
doObj = "Y"
### Run backup tests
doBackup = "Y"
### Run all pics in the imgPath thru enabled (see custom models) object detection tests and compare with a base run.
doExt = "Y"

# Custom models
### Run tests for [logo custom model](https://github.com/OlafenwaMoses/DeepStack_OpenLogo).
doLogo = "Y"
### Run tests for [licence-plate custom model](https://github.com/odd86/deepstack_licenceplate_model).
doPlate = "Y"
### Run tests for [dark custom model](https://github.com/OlafenwaMoses/DeepStack_ExDark).
doDark = "Y"
### Run tests for [actionnet custom model](https://github.com/OlafenwaMoses/DeepStack_ActionNET).
doAction = "Y"
### Run tests for trained model.
doTrained = "Y"
### Name of trained set model. Usually the same as the name of the pt file.
### RMRR is mine from the data in the checked in trainData folder. If you train your own replace the train folder in trainData with your own. 
trainedName = "RMRR" 
### new line used in the data files in trainData folder
ln = '\r\n'

### Output debug info Y,N
debugPrintOn = "N"

### Y=Fail on error, N=Just warn on error
failOnError = "Y"
```
# If you run all the tests you will see output like this

```
.
Ran 1 server up tests in 0:00:00.011784
.....................................
Ran 37 face tests in 0:00:02.868122
............
Ran 12 scene tests in 0:00:00.664204
............
Ran 12 detection tests in 0:00:00.864375
......
Ran 6 custom/openlogo tests in 0:00:00.398178
.....
Ran 5 custom/licence-plate tests in 0:00:00.217168
.......
..
Ran 9 custom/dark tests in 0:00:00.473751
...........................
Ran 27 custom/actionnetv2 tests in 0:00:03.784936
.
Ran 1 backup tests in 0:00:00.006947
..................................................
................................................................................
................................................................................
................................................................................
................................................................................
................................................................................
................................................................................
................................................................................
................................................................................
...........................................................................
Ran 765 detection tests in 0:00:50.983858
.....
................................................................................
................................................................................
................................................................................
................................................................................
................................................................................
................................................................................
................................................................................
.............................
Ran 594 custom/openlogo tests in 0:01:37.613067
...................................................
................................................................................
................................................................................
................................................................................
................................................................................
................................................................................
................................................................................
..........................................................
Ran 589 custom/licence-plate tests in 0:00:48.657136
......................
................................................................................
................................................................................
................................................................................
................................................................................
................................................................................
................................................................................
................................................................................
................................................................................
......................................................
Ran 716 custom/dark tests in 0:01:28.955852
..........................
................................................................................
................................................................................
................................................................................
................................................................................
................................................................................
................................................................................
................................................................................
...............................................
Ran 633 custom/actionnetv2 tests in 0:01:47.463614
...........
WARN:Of 1 expected ['raccoon'] found objects, found:2 objects [u'raccoon', u'raccoon']
....WARN:Of 1 expected ['raccoon'] found objects, found:3 objects [u'raccoon', u'raccoon', u'raccoon']
.
.........WARN:Of 1 expected ['raccoon'] found objects, found:3 objects [u'raccoon', u'raccoon', u'raccoon']
..
............................WARN:Of 1 expected ['raccoon'] found objects, found:2 objects [u'raccoon', u'raccoon']
.
.....
.WARN:Of 1 expected ['raccoon'] found objects, found:2 objects [u'raccoon', u'raccoon']
...................................................WARN:Of 1 expected ['raccoon'] found objects, found:2 objects [u'raccoon', u'raccoon']
.
.....................................................
.WARN:Of 1 expected ['raccoon'] found objects, found:5 objects [u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon']
....
.WARN:Of 1 expected ['raccoon'] found objects, found:9 objects [u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon']
..WARN:Of 1 expected ['raccoon'] found objects, found:8 objects [u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon']
..
.....
.WARN:Of 1 expected ['raccoon'] found objects, found:8 objects [u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon']
....
WARN:Of 1 expected ['raccoon'] found objects, found:5 objects [u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon']
...........WARN:Of 1 expected ['raccoon'] found objects, found:4 objects [u'raccoon', u'raccoon', u'raccoon', u'raccoon']

.....
.WARN:Of 1 expected ['raccoon'] found objects, found:6 objects [u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon']
...WARN:Of 1 expected ['raccoon'] found objects, found:6 objects [u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon']
.
.....
.WARN:Of 1 expected ['raccoon'] found objects, found:7 objects [u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon']
...WARN:Of 1 expected ['raccoon'] found objects, found:7 objects [u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon']
.
.....
.WARN:Of 1 expected ['raccoon'] found objects, found:6 objects [u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon']
....WARN:Of 1 expected ['raccoon'] found objects, found:5 objects [u'raccoon', u'raccoon', u'raccoon', u'raccoon', u'raccoon']

....WARN:Of 1 expected ['raccoon'] found objects, found:3 objects [u'raccoon', u'raccoon', u'raccoon']
.
.....WARN:Of 1 expected ['raccoon'] found objects, found:3 objects [u'raccoon', u'raccoon', u'raccoon']

.....
.WARN:Of 1 expected ['raccoon'] found objects, found:4 objects [u'raccoon', u'raccoon', u'raccoon', u'raccoon']
...WARN:Of 1 expected ['raccoon'] found objects, found:3 objects [u'raccoon', u'raccoon', u'raccoon']
.
...................
WARN:Missing label file trainData/train/DAH412_20210416_181551_6327541_3_0.txt, skipping 
..........WARN:Of 1 expected ['raccoon'] found objects, found:2 objects [u'raccoon', u'raccoon']

.....
WARN:Of 1 expected ['raccoon'] found objects, found:2 objects [u'raccoon', u'raccoon']
.....
.WARN:Of 1 expected ['raccoon'] found objects, found:2 objects [u'raccoon', u'raccoon']
....
.WARN:Of 1 expected ['raccoon'] found objects, found:3 objects [u'raccoon', u'raccoon', u'raccoon']
..........
.WARN:Of 1 expected ['raccoon'] found objects, found:2 objects [u'raccoon', u'raccoon']
....
.WARN:Of 1 expected ['raccoon'] found objects, found:2 objects [u'raccoon', u'raccoon']
..WARN:Of 1 expected ['raccoon'] found objects, found:3 objects [u'raccoon', u'raccoon', u'raccoon']
..
.....
WARN:Of 1 expected ['raccoon'] found objects, found:3 objects [u'raccoon', u'raccoon', u'raccoon']
...WARN:Of 1 expected ['raccoon'] found objects, found:3 objects [u'raccoon', u'raccoon', u'raccoon']
..
...............WARN:Of 1 expected ['raccoon'] found objects, found:4 objects [u'raccoon', u'raccoon', u'raccoon', u'raccoon']
..
.....
.WARN:Of 1 expected ['raccoon'] found objects, found:4 objects [u'raccoon', u'raccoon', u'raccoon', u'raccoon']
...WARN:Of 1 expected ['raccoon'] found objects, found:3 objects [u'raccoon', u'raccoon', u'raccoon']
.
.....
WARN:Of 1 expected ['raccoon'] found objects, found:2 objects [u'raccoon', u'raccoon']
...........................................................
.WARN:Of 1 expected ['raccoon'] found objects, found:2 objects [u'raccoon', u'raccoon']
...............................................................................
...........
Ran 541 RMRR tests in 0:00:46.476036
Check images in ./debug.pics/ match the object in the file name.
Files are named filename.item['label'].objectNumber.item['confidence'].jpg

Of 3948 tests
 Ran:3948
 Skipped:0
 Passed:3912
 Warnings:37
 Failed:0

```
Note the warnings are from raccoons in pics I did not mark for training.

# Utils
## startDeepStack.sh
=======
# Other Utils
## startDeepStack.sh


