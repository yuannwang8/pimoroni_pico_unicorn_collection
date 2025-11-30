# Conway's Game of Life on Pimoroni's Pico Unicorn Pack
# Now with random spontaneous popups!
# 
# extended from on Steve Baine's post for Pico Unicorn pack on
# https://forums.pimoroni.com/t/pico-unicorn-pack-not-working-in-micropython/15997
#
# Button B reseeds Conway.
# Button X exits loop and halts programme.
#
# updated to Micropython 1.25.0

#import picounicorn as uni
import random
import utime
from picounicorn import PicoUnicorn

#uni.init()
uni = PicoUnicorn()

class Cells:
    def __init__(self):
        self.cells = [[[0,0,0,0] for y in range(h)] for x in range(w)]
        
    def __str__(self):
        return '\n'.join(
            ' '.join(
                self.draw_cell(x, y) for x in range(w)
            )
            for y in range(h)
        )
    
    def draw_cell(self,x,y):
        return str(self.cells[x][y])

    def clear_all(self):
        self.cells = [[[0,0,0,0] for y in range(h)] for x in range(w)]

    def populated(self):
        num = 0
        for x in range(w):
            for y in range(h):
                num += self.cells[x][y][0]
        return num > 0

    def birth(self, x, y, prob, cols_rgb):
        num = random.random()
        if num < prob:
            self.cells[x][y][0] = 1
            self.cells[x][y][1::] = cols_rgb
            
    def GenerateColours(self):
        '''To be honest, the settings here are quite subjective'''
        lux = 300
        maxrandint = 220
        
        '''generate random colours'''
        cols_rgb = [random.randint(m,min(maxrandint,255)) for m in [100,20,0]]
        
        '''
        scaling colours by proportion to a standardised brightness 
        then constraining them to max of 255
        '''
        cols_rgb_new = [ min(int(lux*x/sum(cols_rgb)),255) for x in cols_rgb]
        return cols_rgb_new

    def set_random_cells_to_life(self, prob):
        cols_rgb = self.GenerateColours()
        [[ self.birth(x, y, prob, cols_rgb) for y in range(h) ] for x in range(w)]
                
    def is_alive(self,x,y):
        x = x % w
        y = y % h
        return self.cells[x][y]
    
    def get_num_live_neighbours(self, x, y):
        num, r, g, b = 0, 0, 0, 0
        def add_attributes(x, y):
            num1, r1, g1, b1 = self.is_alive(x,y)
            return num + num1, r + r1, g + g1, b + b1

        num, r, g, b = add_attributes(x-1,y-1)
        num, r, g, b = add_attributes(x  ,y-1)
        num, r, g, b = add_attributes(x+1,y-1)
        num, r, g, b = add_attributes(x-1,y)
        num, r, g, b = add_attributes(x+1,y)
        num, r, g, b = add_attributes(x-1,y+1)
        num, r, g, b = add_attributes(x  ,y+1)
        num, r, g, b = add_attributes(x+1,y+1)

        if num:
            r = min(int(r/num),255)
            g = min(int(g/num),255)
            b = min(int(b/num),255)
        
        return num, r, g, b
        
    def iterate_from(self, fromCells, prob):
        cols_rgb = self.GenerateColours()
        for x in range(w):
            for y in range(h):
                num_live_nbrs, r, g, b = fromCells.get_num_live_neighbours(x,y)
                is_alive = fromCells.is_alive(x,y)[0]
                if is_alive and (num_live_nbrs < 2 or num_live_nbrs > 3):
                    self.cells[x][y] = [0,0,0,0] # Died
                elif not is_alive and num_live_nbrs == 3:
                    self.cells[x][y] = [1,r,g,b] # Born with average colours from parent neighbours
                else:
                    self.cells[x][y] = fromCells.cells[x][y] # Unchanged state
                    ## random creaton from vacuum
                    if not self.cells[x][y][0]:
                        self.birth(x, y, prob, cols_rgb)
                    
    def copy(self, fromCells):
        for x in range(w):
            for y in range(h):
                self.cells[x][y] = fromCells.cells[x][y]


def IterateCells(cells1, cells2, cells3, prob):
    cells3.copy(cells2)
    cells2.iterate_from(cells1, prob)
    (cells1, cells2) = (cells2, cells1)
    if printToConsole:
        print(cells1)
        print('--'*w)
    return cells1, cells2, cells3



def ExportToLeds(cells):
    for x in range(w):
        for y in range(h):
            uni.set_pixel(x,y,cells[x][y][1],cells[x][y][2],cells[x][y][3])

    
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
    
    global counter
    global start
    global running
    
    if printToConsole:
        print(action)
    
    if action in ["extinct", "nuked", "stable"]:
        StandardLeds(action)
        counter = 0
        start = True
    
    if action == "goodbye":
        StandardLeds(action)
        running = False


'''Set-up'''
w = uni.get_width()
h = uni.get_height()
running = True
start = True
counter = 0
cellsA = Cells()
cellsB = Cells()
cellsC = Cells()



'''User Settings'''
timeStep = int(100) # in milliseconds
oscillationCounts = 6
printToConsole = False
probs = 0.2
mutate = 20
# divide probs by this for the probability of spontaneous mutation


try:
    while running:
        if start:
            cellsA.clear_all()
            cellsA.set_random_cells_to_life(probs)
            if printToConsole:
                print(cellsA)
                print('-=-'*w)
            start = False
        
        ExportToLeds(cellsA.cells)
        utime.sleep_ms(timeStep)
        
        
        '''
        If cells are stable, clear board then reseed board.
        If all cells are dead, reseed board.
        '''
        
        # Cells are stable and static
        if cellsA.cells == cellsB.cells:
            utime.sleep_ms(timeStep*2)
            StandardActions('stable')
        
        # Cells are in stable oscillation
        elif cellsA.cells == cellsC.cells:
            counter += 1
            # break out of iteration after n repeats
            if counter == oscillationCounts:
                StandardActions('stable')
            else:
                cellsA, cellsB, cellsC = IterateCells(cellsA, cellsB, cellsC, probs/mutate)
                
        # At least one cell is alive
        elif cellsA.populated():
            cellsA, cellsB, cellsC = IterateCells(cellsA, cellsB, cellsC, probs/mutate)
            
        # All cells are dead 
        else:
            StandardActions('extinct')
            
        '''
        Use button B to reset board.
        '''
        if uni.is_pressed(uni.BUTTON_B):
            StandardActions('nuked')
            
        '''
        Use button X to halt programme
        '''
        if uni.is_pressed(uni.BUTTON_X):
            StandardActions('goodbye')
            
        
except KeyboardInterrupt:
    print('bye')
    
