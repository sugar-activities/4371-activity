# g.py - globals
import pygame,utils,grid

app='Boxes'; ver='1.0'
ver='1.1'
# developed on SoaS - removed cursor on/off stuff
# fixed journal stuff
ver='1.2'
# fixed screen resizing - now allows for fact XO is NOT 4:3
ver='1.3'
# shorter version message
ver='1.4'
# hot area on edges reduced along length
# pause b4 drawing new box - pause decreases as box count increase
# grid.easy() = boxes ready to complete with glow clue until 3 wins
# non-turn greyed out
# wizard moves initially slower
ver='1.5'
# round ends @ 13
# try smoothscale
# speeds up after 5 wins
# players faded unless playing
ver='1.6'
# faded players images improved
ver='1.7'
# just one easy box
ver='1.8'
# app title added
ver='3.0'
# uses redraw = changed draw() and added update() in grid.py
# reworked easy setup so flash doesn't end up on finished box
ver='3.1'
# removed debug save to screen.dmp
ver='4.0'
# new sugar cursor etc
ver='4.1'
# repositioned new button
ver='21'
# bug fix for glow between 2 filled in boxes
ver='22'
# flush_queue() doesn't use gtk on non-XO

UP=(264,273)
DOWN=(258,274)
LEFT=(260,276)
RIGHT=(262,275)
CROSS=(259,120)
CIRCLE=(265,111)
SQUARE=(263,32)
TICK=(257,13)

def init(): # called by run()
    global redraw
    global screen,w,h,font1,font2,clock
    global factor,offset,imgf,message,version_display
    global pos,pointer
    redraw=True
    version_display=False
    screen = pygame.display.get_surface()
    pygame.display.set_caption(app)
    screen.fill((70,0,70))
    pygame.display.flip()
    w,h=screen.get_size()
    if float(w)/float(h)>1.5: #widescreen
        offset=(w-4*h/3)/2 # we assume 4:3 - centre on widescreen
    else:
        h=int(.75*w) # allow for toolbar - works to 4:3
        offset=0
    clock=pygame.time.Clock()
    factor=float(h)/24 # measurement scaling factor (32x24 = design units)
    imgf=float(h)/900 # image scaling factor - all images built for 1200x900
    if pygame.font:
        t=int(144*imgf); font1=pygame.font.Font(None,t)
        t=int(96*imgf); font2=pygame.font.Font(None,t)
    message=''
    pos=pygame.mouse.get_pos()
    pointer=utils.load_image('pointer.png',True)
    pygame.mouse.set_visible(False)
    
    # this activity only
    global wizard,xo,won,lost,x0,y0,dd,ww,sq,grid_img,grid,current,state
    global magician,xo2,magician_grey,xo2_grey,glow_h,glow_v,yes,no,result
    # (x0,y0) top left of grid
    dd=sy(3.76); ww=sy(.24) # line width
    x0=sx(16)-2.5*dd-ww/2; y0=sy(1.5)
    won=0; lost=0
    wizard=utils.load_image('wizard.png',True)
    xo=utils.load_image('xo.png',True)
    xo2=utils.load_image('xo2.png',True)
    magician_grey=utils.load_image('magician_grey.png',True)
    xo2_grey=utils.load_image('xo2_grey.png',True)
    magician=utils.load_image('magician.png',True)
    sq=utils.load_image('sq.png',True)
    grid_img=utils.load_image('grid.png',True)
    glow_h=utils.load_image('glow_h.png',True)
    glow_v=utils.load_image('glow_v.png',True)
    yes=utils.load_image('yes.png',True)
    no=utils.load_image('no.png',True)
    result=None
    grid=grid.Grid()
    current=1 # 1=player 2=PC
    state=0
    # 0 setting up - drawing selected edges
    # 1 player click
    # 2 wizard click
    # 3 game over - awaiting button

def sx(f): # scale x function
    return f*factor+offset

def sy(f): # scale y function
    return f*factor

