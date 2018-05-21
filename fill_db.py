from app import app, db, models

d1 = models.Dataset(name="BACH Challenge WSI", directory="/Users/ysbecca/ysbecca-projects/iciar-2018/data/WSI_no_xml/")

d2 = models.Dataset(name="Colorectal cancer trials", directory="/Users/ysbecca/ysbecca-projects/iciar-2018/data/WSI_no_xml/")

i1 = models.Image(file_name="01.svs", file_dir="/Users/ysbecca/ysbecca-projects/iciar-2018/data/WSI_no_xml/", dataset_id=1)
i2 = models.Image(file_name="02.svs", file_dir="/Users/ysbecca/ysbecca-projects/iciar-2018/data/WSI_no_xml/", dataset_id=1)
i3 = models.Image(file_name="03.svs", file_dir="/Users/ysbecca/ysbecca-projects/iciar-2018/data/WSI_no_xml/", dataset_id=1)

s1 = models.Study(name="Colorectal tumour segmentation", description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras in lacus malesuada, ornare quam sed, suscipit urna. Nunc scelerisque varius nisi eget ornare. Fusce ut blandit ipsum. Nullam posuere faucibus sapien, sed dignissim eros viverra lobortis. Aenean in tincidunt augue. Sed sagittis orci in eleifend viverra. Etiam ultricies nunc neque, eget rhoncus sapien ornare et. Etiam eget odio mattis, hendrerit lacus ut, sollicitudin turpis.", dataset_id=1)

db.session.add(d1)
db.session.add(d2)
db.session.add(i1)
db.session.add(i2)
db.session.add(i3)
db.session.add(s1)

print("Committing now...")

db.session.commit()