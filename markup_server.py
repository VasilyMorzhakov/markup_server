from app import app
import logging
import os
from app.review import review_api
from app.input import input_api

app.config["SECRET_KEY"] = os.environ['SECRET_KEY']
app.register_blueprint(review_api)
app.register_blueprint(input_api)

logging.basicConfig(filename='markup.log',level=logging.INFO)

if __name__=='__main__':


    app.run(host='0.0.0.0',port=5000)
