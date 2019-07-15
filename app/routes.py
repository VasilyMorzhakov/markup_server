from app import app
from flask import render_template
from flask import send_from_directory
from flask import request
import json
import os
import shutil

@app.route('/')
def index():
    return "This is a markup service"


@app.route('/markup')
def markup():
    return render_template('markup.html',width=600,height=600)

@app.route('/images/<path:filename>')
def return_image(filename):
    return send_from_directory('images',filename)

@app.route('/get_random_pic_name')
def get_random_pic_name():
    return "images/0.jpg"

@app.route('/save',methods=['POST'])
def savePost():
    data = request.data

    dict=json.loads(data.decode())
    fn=dict['imageName']
    fn_json=fn.replace('.jpg','.json')
    dir=os.path.dirname(os.path.realpath(__file__))

    f=open(os.path.join(dir,fn_json),'wb')
    f.write(data)
    f.close()

    #move to processed
    shutil.move(os.path.join(dir,fn),os.path.join(dir,fn.replace('images/','processed/')))
    shutil.move(os.path.join(dir, fn_json), os.path.join(dir, fn_json.replace('images/', 'processed/')))

    return "ok"