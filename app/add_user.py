import db
import sys

if len(sys.argv)==3:
    print('role: ',sys.argv[1])
    print('token: ',sys.argv[2])
    db.add_pre_user(sys.argv[1],sys.argv[2])
    print('pre user was added')
