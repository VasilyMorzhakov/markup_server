from flask import render_template
from flask import send_from_directory, send_file,url_for,redirect
from flask import request
import json
import logging
from flask_login import login_user, logout_user, current_user, login_required,LoginManager,UserMixin
from flask import Blueprint,session
from app import db
import os
import boto3
import botocore


s3 = boto3.resource('s3')
s3_client  = boto3.client('s3')


review_api = Blueprint('review_api', __name__)

f=open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'config.json'),'r+')
config=json.load(f)
f.close()


@review_api.route('/review/<string:application>', methods=['GET','POST'])
@login_required
def review_get(application):
    logging.info('Visited review')
    user=db.get_user(current_user.id)
    if user['role']!='admin':
        return 'You should be an admin'

    names,ids=db.get_all_users()
    ids.insert(0,'all users')

    if request.method == 'POST':
        session['user_to_review']=request.form['select_user']

    files=[]
    if session.get('user_to_review') is not None:
        cur_user=session['user_to_review']
        if not cur_user == 'all users':
            files_=db.get_files(application,config[application]['output'],cur_user)
        else:
            files_=db.get_files(application,config[application]['output'],ext='.json')

        for i in range(len(files_)):
            files.append(files_[i]['filename'])

    else:
        cur_user='user to review was not chosen'

    
    return render_template('review_choose_user.html',users=ids,application=application,cur_user=cur_user,files=files,output=config[application]['output'],log_in_or_out='out')

@review_api.route('/review/del_sample/<string:application>/<string:folder>/<string:filename>', methods=['GET','POST'])
@login_required
def del_sample(application,folder,filename):
    logging.info('Visited del sample '+application+' '+folder+' '+filename)
    user=db.get_user(current_user.id)

    if user['role']!='admin':
        return 'You should be an admin'

    bucket_name = config[application]['bucket']
    fn_1=filename+'.json'
    fn_2=filename+'.'+config[application]["image_ext"]

    try:
        s3.Object(bucket_name,folder+'/'+fn_1).delete()
        db.delete_file(application,folder,fn_1)
        s3.Object(bucket_name,folder+'/'+fn_2).delete()
        db.delete_file(application,folder,fn_2)

    except botocore.exceptions.ClientError as e: 
        return None
    return redirect('/review/'+application)

@review_api.route('/review/del_all_samples_for_user/<string:application>/<string:folder>', methods=['GET','POST'])
@login_required
def del_all_samples(application,folder):
    logging.info('Visited del all sample for user '+application+' '+folder)
    user=db.get_user(current_user.id)

    if user['role']!='admin':
        return 'You should be an admin'
    cur_user=session['user_to_review']

    
    bucket_name = config[application]['bucket']

    files=db.get_files(application,folder,cur_user)
    for i in range(len(files)):
        filename=files[i]['filename']
        fn_1=filename
        fn_2=filename.replace('.json','.'+config[application]["image_ext"])
        #print(fn_1,fn_2)

        try:
            s3.Object(bucket_name,folder+'/'+fn_1).delete()
            db.delete_file(application,folder,fn_1)
            s3.Object(bucket_name,folder+'/'+fn_2).delete()
            db.delete_file(application,folder,fn_2)

        except botocore.exceptions.ClientError as e: 
            logging.error(bucket_name+' '+folder+' '+ fn_1+' '+fn_2+' were not deleted')

    return redirect('/review/'+application)



@review_api.route('/review/<string:application>/<string:folder>/<string:filename>', methods=['GET','POST'])
@login_required
def review_file(application,folder,filename):
    logging.info('Visited review')
    user=db.get_user(current_user.id)
    
    width=config[application]['width']
    height=config[application]['height']

    return render_template(application+'.html',width=width,height=height,application=application,review=True,
        filename=filename,folder=folder,image_ext=config[application]['image_ext'])

   

@review_api.route('/files/<string:application>/<string:folder>/<string:filename>', methods=['GET'])
@login_required
def files(application,folder,filename):
    if application in config['applications']:
        logging.info('Returning image with application = {}, folder={}, filename = {}'.format(application,folder, filename))
        bucket_name = config[application]['bucket']
        file_key = folder+"/" + filename
        logging.info('Use bucket_name = {}, and file_key = {}'.format(bucket_name, file_key))
        try:
            response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        except botocore.exceptions.ClientError as e: 
            db.delete_file(application,folder,filename)
            return None
        data = response['Body']
        return send_file(data, attachment_filename=filename)  
    return None





