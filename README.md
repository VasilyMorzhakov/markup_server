This is a markup server, which may be connected to an ML core.


Environmental variables:
   SECRET_KEY - random key
   MONGO_DB_ADDRESS - like mongodb:// ....  , that contain everything to connect
   MONGO_COLLECTION - just a name of the collection for this service
   AWS_KEY
   AWS_KEY_ID

Pay attention to YOUR_SITE before build docker - this should correspond to your site name.

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
sudo docker cp ssl_and_bundle.crt markup_server:/app/key.crt
sudo docker cp key.pem markup_server:/app/key.pem
sudo docker start markup_server
```

You can exclude the SSL certificate by changing protocol in nginx config

Also, to debug, you can run <b>python3 main.py</b> from app folder.

To add a new user, run <b>add_user.sh role token</b> (role - "admin" or another, for example, "operator") and a token. Then, you can register a new user passing him the token and the following link: <b>your_site.com/register/role/token</b>.

All html templates are placed in the folder <b>templates</b> with corresponding names, described in config.json
