# fwat

A Fast Whole-slide image Annotation Tool (FWAT) for conducting painless studies requiring annotations on whole-slide images.


## Test server to view a single image

1. In config.py, set the two variables to specify which WSI to use.

``
TEST_WSI_DIR
TEST_WSI_FILE_NAME 
``

2. Make sure Python and Flask are installed.

3. Initiate and migrate database (SQLite) --> Not needed for viewing a test image.

flask db init
flask db migrate 

4. Start server.

``
python run.py
``

5. Access the image server to view the single image at:

``your_local_host_:port/view_single/-1/0``