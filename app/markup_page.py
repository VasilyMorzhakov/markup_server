from flask import render_template
from flask import send_from_directory, send_file,url_for,redirect
from flask import request
import json
import logging
import os
from flask_login import login_user, logout_user, current_user, login_required,LoginManager,UserMixin
from flask import Blueprint,session

markuppage_api = Blueprint('markuppage_api', __name__)

f=open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'config.json'),'r+')
config=json.load(f)
f.close()

@markuppage_api.route('/markup/<string:application>')
@login_required
def markup(application):
    logging.info('Visited /markup/'+application)
    if application in config['applications']:
        width=config[application]['width']
        height=config[application]['height']
        return render_template(application+'.html',width=width,height=height,application=application,review=False,log_in_or_out="out")
    else:
        return "no such application"

@markuppage_api.route('/markup/<string:application>/set_resize', methods=['POST'])
@login_required
def set_resize(application):
    value=request.args.get('resize')
    if not value is None:
        session[application+':resize']=value
        
    else:
        session[application+':resize']='True'
    return "ok"
@markuppage_api.route('/markup/<string:application>/get_resize', methods=['GET'])
def get_resize(application):
    value=session.get(application+':resize')
    if not value is None:
        return value
    else:
        return 'True'
