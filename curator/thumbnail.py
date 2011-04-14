import imghdr
from PIL import Image

class ThumbnailGenerator:
    
    def __init__(self, geom = (100,100)):

        self.geom = geom

    def generate(self, image_path, thumbnail_path):
        im = Image.open(image_path)
        im.thumbnail(self.geom)
        base, ext = os.path.splitext(path)
        im.save(thumbnail_path, imghdr.what(image_path))

    def update(self, image_path, thumbnail_path):
        pass

    def delete(self, thumbnail_path):
        pass
