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

@app.route('/')
def index():
    user = {'name': 'Rebecca Stone'}

    # Show all the datasets and studies on the dashboard
    datasets = Dataset.query.all()
    studies = Study.query.all()

    return render_template('index.html',
    					   datasets=datasets,
    					   studies=studies,
                           user=user)

@app.route('/new_dataset', methods=['GET', 'POST'])
def new_dataset():
	form = DatasetForm(request.form)
	if request.method == 'POST' and form.validate():
		print(form.name.data)
		print(form.directory.data)
		print(form.images.data)

		# dataset = Dataset(form.name.data, form.images.data)
		# db_session.add(dataset)

		flash('New dataset created:' + str(form.name.data))
		return redirect(url_for('/new_dataset'))

	return render_template('new_dataset.html', form=form)

# @app.route('/view/<int:study_id>/<int:image_id>')

@app.route('/run_study/<int:study_id>')
def run_study(study_id):
	study = Study.query.get(study_id)
	dataset = study.dataset
	image_num = 0
	# return redirect(url_for('/view_single', 
						# study_id=study.id,
						# dataset_id=dataset.id, 
						# image_num=0))
	return view_single(study.id, dataset.id, 0)

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
@app.route('/view_single/<int:study_id>/<int:image_num>')
def view_single(study_id, image_num):

	# Test case only
	if study_id == -1:
		image_id = 102
		image_dir = "/Users/ysbecca/ysbecca-projects/iciar-2018/data/WSI_xml/Case_0001/"
		file_name = "A01.svs"
	else:
		study = Study.query.get(study_id)
		dataset = study.dataset
		image_count = dataset.images.count()
		if image_num >= image_count or image_num < 0:
			print("At end or beginning of study.")
			# Redirect to study page - study completed, or back to beginning.
			return render_template('view_study.html',
						study=study,
						dataset=dataset,
						image_count=image_count)
		else:
			image = dataset.images[image_num]
			image_id = image.id
			image_dir = image.file_dir
			file_name = image.file_name

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

	return render_template('view_single.html', slide_url=slide_url,
            associated=associated_urls, #, properties=app.slide_properties,
            slide_mpp=app.slide_mpp,
            image_id=image_id,
            image_dir=image_dir,
            file_name=file_name,
            x=x, y=y,
            study=study,
            dataset_id=dataset.id,
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
    Image.save_new_annotations_file(svg_path_string, wsi_x, wsi_y)

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
