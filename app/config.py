import os

basedir = os.path.abspath(os.path.dirname(__file__))


# Put path to test WSI image here.
# Filename of test WSI image.
TEST_WSI_DIR = "/Users/ysbecca/ysbecca-projects/iciar-2018/data/WSI_xml/Case_0001/"
TEST_WSI_FILE_NAME = "A01.svs"


SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True


# DB in progress


DEEPZOOM_SLIDE=None		# View one slide at a time
DEEPZOOM_FORMAT='jpeg'
DEEPZOOM_TILE_SIZE=254
DEEPZOOM_OVERLAP=1
DEEPZOOM_LIMIT_BOUNDS=True
DEEPZOOM_TILE_QUALITY=75
SLIDE_NAME='slide'