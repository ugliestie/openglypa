from io import BytesIO

from .MemeFactory import MemeFactory, MemeLib
from .MemeLibJsonDecoder import generate_meme_dict


def get_meme_factory(template, args):
    return MemeFactory.factory_from_template(template, args)


def get_meme_image(template, args):
    img = get_meme_factory(template, args).output_image

    byte_io = BytesIO()

    if img is 'JpegImageFile':
        byte_io.name = 'image.jpg'
        
        img.save(byte_io, 'JPEG')
        byte_io.seek(0)

        return byte_io.read()
    else:
        byte_io.name = 'image.gif'
        
        img.save(byte_io, 'GIF')
        byte_io.seek(0)

        return byte_io.read()

        

def add_external_resource_dir(resource_path):
    try:
        meme_dict = generate_meme_dict(resource_path)
        for i in meme_dict:
            MemeLib[i] = meme_dict[i]
    except FileNotFoundError as e:
        error_message = "Could not identify external resource directory.\n" + str(e)
        print(error_message)