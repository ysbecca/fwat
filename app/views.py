from app import app

from flask import render_template, make_response, url_for, abort
import openslide
from openslide import ImageSlide, open_slide
from openslide.deepzoom import DeepZoomGenerator
import re
from unicodedata import normalize
from io import BytesIO



@app.route('/')
def index():
    user = {'name': 'R Stone'}
    return render_template('index.html',
                           user=user)

# @app.route('/view/<int:study_id>/<int:image_id>')

# Temporary single page for viewing a single WSI - testing only.
@app.route('/view_single')
def view_single():
	# Eventually, will load the image object from DB
	image_id = 0
	image_dir = "/Users/ysbecca/ysbecca-projects/iciar-2018/data/WSI_xml/Case_0001/"
	file_name = "A01.svs"

	# Set single WSI options
	config_map = {
	    'DEEPZOOM_TILE_SIZE': 'tile_size',
	    'DEEPZOOM_OVERLAP': 'overlap',
	    'DEEPZOOM_LIMIT_BOUNDS': 'limit_bounds',
	}
	opts = dict((v, app.config[k]) for k, v in config_map.items())

	slide = open_slide(image_dir + file_name)
	try:
	    mpp_x = slide.properties[openslide.PROPERTY_NAME_MPP_X]
	    mpp_y = slide.properties[openslide.PROPERTY_NAME_MPP_Y]
	    app.slide_mpp = (float(mpp_x) + float(mpp_y)) / 2
	except (KeyError, ValueError):
		app.slide_mpp = 0

	# Save globally in app config variables
	slide_slug = file_name
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

	return render_template('view_single.html', slide_url=slide_url,
            associated=associated_urls, #, properties=app.slide_properties,
            slide_mpp=app.slide_mpp,
            image_id=image_id,
            image_dir=image_dir,
            file_name=file_name)

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
