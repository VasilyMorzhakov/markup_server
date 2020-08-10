This is a markup server, which may be connected to an ML core.


You can run it by a docker with nginx as a web-server.
To start you will need a MONGODB and an S3 bucket, where all input and result annotation are stored.

Pay attention to YOUR_SITE in <b>confd_nginx.conf</b> before building a docker image - this should correspond to your site name.

To build and run:

```
sudo docker build -t markup .

sudo docker create --name markup_server -p 27017:27017 -p 443:443 \
            -e ....
            markup:latest
sudo docker cp ssl_and_bundle.crt markup_server:/app/ssl.crt
sudo docker cp key.pem markup_server:/app/ssl.pem
sudo docker start markup_server
```

Environmental variables:
   - SECRET_KEY - random key for FLASK
   - MONGO_DB_ADDRESS - like mongodb:// ....  , that contain everything to connect
   - MONGO_COLLECTION - just a name of the collection for this service
   - AWS_KEY
   - AWS_KEY_ID

You can exclude the SSL certificate by changing protocol in nginx config (change 443 port to 80 and remove lines about ssl certificates).


To add a new user, run <b>add_user.sh role token</b> and a token. Then, you can register a new user passing him the token and the following link: <b>your_site.com/register/role/token</b>.

Or, being an admin, you can add user through the address line: /add_pre_user/role/token (token is a random key-digit sequence)

Possible roles for users:
  - admin
  - operator

All html templates are placed in the folder <b>templates</b> with corresponding names, described in config.json

<h3>Input data</h3>

There are two ways to upload new data to markup. 
1) Just choose files in "upload" on the site <b>your_site.com/markup/<application_name></b>
2) Or your can upload files through POST requests. ('/upload/<string:application>'). Using API you also can upload results from an ML machine throug '/upload_result/<application>' attaching 2 files: image + json. Then, you'll see pre-marked up images in b>your_site.com/markup/<application_name></b>

<h3>Debug</h3>

Also, to debug, you can run <b>python3 main.py</b> from app folder.

You'll also need two more env variables DEBUG_ADMIN_EMAIL and DEBUG_ADMIN_PASSWORD to create a new admin user without running <b>add_user.sh</b> script.
