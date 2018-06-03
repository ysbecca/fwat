from app import app, db, models
import csv
from os import listdir
from os.path import isfile, join

# Set general variables.
dataset_name = "BCSP Expert Training Set"
study_name = dataset_name + " Study"
study_desc = "Annotation of training set for submucosa and epithelial layers."

case_dir = "/nobackup/sc16rsmy/bcsp-expert-cases/"
csv_path = "/home/ufaserv1_k/sc16rsmy/bcsp-expert/training_cases_only.csv"


# Read case numbers from CSV file.
image_paths = []
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
			image_paths.append(this_case_dir + "/" + f)

print("Found", len(image_paths), "images from all cases.")
print(image_paths)


'''
dataset = models.Dataset(name=dataset_name, directory=case_dir)

# Make an object for each image in the dataset.
images = []
for image_path in image_paths:
	images.append(models.Image(file_name="01.svs", file_dir=image_path, dataset_id=dataset.id))


study = models.Study(name=study_name, description=study_desc, dataset_id=dataset.id)

# Add and commit all objects.
db.session.add(dataset)
for image in images:
	db.session.add(image)

db.session.add(study)
print("Committing now...")

db.session.commit()
'''
