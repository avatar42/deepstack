# DeepStack
DeepStack utils.

Run DeepStack pulling new image if needed.

**docker run -e VISION-FACE=True -e VISION-DETECTION=True -e MODE=Medium -v /deepstack/mymodels:/modelstore/detection -v /deepstack/myfaces:/DeepStack/Faces --name DSfaces -p 82:5000 deepquestai/deepstack**

Options are:

Do face detection
**-e VISION-FACE=True **

Do object detection
**-e VISION-DETECTION=True **

Mode to run in. Same as Blue Iris options
**-e MODE=Medium**

Where custom models are. Note maps local path outside of Docker **/deepstack/mymodels** to container path **/modelstore/detection **
**-v /deepstack/mymodels:/modelstore/detection **

Where known faces images are. Note maps local path outside of Docker
**-v /deepstack/myfaces:/DeepStack/Faces **

This specifies the local volume where DeepStack will store all data. Note maps local path outside of Docker
**-v /deepstack/datastore:/datastore **

Name to use to interact with image. Random name is assigned if not given. Note will fail it image with that name already exists on your system.
**--name DSfaces **

External port:internal one. Internal is always 5000 and 82 is assumed external port by BI.
**-p 82:5000 **

Name of cloud image to use.
**deepquestai/deepstack**

If using the gpu version you will want to use.
**--gpus all deepquestai/deepstack:gpu**

#Unit tests
Edit fullTest.py for the server info and the tests you want to run. Then run with

**python fullTest.py**

It will exit with a message when an issue is found.

For further help [see this debug guide](https://securitycam101.rmrr42.com/2021/10/quick-blue-iris-with-deepstack-debug.html)