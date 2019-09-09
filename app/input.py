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
import datetime
import calendar


s3 = boto3.resource('s3')
s3_client  = boto3.client('s3')


input_api = Blueprint('input_api', __name__)
f=open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'config.json'),'r+')
config=json.load(f)
f.close()

@input_api.route('/input/del_day/<string:application>/<string:folder>/<string:day>', methods=['GET','POST'])
@login_required
def del_day(application,folder,day):
    logging.info('del_day '+application+' '+folder+' '+day)
    user=db.get_user(current_user.id)
    if user['role']!='admin':
        return 'You should be an admin'
  
    bucket_name = config[application]['bucket']

    print(application,folder,day)
    files=db.get_files(application,folder,date=day)
    for i in range(len(files)):
        try:
            s3.Object(bucket_name,folder+'/'+files[i]['filename']).delete()
            db.delete_file(application,folder,files[i]['filename'])

        except botocore.exceptions.ClientError as e: 
            logging.error(bucket_name+' '+folder+' '+ files[i]['filename']+' were not deleted')


    return redirect('/input/'+application)


@input_api.route('/input/<string:application>', methods=['GET','POST'])
@login_required
def input_get(application):
    logging.info('Visited input')
    user=db.get_user(current_user.id)

    if user['role']!='admin':
        return 'You should be an admin'

    if request.method == 'POST':
        session['cur_month']=request.form['month']

    if session.get('cur_month') is not None:
        cur_month=session.get('cur_month')  
        
    else:
        cur_month=datetime.datetime.today().strftime("%Y-%m")

    year=int(cur_month.split('-')[0])
    month=int(cur_month.split('-')[1])

    num_days = calendar.monthrange(year, month)[1]

    days = [datetime.date(year, month, day) for day in range(1, num_days+1)]
    
    day_by_day=[]
    for i in range(len(days)):
        day={}
        day['date']=days[i].strftime("%d-%m-%Y")
        files=db.get_files(application,config[application]['input'],date=day['date'])
        if len(files)>0:
            day['count']=len(files)
            day_by_day.append(day)

    return render_template('input.html',application=application,cur_month=cur_month,day_by_day=day_by_day,input=config[application]['input'])