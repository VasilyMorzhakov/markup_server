import pymongo
import sys
import os
import time
from passlib.hash import sha256_crypt
from datetime import datetime
import boto3
import json
import random

##Create a MongoDB client, open a connection to Amazon DocumentDB as a replica set and specify the read preference as secondary preferred
line=os.environ['MONGO_DB_ADDRESS']
collection=os.environ['MONGO_COLLECTION']

client = pymongo.MongoClient(line) 

def get_random_file(application,folder,user_id=None,date=None,exts=None):
    filter={'folder':folder}
    if not user_id is None:
        filter['user_id']=user_id
    if not date is None:
        filter['date']=date
    if not exts is None:
        dicts=[]
        for j in range(len(exts)):
            dicts.append({'filename':{'$regex':'.*'+exts[j]+'.*'}})
        filter['$or']=dicts

    count = client[application].files.find(filter).count()
    if count==0:
        return None
    index= random.randint(0,count-1)
    return client[application].files.find(filter)[index]

def get_files_count(application,folder,user_id=None,date=None,exts=None):
    filter={'folder':folder}
    if not user_id is None:
        filter['user_id']=user_id
    if not date is None:
        filter['date']=date
    if not exts is None:
        dicts=[]
        for j in range(len(exts)):
            dicts.append({'filename':{'$regex':'.*'+exts[j]+'.*'}})
        filter['$or']=dicts
    count = client[application].files.find(filter).count()
    return count
       

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
    client[collection].pre_users.delete_one({'role':role,'token':token})

def add_pre_user(role,token):
    if not client[collection].pre_users.find_one({'role':role,'token':token}):
        client[collection].pre_users.insert_one({'role':role,'token':token})

def check_pre_user(role,token):
    if client[collection].pre_users.find_one({'role':role,'token':token}):
        return True
    else:
        return False

def add_user(name,email,password,role):
    hash=sha256_crypt.hash(password)
    if not client[collection].users.find_one({'name':name}):
        client[collection].users.insert_one({'name':name,'email':email,'hash':hash,'role':role})
    return

def is_user_by_name(name):
    if client[collection].users.find_one({'name':name}):
        return True
    return False

def is_user_by_email(email):
    if client[collection].users.find_one({'email':email}):
        return True
    return False

def check_password(email,password):
    user=client[collection].users.find_one({'email':email})
    if user is None:
        return False
    return sha256_crypt.verify(password,user['hash'])
    
def get_all_users():
    users=client[collection].users.find({})
    names=[]
    ids=[]
    for user in users:
        names.append(user['name'])
        ids.append(user['email'])
    return names,ids
def get_user(email):
    return client[collection].users.find_one({'email':email})