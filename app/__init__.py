from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap



app = Flask(__name__)
app.config.from_pyfile('config.cfg')


# Add the Bootstrap markup
Bootstrap(app)

# Create an instance of the DB
# db = SQLAlchemy(app)

from app import views #, models