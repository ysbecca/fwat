import csv
import os
from os import listdir
from os.path import isfile, join


basedir = os.path.abspath(os.path.dirname(__file__))

# If 0, then will automatically look for annotations to view.
DRAW = 0

# Annotation saving directories
ANNOTATION_DIR = ""
# An array with short codes for annotation types - for example, if annotating tumour and stroma,
# array could be ["T", "S"] or ["TU", "ST"]
ANNOTATION_TYPES = [] 

# Where to read existing annotations from - for displaying. This can be set to ANNOTATION_DIR if 
# it is the same.
ANNOTATION_RDIR = ""

# Details for displaying basic study information on main page.
DATASET = "Dataset name"
STUDY = "Short description of study"

# Case info: optional; can be customised based on file structure.
case_dir = ""
csv_path = ""

# Read case numbers from CSV file.
IMAGE_PATHS = []
IMAGES = []
cases = []

with open(csv_path, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=' ', quotechar='|')
        for row in reader:
                cases.append(row[0])

print("Found", len(cases), "cases.")

for case in cases:
		# Again, this can be customised based on your directory structure.
        this_case_dir = case_dir + "Case_" + case
        files = [file for file in listdir(this_case_dir) if isfile(join(this_case_dir, file))]
        for f in files:
                if '.svs' in f:
                        IMAGE_PATHS.append(this_case_dir + "/")
                        IMAGES.append(f)

IMAGE_COUNT = len(IMAGE_PATHS)

print("Found", IMAGE_COUNT, "images from all cases.")

# DeepZoom config parameters

DEEPZOOM_SLIDE=None		# View one slide at a time
DEEPZOOM_FORMAT='jpeg'
DEEPZOOM_TILE_SIZE=254
DEEPZOOM_OVERLAP=1
DEEPZOOM_LIMIT_BOUNDS=True
DEEPZOOM_TILE_QUALITY=50
SLIDE_NAME='slide'
