# views.py
# =============================================================================
#
# Flask App viewer for OpenSeadragon DeepZoom architecture
#
# Defines the different views for the app
#     e.g.     /                 (default view)
#            /view_single     (single slide viewer)
#            /view_branded     (branded slide viewer)
#
# =============================================================================

import json
import ast
import re
import openslide

from io import BytesIO
from unicodedata import normalize

from app import app
# from app.models import *

from flask import render_template
from flask import make_response
from flask import url_for
from flask import abort
from flask import request
from flask import flash
from flask import redirect

from openslide import ImageSlide
from openslide import open_slide
from openslide.deepzoom import DeepZoomGenerator


# Home view - now hijacked to view single slide given path
#
# Path is relative to the web root of slides.virtualpathology.leeds.ac.uk
# Python can handle the forwardslashes in the path
# Path gets concatenated to 'S:/' - assuming slide storage is mapped to S drive

@app.route('/<path:file_path>')
def view_standalone(file_path):

    #print("Raw file_path = " + file_path)
    file_path         = file_path.replace("/view.apml", "")
    exploded_path     = file_path.split('/')    
    #print("Edited file_path = " + file_path)
    
    file_name = exploded_path[-1]
    image_dir = file_path.replace(file_name, '')
    image_dir = image_dir.replace('%2F', '/')
    image_dir = 'S:/' + image_dir
    print(" ")
    print("========= Slide Name:   " + file_name)
    print("========= Slide Path:   " + image_dir + file_name)
    
    # Set single WSI options
    config_map = {
        'DEEPZOOM_TILE_SIZE':         'tile_size',
        'DEEPZOOM_OVERLAP':         'overlap',
        'DEEPZOOM_LIMIT_BOUNDS':     'limit_bounds',
    }
    
    opts     = dict((v, app.config[k]) for k, v in config_map.items())
    slide    = open_slide(image_dir + file_name)
	
    #print(opts)
    #print(slide)

    # Fetch the x and y dimensions of the original WSI
    if not slide: 
        associated_urls = {}
        file_name = "ERROR: unable to load image " + file_name + " at " + image_dir
        print("========= ERROR: Unable to Load Whole Slide Image")
        print(" ")
    else:
        x, y = slide.dimensions    
        print("========= Slide Width:  " + str(x))
        print("========= Slide Height: " + str(y))
        
        try:
            mpp_x             = slide.properties[openslide.PROPERTY_NAME_MPP_X]
            mpp_y             = slide.properties[openslide.PROPERTY_NAME_MPP_Y]
            app.slide_mpp     = (float(mpp_x) + float(mpp_y)) / 2
            
            print("========= Slide MPP X:  " + str(mpp_x))
            print("========= Slide MPP Y:  " + str(mpp_y))
            print(" ")
            
        except (KeyError, ValueError):
            app.slide_mpp = 0
            
            print("========= Slide MPP X:  " + str(0))
            print("========= Slide MPP Y:  " + str(0))
            print(" ")
            
        # end try except

        # Save globally in app config variables
        slide_slug = slugify(file_name)
		
        app.slides = {
            slide_slug: DeepZoomGenerator(slide, **opts)
        }
		
        app.config['DEEPZOOM_SLIDE'] 	= image_dir + file_name
        app.associated_images   		= []
        app.slide_properties 			= slide.properties
		
		# Get associated images (thumbs, labels etc)
        for name, image in slide.associated_images.items():
            app.associated_images.append(name)
            slug = slugify(name)
            app.slides[slug] = DeepZoomGenerator(ImageSlide(image), **opts)
            #print(app.slides[slug])
		# end for associated_images

        slide_url       = url_for(
                            'dzi', 
                            slug = slide_slug
                        )
                        
        associated_urls   = dict(
                                (file_name, 
                                    url_for(
                                        'dzi', 
                                        slug = slugify(file_name)
                                    )
                                )        
                                for file_name in app.associated_images
                            )
                
        # end of if else

    return render_template('view_standalone.html', 
            slide_url    = slide_url,
            associated   = associated_urls, #, properties=app.slide_properties,
            slide_mpp    = app.slide_mpp,
            image_dir    = image_dir,
            file_name    = file_name,
            x            = x, 
            y            = y,
            study        = None,
            dataset      = None,
            image_id     = 0,
            image_num    = 0,
            image_count  = 1)


# end def view_standalone


@app.route('/view_study/<int:study_id>')
def view_study(study_id):
    study = Study.query.get(study_id)
    dataset = study.dataset
    image_count = dataset.images.count()

    return render_template('view_study.html',
                            study=study,
                            dataset=dataset,
                            image_count=image_count)
                            

