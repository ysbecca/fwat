from app import db


class WSI(db.Model):
	id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), index=True, unique=True)
    file_dir = db.Column(db.String(100))
    

    def generate_deep_zoom(self):
    	# Move backend work from the view to here
    	slide = open_slide(file_dir + file_name) 
		tiles = DeepZoomGenerator(slide, tile_size=tile_size, overlap=overlap, limit_bounds=exclude_background)