import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True


# Annotation saving directories
ANNOTATION_DIR = "/Users/ysbecca/ysbecca-projects/fwat/temp/"
ANNOTATION_TYPES = ["EP", "SM"]


DEEPZOOM_SLIDE=None		# View one slide at a time
DEEPZOOM_FORMAT='jpeg'
DEEPZOOM_TILE_SIZE=254
DEEPZOOM_OVERLAP=1
DEEPZOOM_LIMIT_BOUNDS=True
DEEPZOOM_TILE_QUALITY=75
SLIDE_NAME='slide'