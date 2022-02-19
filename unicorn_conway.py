# Conway's Game of Life on Pimoroni's Pico Unicorn Pack
#
# based on and extended from on Steve Baine's post for Pico Unicorn pack on
# https://forums.pimoroni.com/t/pico-unicorn-pack-not-working-in-micropython/15997
#
# Button B reseeds Conway.
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

    def populated(self):
        return sum([sum(c) for c in self.cells]) > 0

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
                    
    def copy(self, fromCells):
        for x in range(w):
            for y in range(h):
                self.cells[x][y] = fromCells.cells[x][y]


def GenerateColours():
    '''To be honest, the settings here are quite subjective'''
    lux = 300
    maxrandint = 200
    
    '''generate random colours'''
    cols_rgb = [random.randint(m,min(maxrandint,255)) for m in [100,20,0]]
    
    '''
    scaling colours by proportion to a standardised brightness 
    then constraining them to max of 255
    '''
    cols_rgb_new = [ min(int(lux*x/sum(cols_rgb)),255) for x in cols_rgb]
    return cols_rgb_new


def ExportToLeds(cells, cols_rgb):
    for x in range(w):
        for y in range(h):
            value = cells[x][y]
            r, g, b = [value*c for c in cols_rgb]
            uni.set_pixel(x,y,r,g,b)


def StandardLeds(pix):
    
    def Clear():
        [uni.set_pixel_value(x,y,0) for x in range(w) for y in range(h)]
    
    '''clear screen'''
    Clear()
    utime.sleep_ms(int(timeStep//4)) # find quotient from division
    
    '''select image type for display'''
    if pix == "stable":
        [uni.set_pixel(x,y,5,30,2) for x in range(w) for y in range(h)]
        
    if pix == "extinct":
        [uni.set_pixel_value(x,y,75) for x in range(w) for y in range(1, h-1)]
        utime.sleep_ms(timeStep*2)
        Clear()
        [uni.set_pixel_value(x,y,50) for x in range(w) for y in range(2, h-2)]
        utime.sleep_ms(timeStep*2)
        Clear()
        [uni.set_pixel_value(x,3,25) for x in range(w)]
        
    if pix == "nuked":
        [uni.set_pixel(x,y,80,10,5) for x in range(w) for y in range(h)]
        
    if pix == "goodbye":
        [uni.set_pixel_value(x,3,25) for x in range(w)]
        [uni.set_pixel_value(8,y,25) for y in range(h)]
        
    ''' pause image '''
    utime.sleep_ms(timeStep*5)


def StandardActions(action):
    
    if action in ["extinct", "nuked", "stable"]:
        StandardLeds(action)
        counter = 0
        start = True
        return counter, start
    
    if action == "goodbye":
        StandardLeds(action)
        running = False
        return running
    
    
def IterateCells(cellsA, cellsB, cellsC):
    cellsC.copy(cellsB)
    cellsB.iterate_from(cellsA)
    (cellsA, cellsB) = (cellsB, cellsA)
    return cellsA, cellsB, cellsC


cellsA = Cells()
cellsB = Cells()
cellsC = Cells()
running = True
start = True
counter = 0
timeStep = int(150)
oscillationCounts = 6



while running:
    if start:
        cellsA.clear_all()
        cellsA.set_random_cells_to_life(0.2)
        rgb = GenerateColours()
        start = False
    
    ExportToLeds(cellsA.cells, rgb)
    utime.sleep_ms(timeStep)
    
    '''
    If cells are stable, clear board then reseed board.
    If all cells are dead, reseed board.
    '''
    
    # Cells are stable and static
    if cellsA.cells == cellsB.cells:
        utime.sleep_ms(timeStep*2)
        counter, start = StandardActions('stable')
    
    # Cells are in stable oscillation
    elif cellsA.cells == cellsC.cells:
        counter += 1
        # break out of iteration after n repeats
        if counter == oscillationCounts:
            counter, start = StandardActions('stable')
        else:
            cellsA, cellsB, cellsC = IterateCells(cellsA, cellsB, cellsC)
            
    
    # At least one cell is alive
    elif cellsA.populated():
        cellsA, cellsB, cellsC = IterateCells(cellsA, cellsB, cellsC)
        
        
    # All cells are dead 
    else:
        counter, start = StandardActions('extinct')
    
    '''
    Use button B to reset board.
    '''
    if uni.is_pressed(uni.BUTTON_B):
        counter, start = StandardActions('nuked')
        
    '''
    Use button X to halt programme
    '''
    if uni.is_pressed(uni.BUTTON_X):
        running = StandardActions('goodbye')
