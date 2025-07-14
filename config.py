# -*- coding: utf-8 -*-
import os
import json


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class JsonConfig:
    DATA = json.loads(open('{}/config.json'.format(ROOT_DIR)).read())

    @staticmethod
    def get_data(varname, value=None):
        result = JsonConfig.DATA.get(varname) or os.getenv(varname) or value
        if result == 'true':
            return True
        elif result == 'false':
            return False
        return result

    @staticmethod
    def set_data(key, value):
        JsonConfig.DATA[key] = value
        with open('{}/config.json'.format(ROOT_DIR), 'w') as f:
            json.dump(JsonConfig.DATA, f, indent=4)


# app config
class Config:
    ROOT_DIR = ROOT_DIR
    STATIC_DIR = '{0}/static'.format(ROOT_DIR)
    TEMPLATES_DIR = '{0}/template'.format(ROOT_DIR)
    MEDIA_DIR = '{}/media'.format(STATIC_DIR)
    ERROR_CODE = {
        40000: 'Bad Request',
        41000: 'Gone',
        40300: 'Forbidden',
        40400: 'Not Found',
        42200: 'Invalid Request',
        50000: 'Internal Server Error',
    }

    APP_MODE_PRODUCTION = 'production'
    APP_MODE_DEVELOPMENT = 'development'
    APP_MODE_TESTING = 'testing'

    APP_MODE = JsonConfig.get_data('APP_MODE', APP_MODE_DEVELOPMENT)
    APP_HOST = JsonConfig.get_data('APP_HOST', '0.0.0.0')
    APP_PORT = int(JsonConfig.get_data('APP_PORT', 8000))

    DB_USER_NAME = JsonConfig.get_data('DB_USER_NAME', 'admin')
    DB_USER_PASSWD = JsonConfig.get_data('DB_USER_PASSWD', 'asdf1234')
    DB_HOST = JsonConfig.get_data('DB_HOST', '168.235.78.161')
    DB_NAME = JsonConfig.get_data('DB_NAME', 'org')

    REDIS_HOST = JsonConfig.get_data('REDIS_HOST', 'localhost')
    REDIS_PASSWD = JsonConfig.get_data('REDIS_PASSWD')
    
    SECRET = JsonConfig.get_data('SECRET')

    @staticmethod
    def from_app_mode():
        mode = {
            Config.APP_MODE_PRODUCTION: 'config.ProductionConfig',
            Config.APP_MODE_DEVELOPMENT: 'config.DevelopmentConfig',
            Config.APP_MODE_TESTING: 'config.TestingConfig',
        }
        return mode.get(Config.APP_MODE, mode[Config.APP_MODE_DEVELOPMENT])
