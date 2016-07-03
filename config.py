import os


class Config:

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MONGO_DBNAME = 'scarf'
    TEMP_FOLDER = 'tmp'

    try:
        SECRET_KEY = os.environ['SECRET_KEY']
    except KeyError as err: 
        print('''Please have an shell environment variable by the name "SECRET_KEY". 
        Flask-WTF module uses this SECRET_KEY to generate encrypted tokens that 
        are used to verify the authenticity of requests with "HTML form data"''')
        raise err

    
class TestingConfig(Config):
    TESTING = True


class ProductionConfig(DevelopmentConfig):
    pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
