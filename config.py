import os

APP_ROOT_DIR = os.path.abspath(os.path.dirname(__file__)) # define the root dir of this application as the dir containing this file


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or "unclejackgavemehiswaterbillformythirdbirthday" # seecrt ke do noot steel

    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DB_URI") or "sqlite:///" + os.path.join(APP_ROOT_DIR, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False # don't notify the flask app every time something changes in the database
