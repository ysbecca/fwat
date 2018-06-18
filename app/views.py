from app import app
from app.models import *

from flask import render_template, make_response, url_for, abort, request, flash, redirect
import openslide
from openslide import ImageSlide, open_slide
from openslide.deepzoom import DeepZoomGenerator
import re
from unicodedata import normalize
from io import BytesIO
import json
import ast


@app.route('/view_study/')
def view_study():
	study = app.config["STUDY"]
	dataset = app.config["DATASET"]
	image_count = app.config["IMAGE_COUNT"]

	return render_template('view_study.html',
							study=study,
							dataset=dataset,
							image_count=image_count)

# Temporary single page for viewing a single WSI - testing only.
@app.route('/view_single/<int:image_num>')
def view_single(image_num):

	study = app.config["STUDY"]
	dataset = app.config["DATASET"]
	image_count = app.config["IMAGE_COUNT"]

	if image_num >= image_count or image_num < 0:
		print("At end or beginning of study.")
		# Redirect to study page - study completed, or back to beginning.
		return render_template('view_study.html',
					study=study,
					dataset=dataset,
					image_count=image_count)
	else:
		image_dir = app.config["IMAGE_PATHS"][image_num]
		file_name = app.config["IMAGES"][image_num]

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
		app.slide_properties = slide.properties
		slide_url = url_for('dzi', slug=slide_slug)


	# Look for any pre-existing annotations to display (on sidebar only)
	json_files = fetch_annotations(file_name)
	coords = []
	if not app.config["DRAW"]:
		coords = fetch_coords(json_files)

	return render_template('view_single.html', slide_url=slide_url,
            slide_mpp=app.slide_mpp,
            image_dir=image_dir,
            file_name=file_name,
            x=x, y=y,
            study=study,
            dataset=dataset,
            image_num=image_num,
            image_count=image_count,
            annotation_types=app.config['ANNOTATION_TYPES'],
            saved_annotations=json_files,
            draw=app.config["DRAW"],
            coords=coords)


@app.route('/save_annotations', methods=['POST'])
def save_annotations():
    print("Received: " + str(request))
    
    data = request.values.to_dict(flat=False)
    # This is a hack because of the way the data is stored in a stringified string.
    key, value = data.popitem()
    parsed_data = ast.literal_eval(key)
    paths = parsed_data["paths"]

    wsi_x, wsi_y = parsed_data["wsi_x"], parsed_data["wsi_y"]
    code = parsed_data["code"]
    file_name = parsed_data["file_name"]

    # Parse and save annotations
    state = save_new_annotations_file(paths, wsi_x, wsi_y, code, file_name[:-4])

    return json.dumps({'status': state, 'data': str(paths) });


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
