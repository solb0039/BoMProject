from config import Config
from dotenv import load_dotenv
import os

APP_ROOT = os.path.join(os.path.dirname(__file__), '..')
dotenv_path = os.path.join(__file__, '.env')
load_dotenv(dotenv_path)

from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)

from app import routes

