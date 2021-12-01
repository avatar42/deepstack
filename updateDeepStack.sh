id=`docker ps | grep 5000 | cut -f3 -d'>' | awk '{print $2}'`
docker stop $id
docker system prune --all --volumes --force
docker pull deepquestai/deepstack:latest
sleep 1
docker ps -a
./startDeepStack.sh
