<<<<<<< HEAD
import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Scheme: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>"

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'postgres+psycopg2://matt:santa@54321@localhost:2345/mydb'
=======
import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Scheme: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>"

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'postgres+psycopg2://matt:santa@54321@localhost:2345/mydb'
>>>>>>> 0dff165015eeb955499a79290ce36a26867a031f
    SQLALCHEMY_TRACK_MODIFICATIONS = False