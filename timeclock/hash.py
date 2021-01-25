from PIL import Image
from imagehash import average_hash()

def hashImage(image):
    return average_hash(Image.open(image), hashsize=64)
    
def check_image_hash(realHash, image):
    return -5 < realHash - hashImage(image) < 5
