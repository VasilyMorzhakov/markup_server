import pymongo
import sys
import os
import time

##Create a MongoDB client, open a connection to Amazon DocumentDB as a replica set and specify the read preference as secondary preferred
line='mongodb+srv://morzhakov:'+os.environ['MONGO_DB_PASSWORD']+'@markup-0yjwh.mongodb.net/test?retryWrites=true&w=majority'
client = pymongo.MongoClient(line) 

def get_files(application,folder):
    cursor=client[application].files.find({"folder":folder})
    res=[]
    for document in cursor:
        res.append(document)
    return res

def put_file(application,folder,file):
    client[application].files.insert_one({'folder':folder,'filename':file})


if __name__=='__main__':
    cars = []
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
	
    client.close()