from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from config import config
from flask.ext.pymongo import PyMongo

bootstrap = Bootstrap()
moment = Moment()
mongo = PyMongo()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    mongo.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

