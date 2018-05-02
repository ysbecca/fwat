from app import db

class Image(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	file_name = db.Column(db.String(100), index=True, unique=True)
	file_dir = db.Column(db.String(100))
	xml_files = db.Column(db.String(1000)) # An array of file names stringified.

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