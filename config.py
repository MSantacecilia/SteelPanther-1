import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Scheme: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>"

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'postgres+psycopg2://mukulbatra:Cleaver@54321@localhost:5432/mydb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False