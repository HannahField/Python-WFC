import imageio
import pathlib
import os
import csv

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

class TileSet:
    def __init__(self,tilesetname:str) -> None:
        self.tileset = dict()
        
        with open(pathlib.Path(os.path.join(CURRENT_DIR,"TileSets",tilesetname,"rules.txt")),newline="\n") as file:
            rules = list(csv.reader(file,delimiter=","))
        
        for tile in rules:
            image_data = TileSet.load_image_data(os.path.join(CURRENT_DIR,"TileSets",tilesetname,tile[0]+".bmp"))
            self.tileset[tile[0]] = Tile(image_data,tile[1],tile[2],tile[3],tile[4],tile[0])
    def load_image_data(file):
        image_data = imageio.v3.imread(file)
        return image_data

class Tile:
    def __init__(self, image_data,north_socket,east_socket,south_socket,west_socket,ID) -> None:
        self.image_data = image_data
        self.north_socket = north_socket
        self.east_socket = east_socket
        self.south_socket = south_socket
        self.west_socket = west_socket
        self.ID = ID
