import imghdr
from PIL import Image

class ThumbnailGenerator(object):
    
    def __init__(self, geom = (100,100)):

        self.geom = geom

    def generate(self, image_path):
        """
        Given the image, produces a thumbnail, saves with a random name in the
        thumbnail directory, and returns the name
        """
        return 'foo'

#         im = Image.open(image_path)
#         im.thumbnail(self.geom)
#         base, ext = os.path.splitext(path)
#         im.save(thumbnail_path, imghdr.what(image_path))

    def update(self, image_path, thumbnail_path):
        pass

    def delete(self, thumbnail_path):
        pass
