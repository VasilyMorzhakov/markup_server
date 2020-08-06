import logging
import os
from app.review import review_api
from app.input import input_api
from app.markup_page import markuppage_api

logging.basicConfig(filename='markup.log',level=logging.INFO)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ['SECRET_KEY']
app.register_blueprint(review_api)
app.register_blueprint(input_api)
app.register_blueprint(markuppage_api)
import data_manager



if __name__=='__main__':
    app.run(host='0.0.0.0',port=5005)


