from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_pyfile('config.py')

# Add the Bootstrap markup
Bootstrap(app)

# Create an instance of the DB
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import models, views