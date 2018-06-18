import csv
import os
from os import listdir
from os.path import isfile, join


basedir = os.path.abspath(os.path.dirname(__file__))

# If False, then will automatically look for annotations to view.
DRAW = False

# Annotation saving directories
ANNOTATION_DIR = "/home/ufaserv1_k/sc16rsmy/bcsp-expert/annotations/"# "/Users/ysbecca/ysbecca-projects/fwat/temp/"
ANNOTATION_TYPES = ["EP", "SM"]

# Where to read existing annotations from - for displaying
ANNOTATION_RDIR = "/Users/ysbecca/ysbecca-projects/fwat/temp/"

DATASET = "BCSP Expert Training Set"
STUDY = "EP/SM Annotation BCSP Expert"

# Case info (equivalent to fill_db.py)
case_dir = "/nobackup/sc16rsmy/bcsp-expert-cases/" #/Users/ysbecca/ysbecca-projects/iciar-2018/data/WSI_xml/"
csv_path = "/home/ufaserv1_k/sc16rsmy/bcsp-expert/training_cases_only.csv"#"/Users/ysbecca/ysbecca-projects/fwat/test_cases.csv"

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
