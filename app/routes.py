from app import app
from flask import render_template
from flask import send_from_directory
from flask import request
import json
import os
import shutil
import random

USE_AWS = True

if USE_AWS:
    import boto3
    bucket_name="bus.markup"
    s3 = boto3.resource('s3')

temp={}
temp['applications']=[]
temp['applications'].append('bus')
temp['applications'].append('one_rect')
temp['applications'].append('three_rect')
temp['applications'].append('one_point')


f=open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'config.json'),'r+')
config=json.load(f)
f.close()


width=600
height=600

@app.route('/')
def index():
    return "This is a markup service"


@app.route('/markup/<string:application>')
def markup(application):
    if application in config['applications']:
        return render_template(application+'.html',width=width,height=height)
    else:
        return "no such application"

@app.route('/<string:application>/images/<path:filename>')
def return_image(application,filename):

    return send_from_directory(os.path.join(os.path.dirname(os.path.realpath(__file__)),'data',application,'images'),filename)

@app.route('/<string:application>/get_random_pic_name')
def get_random_pic_name(application):

    dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),'data',application,'images')
    if os.path.exists(dir):
        files=os.listdir(dir)
        if len(files)==0:
            return "/"+application+"/images/fail"
        else:
            index=random.randint(0,len(files)-1)
            return "/"+application+'/images/'+files[index]
    else:
        return "None"


@app.route('/save/<string:application>',methods=['POST'])
def savePost(application):

    if application in config['applications']:
        data = request.data

        dict=json.loads(data.decode())
        fn=dict['imageName']
        fn_json=fn.replace('.jpg','.json')
        directory=os.path.dirname(os.path.realpath(__file__))

        f=open(directory+'/data'+fn_json,'wb')
        f.write(data)
        f.close()

        image_path = directory+'/data'+fn
        mark_path = directory+'/data'+fn_json
        image_path_new = image_path.replace('images/','processed/')
        mark_path_new = mark_path.replace('images/','processed/')
        #move to processed
        shutil.move(image_path, image_path_new)
        shutil.move(mark_path, mark_path_new)
        
        if USE_AWS:
            with open(mark_path_new) as data:
                s3.Bucket(bucket_name).put_object(Key=mark_path_new, Body=data)
            with open(image_path_new) as data:
                s3.Bucket(bucket_name).put_object(Key=image_path_new, Body=data)

        return "ok"
    else:
        return "no such application"
