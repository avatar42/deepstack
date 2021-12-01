if [ -z "`docker ps -a | grep DSfaces`" ]
then
        docker run -e VISION-FACE=True -e VISION-DETECTION=True -e VISION-SCENE=True -v localstorage:/datastore -e MODE=Medium -v /deepstack/mymodels:/modelstore/detection -v /deepstack/myfaces:/DeepStack/Faces --name DSfaces -p 82:5000 deepquestai/deepstack
else
        docker start DSfaces
        docker logs -f DSfaces
fi
