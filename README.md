This is a markup server, which may be connected to an ML core.

run ./start.sh to start the service in a debug mode without nginx. 




User management:

  Linux:

  There is a script app/add_user_default.sh, rename it to add_user.sh locally and change default password to actual one.
  Make it executable by chmod.

  To add a new user:
      cd app
      ./add_user.sh  {{role}} {{token}}
      
  roles are two roles: admin, marking

  Windows:
  
  add environmental variable - MONGO_DB_PASSWORD 
  
  cd app
  python3 add_user.py {{role}} {{token}}

  the token may be generated or choosen randomly

  then, you'll be able to register a new user: http://server_address/register/{{role}}/{{token}}
 
