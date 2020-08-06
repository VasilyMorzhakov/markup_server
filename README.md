This is a markup server, which may be connected to an ML core.


Environmental variables:
   SECRET_KEY - random key
   MONGO_DB_ADDRESS - like mongodb:// ....  , that contain everything to connect
   MONGO_COLLECTION - just a name of the collection for this service
   AWS_KEY
   AWS_KEY_ID

Also, I couldn't find a way to put the site address-line to envs in confd_nginx.conf, so pay attention to YOUR_SITE before build docker.

To run the docker from Docker Hub, for example:

```
sudo docker system prune
sudo docker stop markup_server
sudo docker rm markup_server
echo "YOUR_DOCKER_HUB_PASSWORD" | sudo docker login -u "YOUR_DOCKER_HUB_PASS" --password-stdin
sudo docker pull "IMAGE_NAME"
sudo docker create --name markup_server -p 27017:27017 -p 443:443 \
            -e ....
            "IMAGE_NAME"
sudo docker cp rembrain_and_bundle.crt markup_server:/app/rembrain.crt
sudo docker cp rembrain.pem markup_server:/app/rembrain.pem
sudo docker start markup_server
```
