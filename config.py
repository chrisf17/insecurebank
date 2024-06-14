import os
from flask import Flask

class BaseConfig:
    DROPDB = False
    DEBUG = True
    DATABASE_URI = 'bank.db'
    USERNAME = 'admin'
    PASSWORD = 'P4$$w0rd'
    SECRET_KEY = 'your_secret_key'
    SESSION_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SECURE = False
    ASSET_FOLDER = 'static/statements'

class DevelopmentConfig(BaseConfig):
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True

class TestConfig(BaseConfig):
    DROPDB = True
    DEBUG=False

class ProductionConfig(BaseConfig):
    DEBUG = False
    SECRET_KEY = 'acme_bank_secret_key'


