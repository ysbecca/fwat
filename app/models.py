from app import app
import json


# Extra helper functions
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
	# Saves WSI coordinates.
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



