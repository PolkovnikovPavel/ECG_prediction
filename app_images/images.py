from PIL import Image, ImageTk
from data.functions import *


def get_image(name, w, h, mode=0):
    size = (w, h)
    if ':/' not in name:
        img = Image.open(f'app_images/{name}')
    else:
        img = Image.open(name)
    img = img.resize(size, Image.ANTIALIAS)

    if mode == 1:
        return ImageTk.PhotoImage(img), img
    return ImageTk.PhotoImage(img)
