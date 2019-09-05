from app import app
from flask import render_template
from flask import send_from_directory, send_file,url_for,redirect
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
from app.forms import RegistrationForm
from flask_login import login_user, logout_user, current_user, login_required,LoginManager,UserMixin


s3 = boto3.resource('s3')
s3_client  = boto3.client('s3')



f=open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'config.json'),'r+')
config=json.load(f)
f.close()

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):

    user_dict=db.get_user(email)
    if user_dict is None:
        return

    user = User()
    user.id = user_dict['email']
    user.name=user_dict['email']
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')

    user_dict=db.get_user(email)

    if user_dict is None:
        return

    user = User()
    user.id = user_dict['email']
    user.name=user_dict['email']

    user.is_authenticated = db.check_password(email,request.form['password'])

    return user

@app.route('/')
@login_required
def index():
    logging.info('Visited root')
    return 'Logged in as: ' + current_user.id

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'/>
                <input type='password' name='password' id='password' placeholder='password'/>
                <input type='submit' name='submit'/>
               </form>
               '''
    email = request.form['email']

    if db.check_password(email,request.form['password']):
        user_dict=db.get_user(email)
        user = User()
        user.id = user_dict['email']
        user.name= user_dict['email']

        login_user(user)
        return redirect('/')
    return 'Bad login'

@app.route('/logout')
def logout():
    logout_user()
    return 'Logged out'
@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect('/login')

@app.route('/register/<string:role>/<string:token>', methods=['GET'])
def register_get(role,token):
    print('register ',role,token)
    if db.check_pre_user(role,token):
        form = RegistrationForm(role)
        return render_template('register.html', title='Register', form=form)    
    return "no such user"

@app.route('/register/<string:role>/<string:token>', methods=['POST'])
def register_post(role,token):
    form = RegistrationForm(role)
    if form.validate_on_submit():
        db.add_user(form.username.data,form.email.data,form.password.data,form.role)
        db.del_pre_user(role,token)
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/upload/<string:application>',methods=['GET'])
@login_required
def upload_get(application):
    logging.info('Visited get /upload/'+application)
    if application in config['applications']:
        return render_template('uploadfiles.html',application=application,log_in_or_out='out')
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
@login_required
def markup(application):
    logging.info('Visited /markup/'+application)
    if application in config['applications']:
        width=config[application]['width']
        height=config[application]['height']
        
        return render_template(application+'.html',width=width,height=height,application=application,review=False,log_in_or_out="out")
    else:
        return "no such application"


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

@app.route('/<string:application>/get_file_names/<string:folder>')
def get_file_names(application,folder):

    if application in config['applications']:
        files=db.get_files(application,folder)
        res=[]
        for f in files:
            res.append(f['filename'])
        return json.dumps(res)
    else:
        return None
@app.route('/<string:application>/get_file/<string:folder>/<string:filename>')
def get_file(application,folder,filename):

    if application in config['applications']:
        logging.info('Returning file  with application = {}, folder = {}, filename = {}'.format(application,folder, filename))
        bucket_name = config[application]['bucket']
        file_key = folder+"/" + filename
        try:
            response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        except botocore.exceptions.ClientError as e: 
            db.delete_file(application,config[application]['input'],filename)
            return None

        data = response['Body']
        return send_file(data, attachment_filename=filename)  
    else:
        return None



@app.route('/<string:application>/get_random_pic_name')
@login_required
def get_random_pic_name(application):

    if application in config['applications']:
        start=time.time()
        folder=config[application]['input']
        files=db.get_files(application,folder)
        images=[e for e in files if (e['filename'].endswith('.jpg') or e['filename'].endswith('.png'))]
        index=random.randint(0,len(images)-1)
        res='/'+application+'/get_file/'+folder+'/'+images[index]['filename']
        #print('dt ',time.time()-start)
        return res
    else:
        return None

@app.route('/<string:application>/get_json/<string:folder>/<string:image_filename>')
@login_required
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
@login_required
def savePost(application):
    if application in config['applications']:
        bucket_name = config[application]['bucket']
        logging.info('savePost, application = {}, bucket_name = {}'.format(application, bucket_name))
        data = request.data

        dict=json.loads(data.decode())
        fn=dict['imageName']


        #recived markup

        image_path = fn.split('/')[3]+'/'+fn.split('/')[4]
        #print(image_path)

        if image_path.endswith('.jpg'):
            mark_path = image_path.replace(config[application]['input'], config[application]['output']).replace('.jpg','.json')
        else:
            if image_path.endswith('.png'):
                mark_path = image_path.replace(config[application]['input'], config[application]['output']).replace('.png', '.json')
            else:
                return "wrong file format"

        logging.info("Saving markup to " + mark_path)
        s3.Bucket(bucket_name).put_object(Key=mark_path, Body=data)
        db.put_file(application,config[application]['output'],os.path.basename(mark_path),user_id=current_user.id)

        #move image
        old_location = image_path
        new_location = image_path.replace(config[application]['input'], config[application]['output'])
        logging.info("Moving image from {} to {}".format(old_location, new_location))
        s3.Object(bucket_name, new_location).copy_from(CopySource=bucket_name+'/' + old_location)
        db.put_file(application,config[application]['output'],os.path.basename(new_location))

        s3.Object(bucket_name, old_location).delete()
        db.delete_file(application,config[application]['input'],os.path.basename(old_location))
        #print('to del mark:',mark_path)
        db.delete_file(application,config[application]['input'],os.path.basename(mark_path))
        s3.Object(bucket_name,mark_path.replace(config[application]['output'],config[application]['input'])).delete()



        return "ok"
    else:
        return "no such application"
