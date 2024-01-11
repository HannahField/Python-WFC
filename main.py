import imageio
import pathlib
import os
import csv
import numpy as np
from random import choice
from copy import deepcopy
from pprint import pprint

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


def flatten(array_of_array):
    return [x for array in array_of_array for x in array]

def is_valid_tileset(tileset: str):
    return os.path.exists(os.path.join(CURRENT_DIR, "TileSets", tileset))

def parse_dimensions(dimensions: str):
    split_dims = dimensions.split(",")
    if not len(split_dims) == 2:
        return None
    (x, y) = [int_try_parse(x.strip()) for x in split_dims]
    if x is None or y is None:
        return None
    return (x, y)

def int_try_parse(string: str):
    try:
        return int(string)
    except ValueError:
        return None

class TileSet:
    def __init__(self, tilesetname: str, extension) -> None:
        self.tileset = dict()

        with open(
            pathlib.Path(os.path.join(CURRENT_DIR, "TileSets", tilesetname, "rules.txt")), newline="\n",) as file:
            rules = list(csv.reader(file, delimiter=","))

        for tile in rules:
            image_data = TileSet.load_image_data(
                os.path.join(CURRENT_DIR, "TileSets", tilesetname, tile[0] + extension)
            )
            self.tileset[tile[0]] = Tile(image_data, tile[1], tile[2], tile[3], tile[4], tile[0])

    def load_image_data(file):
        image_data = imageio.v3.imread(file)
        return image_data

class Tile:
    def __init__(
        self, image_data, north_socket, east_socket, south_socket, west_socket, ID
    ) -> None:
        self.image_data = image_data
        self.north_socket = north_socket
        self.east_socket = east_socket
        self.south_socket = south_socket
        self.west_socket = west_socket
        self.ID = ID

class TileSuperposition:
    def __init__(self, tileset: TileSet) -> None:
        self.possible_tiles = deepcopy(tileset.tileset)
        self.north_neightbor = None
        self.east_neightbor = None
        self.south_neightbor = None
        self.west_neightbor = None

    def number_of_possible_tiles(self):
        return len(self.possible_tiles)

    def collapsed(self):
        return self.number_of_possible_tiles() == 1

    def propagate_to_existing_neighbors(self):
        self.north_neightbor.propagate("north") if self.north_neightbor is not None else None
        self.east_neightbor.propagate("east") if self.east_neightbor is not None else None
        self.south_neightbor.propagate("south") if self.south_neightbor is not None else None
        self.west_neightbor.propagate("west") if self.west_neightbor is not None else None

    def get_sockets_in_direction(self, direction: str):
        match direction:
            case "north":
                return set([x.north_socket for x in self.possible_tiles.values()])
            case "east":
                return set([x.east_socket for x in self.possible_tiles.values()])
            case "south":
                return set([x.south_socket for x in self.possible_tiles.values()])
            case "west":
                return set([x.west_socket for x in self.possible_tiles.values()])

    def propagate(self, direction: str):
        number_of_possible_tiles = self.number_of_possible_tiles()
        propagator = None
        match direction:
            case "north":
                propagator = self.south_neightbor
                possible_sockets = propagator.get_sockets_in_direction("north")
                self.possible_tiles = dict(
                    [(k, v) for k, v in self.possible_tiles.items() if v.south_socket in possible_sockets]
                )
            case "east":
                propagator = self.west_neightbor
                possible_sockets = propagator.get_sockets_in_direction("east")
                self.possible_tiles = dict(
                    [(k, v) for k, v in self.possible_tiles.items() if v.west_socket in possible_sockets]
                )
            case "south":
                propagator = self.north_neightbor
                possible_sockets = propagator.get_sockets_in_direction("south")
                self.possible_tiles = dict(
                    [(k, v) for k, v in self.possible_tiles.items() if v.north_socket in possible_sockets]
                )
            case "west":
                propagator = self.east_neightbor
                possible_sockets = propagator.get_sockets_in_direction("west")
                self.possible_tiles = dict(
                    [(k, v) for k, v in self.possible_tiles.items() if v.east_socket in possible_sockets]
                )
        if number_of_possible_tiles != len(self.possible_tiles):
            self.propagate_to_existing_neighbors()

    def collapse(self):
        random_tile = choice(list(self.possible_tiles.values()))
        self.possible_tiles = dict([(random_tile.ID, random_tile)])
        self.propagate_to_existing_neighbors()


class Grid:
    def __init__(self, width: int, height: int, tileset: TileSet) -> None:
        self.width = width
        self.height = height
        self.grid = [
            [TileSuperposition(tileset) for y in range(height)] for x in range(width)
        ]
        for y in range(height):
            for x in range(width):
                current_tile = self.grid[x][y]
                if y != 0:
                    current_tile.north_neightbor = self.grid[x][y - 1]
                if x != width - 1:
                    current_tile.east_neightbor = self.grid[x + 1][y]
                if y != height - 1:
                    current_tile.south_neightbor = self.grid[x][y + 1]
                if x != 0:
                    current_tile.west_neightbor = self.grid[x - 1][y]

    def collapse_min_cell(self):
        flat_grid = flatten(self.grid)
        filtered_grid = [tilesuperposition for tilesuperposition in flat_grid if not tilesuperposition.collapsed()]
        min(filtered_grid, key=lambda x: x.number_of_possible_tiles()).collapse()

    def collapsed(self):
        return all([x.collapsed() for x in flatten(self.grid)])

    def to_image(self):
        tile_image_width = len(list(self.grid[0][0].possible_tiles.values())[0].image_data[0])
        tile_image_height = len(list(self.grid[0][0].possible_tiles.values())[0].image_data)

        image_grid = np.ndarray(shape=(self.width*tile_image_width,self.height*tile_image_height,3),dtype="uint8")

        for h in range(self.height):
            for w in range(self.width):
                tile = list(self.grid[w][h].possible_tiles.values())[0]
                for y in range(tile_image_height):
                    for x in range(tile_image_width):
                        image_grid[(w * tile_image_width) + x][(h * tile_image_height) + y] = tile.image_data[y][x][range(3)]
        imageio.imwrite(os.path.join(CURRENT_DIR, "output.png"), image_grid)





def main():
    tilesetpath = input("What tileset should be used? It must be in the folder TileSets: ")
    while not is_valid_tileset(tilesetpath):
        tilesetpath = input("The given input is not a valid tileset. Check the TileSets directory for valid tilesets: ")
    extension = input("What file extension will you be using? ")
    size = input("What should the amount of tiles horizontally and vertically be? Please enter them in the format x,y: ")
    dimensions = parse_dimensions(size)
    while dimensions is None:
        size = input("Invalid dimensions, please enter two comma seperated integers: ")
        dimensions = parse_dimensions(size)
    tileset = TileSet(tilesetpath,extension)
    grid = Grid(dimensions[0], dimensions[1], tileset)

    while not grid.collapsed():
        grid.collapse_min_cell()
    grid.to_image()


if __name__ == "__main__":
    main()
