from app import app
from flask import render_template
from flask import send_from_directory
from flask import request
import json
import os
import shutil
import random

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
        dir=os.path.dirname(os.path.realpath(__file__))

        f=open(dir+'/data'+fn_json,'wb')
        f.write(data)
        f.close()

        #move to processed
        shutil.move(dir+'/data'+fn,dir+'/data'+fn.replace('images/','processed/'))
        shutil.move(dir+'/data'+fn_json, dir+'/data'+fn_json.replace('images/','processed/'))

        return "ok"
    else:
        return "no such application"