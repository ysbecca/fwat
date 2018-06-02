from app import app, db, models
import csv


# Set general variables.
dataset_name = "BCSP Expert Training Set"
study_name = dataset_name + " Study"
study_desc = "Annotation of training set for submucosa and epithelial layers."

case_dir = "/Users/ysbecca/ysbecca-projects/iciar-2018/data/WSI_no_xml/"
csv_path = "/Users/ysbecca/ysbecca-projects/iciar-2018/data/cases.csv"


# Read case numbers from CSV file.
image_paths = []



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


