import os
from datetime import datetime, timedelta, timezone

class Config:

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MONGO_DBNAME = 'scarf'


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
