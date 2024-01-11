import imageio
import pathlib
import os
import csv
from copy import deepcopy

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

def flatten(array_of_array):
    return [x for array in array_of_array for x in array]

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

class TileSuperposition:
    def __init__(self,tileset:TileSet) -> None:
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
    
    def get_sockets_in_direction(self,direction:str):
        match direction:
            case "north":
                return set([x.north_socket for x in self.possible_tiles.values()])
            case "east":
                return set([x.east_socket for x in self.possible_tiles.values()])
            case "south":
                return set([x.south_socket for x in self.possible_tiles.values()])
            case "west":
                return set([x.west_socket for x in self.possible_tiles.values()])

    def propagate(self,direction:str):
        number_of_possible_tiles = self.number_of_possible_tiles()
        propagator = None
        match direction:
            case "north":
                propagator = self.south_neightbor
                possible_sockets = propagator.get_sockets_in_direction("north")
                self.possible_tiles = dict([ (k,v) for k,v in self.possible_tiles.items() if v.south_socket in possible_sockets])
            case "east":
                propagator = self.west_neightbor
                possible_sockets = propagator.get_sockets_in_direction("east")
                self.possible_tiles = dict([ (k,v) for k,v in self.possible_tiles.items() if v.west_socket in possible_sockets])
            case "south":
                propagator = self.north_neightbor
                possible_sockets = propagator.get_sockets_in_direction("south")
                self.possible_tiles = dict([ (k,v) for k,v in self.possible_tiles.items() if v.north_socket in possible_sockets])
            case "west":
                propagator = self.east_neightbor
                possible_sockets = propagator.get_sockets_in_direction("west")
                self.possible_tiles = dict([ (k,v) for k,v in self.possible_tiles.items() if v.east_socket in possible_sockets])
        if number_of_possible_tiles != len(self.possible_tiles):
            self.propagate_to_existing_neighbors()
            
    def collapse(self):
        self.possible_tiles = dict([self.possible_tiles.popitem()])
        self.propagate_to_existing_neighbors()
    
            

class Grid:
    def __init__(self,width:int,height:int,tileset:TileSet) -> None:
        self.grid = [ [ TileSuperposition(tileset) for y in range( height ) ] for x in range( width ) ]
        for y in range(height):
            for x in range(width):
                current_tile = self.grid[x][y]
                if y != 0:
                    current_tile.north_neightbor = self.grid[x][y-1]
                if x != width-1:
                    current_tile.east_neightbor = self.grid[x+1][y]
                if y != height-1:
                    current_tile.south_neightbor = self.grid[x][y+1]
                if x != 0:
                    current_tile.west_neightbor = self.grid[x-1][y]
    
    def collapse_min_cell(self):
        flat_grid = flatten(self.grid)
        filtered_grid = [tilesuperposition for tilesuperposition in flat_grid if not tilesuperposition.collapsed()]
        min(filtered_grid,key=lambda x: x.number_of_possible_tiles()).collapse()
                
    def collapsed(self):
        return all([x.collapsed() for x in flatten(self.grid)])

    

    
    


tileset = TileSet("pipes")
a = TileSuperposition(tileset)

grid = Grid(3,3,tileset)


print([[y.number_of_possible_tiles() for y in x] for x in grid.grid])
grid.collapse_min_cell()
print([[y.number_of_possible_tiles() for y in x] for x in grid.grid])
grid.collapse_min_cell()
print([[y.number_of_possible_tiles() for y in x] for x in grid.grid])
grid.collapse_min_cell()
print([[y.number_of_possible_tiles() for y in x] for x in grid.grid])
grid.collapse_min_cell()
print([[y.number_of_possible_tiles() for y in x] for x in grid.grid])
grid.collapse_min_cell()
print(grid.collapsed())
print([[y.number_of_possible_tiles() for y in x] for x in grid.grid])
grid.collapse_min_cell()
print([[y.number_of_possible_tiles() for y in x] for x in grid.grid])
grid.collapse_min_cell()
print([[y.number_of_possible_tiles() for y in x] for x in grid.grid])
grid.collapse_min_cell()
print([[y.number_of_possible_tiles() for y in x] for x in grid.grid])
grid.collapse_min_cell()
print([[y.number_of_possible_tiles() for y in x] for x in grid.grid])
print(grid.collapsed())