# Temporary single page for viewing a single WSI - testing only.
# @app.route('/view_branded/<int:study_id>/<int:image_num>')
@app.route('/view_single/<int:study_id>/<int:image_num>')
def view_single(study_id, image_num):

    # Test case only
    if study_id == 0:
        image_id = 0
        image_dir = app.config['TEST_WSI_DIR']
        file_name = app.config['TEST_WSI_FILE_NAME']
        study = None
        dataset = None
        image_count = 1


    # Set single WSI options
    config_map = {
        'DEEPZOOM_TILE_SIZE': 'tile_size',
        'DEEPZOOM_OVERLAP': 'overlap',
        'DEEPZOOM_LIMIT_BOUNDS': 'limit_bounds',
    }
    opts = dict((v, app.config[k]) for k, v in config_map.items())
    print("========= " + image_dir + file_name + " ==========")
    slide = open_slide(image_dir + file_name)

    # Fetch the x and y dimensions of the original WSI
    if not slide: 
        associated_urls = {}
        file_name = "ERROR: unable to load image " + file_name + " at " + image_dir
    else:
        x, y = slide.dimensions
        print("X, Y: " + str(x) + ", " + str(y))

        try:
            mpp_x = slide.properties[openslide.PROPERTY_NAME_MPP_X]
            mpp_y = slide.properties[openslide.PROPERTY_NAME_MPP_Y]
            app.slide_mpp = (float(mpp_x) + float(mpp_y)) / 2
        except (KeyError, ValueError):
            app.slide_mpp = 0

        # Save globally in app config variables
        slide_slug = slugify(file_name)
        app.slides = {
            slide_slug: DeepZoomGenerator(slide, **opts)
        }
        app.config['DEEPZOOM_SLIDE'] = image_dir + file_name

        app.associated_images = []
        app.slide_properties = slide.properties
        for name, image in slide.associated_images.items():
            app.associated_images.append(name)
            slug = slugify(name)
            app.slides[slug] = DeepZoomGenerator(ImageSlide(image), **opts)


        slide_url = url_for('dzi', slug=slide_slug)
        associated_urls = dict((file_name, url_for('dzi', slug=slugify(file_name)))
                for file_name in app.associated_images)

    return render_template('view_branded.html', slide_url=slide_url,
            associated=associated_urls, #, properties=app.slide_properties,
            slide_mpp=app.slide_mpp,
            image_id=image_id,
            image_dir=image_dir,
            file_name=file_name,
            x=x, y=y,
            study=study,
            dataset=dataset,
            image_num=image_num,
            image_count=image_count)


@app.route('/save_annotations', methods=['POST'])
def save_annotations():
    print("Received: " + str(request))
    
    data = request.values.to_dict(flat=False)
    # This is a hack because of the way the data is stored in a stringified string.
    key, value = data.popitem()
    parsed_data = ast.literal_eval(key)
    paths = parsed_data["paths"]
    image_id = parsed_data["image_id"]
    wsi_x, wsi_y = parsed_data["wsi_x"], parsed_data["wsi_y"]

    # Create "save_annotation" function of Image model.
    # It does parsing and saving.
    # Image.save_new_annotations_file(svg_path_string, wsi_x, wsi_y)

    return json.dumps({'status':'OK','data': str(paths) });


@app.route('/<slug>.dzi')
def dzi(slug):
    format = app.config['DEEPZOOM_FORMAT']
    try:
        resp = make_response(app.slides[slug].get_dzi(format))
        resp.mimetype = 'application/xml'
        return resp
    except KeyError:
        # Unknown slug
        abort(404)


@app.route('/<slug>_files/<int:level>/<int:col>_<int:row>.<format>')
def tile(slug, level, col, row, format):
    format = format.lower()
    if format != 'jpeg' and format != 'png':
        # Not supported by Deep Zoom
        abort(404)
    try:
        tile = app.slides[slug].get_tile(level, (col, row))
    except KeyError:
        # Unknown slug
        abort(404)
    except ValueError:
        # Invalid level or coordinates
        abort(404)
    buf = PILBytesIO()
    tile.save(buf, format, quality=app.config['DEEPZOOM_TILE_QUALITY'])
    resp = make_response(buf.getvalue())
    resp.mimetype = 'image/%s' % format
    return resp

def slugify(text):
    text = normalize('NFKD', text.lower()).encode('ascii', 'ignore').decode()
    return re.sub('[^a-z0-9]+', '-', text)


class PILBytesIO(BytesIO):
    def fileno(self):
        '''Classic PIL doesn't understand io.UnsupportedOperation.'''
        raise AttributeError('Not supported')
