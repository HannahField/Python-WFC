import imageio
import pathlib

def load_all_images_in_folder(folder:str) -> dict:
    images = dict()
    for file in pathlib.Path("tiles/").iterdir():
        if file.is_file() and file.suffix == ".bmp":
            images[file.stem] = imageio.v3.imread(file)
    return images

