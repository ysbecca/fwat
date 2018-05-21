from app import db
from wtforms import Form, BooleanField, StringField, PasswordField, TextAreaField, SelectField, validators

# TODO Placeholder until we have created datasets
TEMP_DATASET_CHOICES = [(1, 'Colorectal Cancer Leeds'),(2, 'NHS BCSP All')]



class DatasetForm(Form):
	name = StringField('Name', [validators.Length(min=4, max=30)])
	directory = StringField('Directory', [validators.DataRequired()])
	# Something for selecting images (text string now for storing paths)
	images = TextAreaField("Select images", [validators.optional()])

class StudyForm(Form):
    name = StringField('Name', [validators.Length(min=4, max=30)])
    # TODO replace by admin ID
    creator = StringField('Name of creator', [validators.Length(min=2, max=50)])
    description = TextAreaField('Description of study', [validators.optional(), validators.length(max=300)])
    
    # TODO query DB for all created image datasets
    dataset = StringField('Dataset', [validators.DataRequired()])

    hide_annotated_images = BooleanField('Hide images once annotated', [validators.DataRequired()])
    code = StringField('Set the access code for all study participants', [validators.Length(min=6, max=20)])

# class Admin(db.Model):
	# id = db.Column(db.Integer, primary_key=True)
	# name = db.Column(db.String(100), unique=True)

class Dataset(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(35))
	directory = db.Column(db.String(150))
	images = db.relationship('Image', backref='dataset', lazy='dynamic')
	studies = db.relationship('Study', backref='dataset', lazy='dynamic')

	def __repr__(self):
		return '' % (self.id, self.name, self.directory)

class Study(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(35))
	# admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
	description = db.Column(db.Text())
	dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'))
	
class AnnotationFile(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	file_name = db.Column(db.String(100), index=True, unique=True)
	file_dir = db.Column(db.String(200))
	image_id = db.Column(db.Integer, db.ForeignKey('image.id'))

	def __repr__(self):
		return '' % (self.id, self.file_name, self.file_dir, self.image_id)

class Image(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	file_name = db.Column(db.String(100), index=True, unique=True)
	file_dir = db.Column(db.String(200))
	annotation_files = db.relationship('AnnotationFile', backref='image', lazy='dynamic')
	dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'))

	def __repr__(self):
		return '' % (self.id, self.file_name, self.file_dir)

	def convert_path_coords(svg_path_string, wsi_x, wsi_y):
		''' Converts from SVG (100, 100) no aspect ratio preserved viewBox to WSI original coords. '''
		all_coords = []
		x_factor, y_factor = wsi_x / 100.0, wsi_y / 100.0

		for path in paths:
		    split_path = path.replace("M", ",").replace("L", ",").split(",")[1:]
		    split_path = list(map(str.strip, split_path))

		    coords_array = []
		    for coord in split_path:
		        x, y = coord.split(" ")
		        coords_array.append([round(x_factor*float(x), 2), round(y_factor*float(y), 2)])
		    all_coords.append(coords_array)
		return all_coords

	def save_new_annotations_file(svg_path_string, wsi_x, wsi_y):
		# Saves WSI coordinates into an Aperio XML file.

		coords = convert_path_coords(svg_path_string, wsi_x, wsi_y)

		if len(coords):
			print(coords)

			# TODO save using image file_name (self.file_name)
			print("Successful conversion and save.")
			# Return success message.
			return True
		else:
			return False