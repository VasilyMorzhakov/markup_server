from app import app
from flask import render_template
from flask import send_from_directory, send_file
from flask import request
import json
import os
import shutil
import random
import logging
import time
import boto3
import botocore
from app import db
s3 = boto3.resource('s3')
s3_client  = boto3.client('s3')



f=open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'config.json'),'r+')
config=json.load(f)
f.close()



@app.route('/')
def index():
    logging.info('Visited root')
    return "This is a markup service"


@app.route('/upload/<string:application>',methods=['GET'])
def upload_get(application):
    logging.info('Visited get /upload/'+application)
    if application in config['applications']:
        return render_template('uploadfiles.html',application=application)
    else:
        return "no such application"

@app.route('/upload/<string:application>',methods=['POST'])
def upload_post(application):
    logging.info('Visited post /upload/'+application)
    
    if application in config['applications']:
      
        bucket_name = config[application]['bucket']
        files = request.files.getlist("files")
        for file in files:

            if '.jpg' in file.filename or '.png' in file.filename:

                db.put_file(application,config[application]['input'],file.filename)
                s3.Bucket(bucket_name).put_object(Key=config[application]['input']+'/'+file.filename, Body=file.read())

        return "ok"
    else:
        return "no such application"

@app.route('/upload_result/<string:application>',methods=['POST'])
def upload_result_post(application):
    logging.info('Visited post /upload_result/'+application)
    
    if application in config['applications']:
        bucket_name = config[application]['bucket']
        files = request.files.getlist("files")
        if len(files)==2 and ('.jpg' in files[0].filename or '.png' in files[0].filename) and ('.json' in files[1].filename):
            db.put_file(application,config[application]['input'],files[0].filename)
            s3.Bucket(bucket_name).put_object(Key=config[application]['input']+'/'+files[0].filename, Body=files[0].read())
            db.put_file(application,config[application]['input'],files[1].filename)
            s3.Bucket(bucket_name).put_object(Key=config[application]['input']+'/'+files[1].filename, Body=files[1].read())
        return "ok"
    else:
        return "no such application"



@app.route('/markup/<string:application>')
def markup(application):
    logging.info('Visited /markup/'+application)
    if application in config['applications']:
        width=config[application]['width']
        height=config[application]['height']
        return render_template(application+'.html',width=width,height=height,application=application)
    else:
        return "no such application"


@app.route('/<string:application>/images/<path:filename>')
def return_image(application,filename):
    if application in config['applications']:
        logging.info('Returning image with application = {}, filename = {}'.format(application, filename))
        bucket_name = config[application]['bucket']
        file_key = config[application]['input']+"/" + filename
        logging.info('Use bucket_name = {}, and file_key = {}'.format(bucket_name, file_key))
        try:
            response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        except botocore.exceptions.ClientError as e: 
            db.delete_file(application,config[application]['input'],filename)
            return None

        data = response['Body']
        return send_file(data, attachment_filename=filename)  
    else:
        return None

@app.route('/<string:application>/get_left_images')
def get_left_images(application):
    if application in config['applications']:
        folder=config[application]['input']
        files=db.get_files(application,folder)
        images=[e for e in files if (e['filename'].endswith('.jpg') or e['filename'].endswith('.png'))]
        return str(len(images))
    else:
        return None

@app.route('/<string:application>/get_config/<string:field>')
def get_config(application,field):
    if application in config['applications']:
        return json.dumps(config[application][field])
    return None


@app.route('/<string:application>/get_random_pic_name')
def get_random_pic_name(application):

    if application in config['applications']:
        start=time.time()
        folder=config[application]['input']
        files=db.get_files(application,folder)
        images=[e for e in files if (e['filename'].endswith('.jpg') or e['filename'].endswith('.png'))]
        index=random.randint(0,len(images)-1)
        res='/'+application+'/'+images[index]['folder']+'/'+images[index]['filename']
        #print('dt ',time.time()-start)
        return res
    else:
        return None

@app.route('/<string:application>/get_json/<string:folder>/<string:image_filename>')
def get_json(application,folder,image_filename):

    if application in config['applications']:
        start=time.time()
        bucket_name = config[application]['bucket']
        logging.info('get json, app  = {}, bucket_name = {}, filename={}'.format(application, bucket_name,image_filename)) 
        file_key=folder+'/'+image_filename.split('.')[0]+'.json'
        try:

            response=s3_client.get_object(Bucket=bucket_name, Key=file_key)
            str = response['Body'].read().decode('utf-8') 
            #print(time.time()-start)
            return str
        except botocore.exceptions.ClientError as e: 
            return '{}'
        return '{}'
    else:
        return '{}'



@app.route('/save/<string:application>',methods=['POST'])
def savePost(application):
    

    if application in config['applications']:
        bucket_name = config[application]['bucket']
        logging.info('savePost, application = {}, bucket_name = {}'.format(application, bucket_name))
        data = request.data

        dict=json.loads(data.decode())
        fn=dict['imageName']


        #recived markup
        image_path = dict['imageName'][len(application)+2:]
        if image_path.endswith('.jpg'):
            mark_path = image_path.replace('images', config[application]['output']).replace('.jpg','.json')
        else:
            if image_path.endswith('.png'):
                mark_path = image_path.replace('images', config[application]['output']).replace('.png', '.json')
            else:
                return "wrong file format"

        logging.info("Saving markup to " + mark_path)
        s3.Bucket(bucket_name).put_object(Key=mark_path, Body=data)
        db.put_file(application,config[application]['output'],os.path.basename(mark_path))

        #move image
        old_location = image_path
        new_location = image_path.replace(config[application]['input'], config[application]['output'])
        logging.info("Moving image from {} to {}".format(old_location, new_location))
        s3.Object(bucket_name, new_location).copy_from(CopySource=bucket_name+'/' + old_location)
        db.put_file(application,config[application]['output'],os.path.basename(new_location))

        s3.Object(bucket_name, old_location).delete()
        db.delete_file(application,config[application]['input'],os.path.basename(old_location))
        db.delete_file(application,config[application]['input'],os.path.basename(mark_path))


        return "ok"
    else:
        return "no such application"
