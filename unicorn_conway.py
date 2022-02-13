# Perpetual Conway's Game of Life on pimoroni's Pico Unicorn Pack
#
# based on Steve Baine's post for Pico Unicorn pack on
# https://forums.pimoroni.com/t/pico-unicorn-pack-not-working-in-micropython/15997
# note that the picounicorn module comes from pimoroni's custom MicroPython uf2
#
# Button Y reseeds Conway.
# Button X exits loop and halts programme.

import picounicorn as uni
import random
import utime

uni.init()

w = uni.get_width()
h = uni.get_height()

class Cells:
    def __init__(self):
        self.cells = [[0]*h for i in range(w)]

    def clear_all(self):
        for x in range(w):
            for y in range(h):
                self.cells[x][y] = 0

    def set_random_cells_to_life(self, prob):
        for x in range(w):
            for y in range(h):
                if random.random() < prob:
                    self.cells[x][y] = 1

    def is_alive(self,x,y):
        x = x % w
        y = y % h
        return self.cells[x][y] == 1

    def get_num_live_neighbours(self, x, y):
        num = 0
        num += (1 if self.is_alive(x-1,y-1) else 0)
        num += (1 if self.is_alive(x  ,y-1) else 0)
        num += (1 if self.is_alive(x+1,y-1) else 0)
        num += (1 if self.is_alive(x-1,y) else 0)
        num += (1 if self.is_alive(x+1,y) else 0)
        num += (1 if self.is_alive(x-1,y+1) else 0)
        num += (1 if self.is_alive(x  ,y+1) else 0)
        num += (1 if self.is_alive(x+1,y+1) else 0)
        return num
        
    def iterate_from(self, fromCells):
        for x in range(w):
            for y in range(h):
                num_live_nbrs = fromCells.get_num_live_neighbours(x,y)
                is_alive = fromCells.is_alive(x,y)
                if is_alive and (num_live_nbrs < 2 or num_live_nbrs > 3):
                    self.cells[x][y] = 0 # Died
                elif not is_alive and num_live_nbrs == 3:
                    self.cells[x][y] = 1 # Born
                else:
                    self.cells[x][y] = fromCells.cells[x][y] # Unchanged state

def ExportToLeds(cells, cols_rgb):
    for x in range(w):
        for y in range(h):
            value = cells[x][y]
            r, g, b = [value*c for c in cols_rgb]
            uni.set_pixel(x,y,r,g,b)

cellsA = Cells()
cellsB = Cells()
running = True
start = True


while running:
    if start:
        cellsA.clear_all()
        cellsA.set_random_cells_to_life(0.2)
        rgb = [random.randint(m,255) for m in [100, 20, 0]]
        start = False
    
    ExportToLeds(cellsA.cells, rgb)
    utime.sleep_ms(200)
    
    '''
    If cells are stable, clear board and reseed cells.
    If all cells are dead, reseed cells.
    '''
    if cellsA.cells == cellsB.cells:
        utime.sleep_ms(400)
        cellsA.clear_all()
        ExportToLeds(cellsA.cells,rgb)
        [uni.set_pixel_value(8,n,130) for n in range(h) ]
        utime.sleep_ms(400)
        start = True
    
    elif sum([sum(c) for c in cellsA.cells]):    
        cellsB.iterate_from(cellsA)
        (cellsA, cellsB) = (cellsB, cellsA)
    
    else:
        [uni.set_pixel_value(n,3,130) for n in range(w) ]
        utime.sleep_ms(400)
        start = True
    
    '''
    Use button Y to reset cells
    '''
    if uni.is_pressed(uni.BUTTON_Y):
        cellsA.clear_all()
        ExportToLeds(cellsA.cells, rgb)
        
    '''
    Use button X to halt programme
    '''
    if uni.is_pressed(uni.BUTTON_X):
        cellsA.clear_all()
        ExportToLeds(cellsA.cells, rgb)
        [uni.set_pixel_value(n,3,25) for n in range(w) ]
        [uni.set_pixel_value(8,n,25) for n in range(h) ]
        running = False
