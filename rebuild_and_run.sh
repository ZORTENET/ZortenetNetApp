#docker stop mynetapp
#docker rm mynetapp
#docker rmi netapp:latest
#docker build --tag netapp .
#docker run -d -p 5000:5000 --name mynetapp  netapp

docker-compose down
docker-compose up
docker network connect nef_emulator_default mynetapp