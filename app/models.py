from app import app
import json
from os import listdir
from os.path import isfile, join

# Helper functions (No DB)


def fetch_annotations(file_name):
	this_dir = app.config["ANNOTATION_DIR"]
	files = [file for file in listdir(this_dir) if (isfile(join(this_dir, file)) and file_name[:-4] in file)]
	
	return files


def fetch_coords(file_names):
	all_coords = []
	for file in file_names:
		with open(app.config["ANNOTATION_DIR"] + file) as f:
			data = json.load(f)
			all_coords.append(data)
	return all_coords


def convert_path_coords(paths, wsi_x, wsi_y):
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


def xml_coords_to_svg(coords, wsi_x, wsi_y):
	''' Converts a numpy array of a list of coordinates to svg coordinates for displaying on the viewBox. '''
	# app.config["ANNOTATION_RDIR"]
	x_factor, y_factor = wsi_x / 100.0, wsi_y / 100.0
	# for c in coords:
		


def save_new_annotations_file(svg_path_string, wsi_x, wsi_y, code, file_name):
	''' Saves WSI coordinates. '''
	coords = convert_path_coords(svg_path_string, wsi_x, wsi_y)

	if len(coords):
		annotation_file = file_name + "_" + code + ".json"
		print(annotation_file, "saving to", app.config["ANNOTATION_DIR"])

		with open(app.config["ANNOTATION_DIR"] + annotation_file, 'w') as outfile:
			json.dump(coords, outfile)

		return True
	else:
		print("No coordinates to save.")
		return False



