from app import app
from flask import render_template
from flask import send_from_directory, send_file
from flask import request
import json
import os
import shutil
import random
import logging

import boto3
s3 = boto3.resource('s3')
s3_client  = boto3.client('s3')

temp={}
temp['applications']=[]
temp['applications'].append('bus')
temp['applications'].append('one_rect')
temp['applications'].append('three_rect')
temp['applications'].append('one_point')


f=open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'config.json'),'r+')
config=json.load(f)
f.close()



@app.route('/')
def index():
    logging.info('Visited root')
    return "This is a markup service"


@app.route('/markup/<string:application>')
def markup(application):
    logging.info('Visited /markup/'+application)
    if application in config['applications']:
        width=config[application]['width']
        height=config[application]['height']
        return render_template(application+'.html',width=width,height=height)
    else:
        return "no such application"

@app.route('/<string:application>/images/<path:filename>')
def return_image(application,filename):
    logging.info('Returning image with application = {}, filename = {}'.format(application, filename))
    bucket_name = application + ".markup"
    file_key = "images/" + filename
    logging.info('Use bucket_name = {}, and file_key = {}'.format(bucket_name, file_key))
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    data = response['Body']
    return send_file(data, attachment_filename=filename)

@app.route('/<string:application>/get_random_pic_name')
def get_random_pic_name(application):
    bucket_name = application + ".markup"
    logging.info('Random pick with application = {}, bucket_name = {}'.format(application, bucket_name)) 
    #query all files and dirs
    #if error hapens, app crashes
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    elements = [c["Key"] for c in response['Contents']]
    print(elements)
    elements = [e for e in elements if e.startswith("images") and (e.endswith(".jpg") or e.endswith(".png"))]
    if len(elements) == 0:
        return None #"/"+application+"/images/fail"
    else:
        index=random.randint(0,len(elements)-1)
        logging.info('    return: ' + "/"+application+"/"+ elements[index])
        return "/"+application+"/"+ elements[index]


@app.route('/save/<string:application>',methods=['POST'])
def savePost(application):
    bucket_name = application + ".markup"
    logging.info('savePost, application = {}, bucket_name = {}'.format(application, bucket_name))
    if application in config['applications']:
        data = request.data

        dict=json.loads(data.decode())
        fn=dict['imageName']


        #recived markup
        image_path = dict['imageName'][len(application)+2:]

        if image_path.endwith('.jpg'):
            mark_path = image_path.replace("images", "processed").replace('.jpg','.json')
        else:
            if image_path.endwith('.png'):
                mark_path = image_path.replace("images", "processed").replace('.png', '.json')
            else:
                return "wrong file format"

        logging.info("Saving markup to " + mark_path)
        s3.Bucket(bucket_name).put_object(Key=mark_path, Body=data)
        #move image
        old_location = image_path
        new_location = image_path.replace("images", "processed")
        logging.info("Moving image from {} to {}".format(old_location, new_location))
        s3.Object(bucket_name, new_location).copy_from(CopySource=bucket_name+'/' + old_location)
        s3.Object(bucket_name, old_location).delete()

        return "ok"
    else:
        return "no such application"
