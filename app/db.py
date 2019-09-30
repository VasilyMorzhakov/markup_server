import pymongo
import sys
import os
import time
from passlib.hash import sha256_crypt
from datetime import datetime
import boto3
import json

##Create a MongoDB client, open a connection to Amazon DocumentDB as a replica set and specify the read preference as secondary preferred
#line='mongodb+srv://morzhakov:'+os.environ['MONGO_DB_PASSWORD']+'@markup-0yjwh.mongodb.net/test?retryWrites=true&w=majority'

line='mongodb+srv://morzhakov:VA1425846@markup-0yjwh.mongodb.net/test?retryWrites=true&w=majority'

client = pymongo.MongoClient(line) 

def get_files(application,folder,user_id=None,ext=None,date=None):
    filter={'folder':folder}
    if not user_id is None:
       filter["user_id"]=user_id
    if not date is None:
       filter['date']=date

    cursor=client[application].files.find(filter)
    res=[]
    for document in cursor:

        if not ext is None:
            
            if ext in document['filename']:
                res.append(document)
        else:
            res.append(document)
    return res


def delete_file(application,folder,file):
    client[application].files.delete_one({'folder':folder,'filename':file})

def put_file(application,folder,file,user_id=None):
    date=datetime.today().strftime("%d-%m-%Y")
    if not user_id is None:
        client[application].files.insert_one({'folder':folder,'filename':file,'user_id':user_id,'date':date})
    else:
        client[application].files.insert_one({'folder':folder,'filename':file,'date':date})

def del_pre_user(role,token):
    client['adminka'].pre_users.delete_one({'role':role,'token':token})

def add_pre_user(role,token):
    if not client['adminka'].pre_users.find_one({'role':role,'token':token}):
        client['adminka'].pre_users.insert_one({'role':role,'token':token})

def check_pre_user(role,token):
    if client['adminka'].pre_users.find_one({'role':role,'token':token}):
        return True
    else:
        return False

def add_user(name,email,password,role):
    hash=sha256_crypt.hash(password)
    if not client['adminka'].users.find_one({'name':name}):
        client['adminka'].users.insert_one({'name':name,'email':email,'hash':hash,'role':role})
    return

def is_user_by_name(name):
    if client['adminka'].users.find_one({'name':name}):
        return True
    return False

def is_user_by_email(email):
    if client['adminka'].users.find_one({'email':email}):
        return True
    return False

def check_password(email,password):
    user=client['adminka'].users.find_one({'email':email})
    if user is None:
        return False
    return sha256_crypt.verify(password,user['hash'])
    
def get_all_users():
    users=client['adminka'].users.find({})
    names=[]
    ids=[]
    for user in users:
        names.append(user['name'])
        ids.append(user['email'])
    return names,ids
def get_user(email):
    return client['adminka'].users.find_one({'email':email})
    

if __name__=='__main__':
    files=get_files('heads','images',user_id=None)
    print(len(files))
    

    f=open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'config.json'),'r+')
    config=json.load(f)
    f.close()

    s3 = boto3.resource('s3')
    s3_client  = boto3.client('s3')

    bucket_name = config['heads']['bucket']
    
  
    for i in range(len(files)):
        print(i)
        delete_file('heads','images',files[i]['filename'])
        s3.Object(bucket_name,'images'+'/'+files[i]['filename']).delete()
        

    '''add_pre_user('Vasyutka','letscallittoken')
    print(check_pre_user('Vasyutka','letscallittoken'))'''

    '''cars = []
    for i in range(2000):
        cars.append({'id':i})

    db=client.cars
    db.items.drop()
    

    db.items.insert_many(cars)
    cursor = db.items.find({})

    start=time.time()    
    res=[]
    for document in cursor:
          res.append(document)
    print(time.time()-start,' len: ',len(res))
	
    client.close()'''
