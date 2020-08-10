This is a markup server, which may be connected to an ML core.


Pay attention to YOUR_SITE before build docker - this should correspond to your site name.

You can build and run:

```
sudo docker build -t markup .

sudo docker create --name markup_server -p 27017:27017 -p 443:443 \
            -e ....
            markup:latest
sudo docker cp ssl_and_bundle.crt markup_server:/app/key.crt
sudo docker cp key.pem markup_server:/app/key.pem
sudo docker start markup_server
```

Environmental variables:
   - SECRET_KEY - random key
   - MONGO_DB_ADDRESS - like mongodb:// ....  , that contain everything to connect
   - MONGO_COLLECTION - just a name of the collection for this service
   - AWS_KEY
   - AWS_KEY_ID

You can exclude the SSL certificate by changing protocol in nginx config

Also, to debug, you can run <b>python3 main.py</b> from app folder.

To add a new user, run <b>add_user.sh role token</b> (role - "admin" or another, for example, "operator") and a token. Then, you can register a new user passing him the token and the following link: <b>your_site.com/register/role/token</b>.

All html templates are placed in the folder <b>templates</b> with corresponding names, described in config.json

<h3>Input data</h3>

There are two ways to upload new data to markup. 
1) Just choose files in "upload" on the site <b>your_site.com/markup/<application_name></b>
2) Or your can upload files through POST requests. ('/upload/<string:application>'). Using API you also can upload results from an ML machine throug '/upload_result/<application>' attaching 2 files: image + json. Then, you'll see pre-marked up images in b>your_site.com/markup/<application_name></b>
