from app import app
import json
from os import listdir
from os.path import isfile, join

import urllib.request
from xml.dom import minidom

# Helper functions (No DB)


def fetch_annotations(file_name):
	if app.config["DRAW"]:
		this_dir = app.config["ANNOTATION_DIR"]
	else:
		this_dir = app.config["ANNOTATION_RDIR"]
	files = [file for file in listdir(this_dir) if (isfile(join(this_dir, file)) and file_name[:-4] in file)]
	print("Files: ", files)
	return files


def fetch_coords(file_names):
	all_coords, errors = [], []
	error = 0
        if app.config["DRAW"]:
                this_dir = app.config["ANNOTATION_DIR"]
        else:
                this_dir = app.config["ANNOTATION_RDIR"]


	for f in file_names:
		print("==============", f, "=========")
		if app.config["IS_XML"]:
			try:
				xml = minidom.parse(this_dir + f)
			except:
				errors.append(f)
				error = 1
			if not error:
				regions = xml.getElementsByTagName("Region")
				coords = []

				for region in regions:
					# key = region.getElementsByTagName("Attribute")[0].attributes['Value'].value
					vertices = region.getElementsByTagName("Vertex")
					one_coord = np.zeros((len(vertices), 2))

					for i, vertex in enumerate(vertices):
						one_coord[i][0] = vertex.attributes['X'].value
						one_coord[i][1] = vertex.attributes['Y'].value
					coords.append(one_coord)
				all_coords.append(coords)
				print("Read", coords)
		else: # JSON
			with open(this_dir + f) as f_:
				data = json.load(f_)
				all_coords.append(data)

	print("Annotation file errors: " + str(errors))
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



