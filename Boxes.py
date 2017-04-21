#!/usr/bin/python
# Boxes.py
"""
    Copyright (C) 2010  Peter Hewitt

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

"""
import g,utils,pygame,buttons,sys,random,load_save
try:
    import gtk
except:
    pass

class Boxes:
    
    def __init__(self):
        self.journal=True # set to False if we come in via main()
        self.canvas=None # set to the pygame canvas if we come in via activity.py

    def display(self):
        g.screen.fill((220,64,64))
        g.grid.draw()
        buttons.draw()
        x=5
        cy=g.sy(3); np=g.grid.counts[1]; nw=g.grid.counts[2]
        if nw>0: utils.display_number(nw,(g.sx(x),cy),g.font2,utils.ORANGE)
        if np>0: utils.display_number(np,(g.sx(32-x),cy),g.font2,utils.CYAN)
        x=3.3
        cy=g.sy(13.2)
        if g.lost>0: utils.display_number(g.lost,(g.sx(x),cy),g.font1)
        cy=g.sy(14.6)
        if g.won>0: utils.display_number(g.won,(g.sx(32-x),cy),g.font1)
        cy=g.sy(18.7)
        img=g.magician
        if g.state!=2: img=g.magician_grey
        utils.centre_blit(g.screen,img,(g.sx(x),cy))
        img=g.xo2
        if g.state!=1: img=g.xo2_grey
        utils.centre_blit(g.screen,img,(g.sx(32-x),cy))
        cy=g.sy(9)
        if g.result != None: # smiley
            utils.centre_blit(g.screen,g.result,(g.sx(32-x),cy))

    def do_key(self,key):
        if key in g.SQUARE: g.state=0; g.grid.setup(); buttons.off("cyan"); return
        if key==pygame.K_v: g.version_display=not g.version_display; return

    def grid(self): # only for setting up original grid
        g.screen.fill((0,0,0))
        y=g.y0
        for r in range(5):
            x=g.x0
            for c in range(5):
                utils.centre_blit(g.screen,g.sq,(x,y))
                x=x+g.dd
            y=y+g.dd

    def click(self):
        if g.state==1:
            if g.grid.click(): return True
        return False

    def process(self):
        if g.state==0:
            g.grid.start()
        if g.state==1:
            g.current=1
            if self.complete(): g.state=3
        if g.state==2:
            g.current=2; g.grid.wizard()
            if self.complete(): g.state=3
        if g.state==3:
            buttons.on("cyan")

    def complete(self):
        if g.grid.counts[1]>12:
            g.won+=1; self.won=g.won; g.result=g.yes
            return True
        if g.grid.counts[2]>12:
            g.lost+=1; self.lost=g.lost; g.result=g.no
            return True
        return False

    def flush_queue(self):
        flushing=True
        while flushing:
            flushing=False
            if self.journal:
                while gtk.events_pending(): gtk.main_iteration()
            for event in pygame.event.get(): flushing=True
        
    def run(self):
        g.init()
        if not self.journal: utils.load()
        g.grid.setup()
        load_save.retrieve()
        bx=g.sx(3.3); by=g.sy(9)
        buttons.Button("cyan",(bx,by),True); buttons.off("cyan")
        if self.canvas<>None: self.canvas.grab_focus()
        ctrl=False
        pygame.key.set_repeat(600,120); key_ms=pygame.time.get_ticks()
        going=True
        while going:
            if self.journal:
                # Pump GTK messages.
                while gtk.events_pending(): gtk.main_iteration()

            # Pump PyGame messages.
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    if not self.journal: utils.save()
                    going=False
                elif event.type == pygame.MOUSEMOTION:
                    g.pos=event.pos
                    g.redraw=True
                    if self.canvas<>None: self.canvas.grab_focus()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    g.redraw=True
                    if event.button==1:
                        if self.click(): self.flush_queue(); break
                        bu=buttons.check()
                        if bu<>'':
                            g.result=None
                            g.state=0; g.grid.setup()
                            buttons.off("cyan"); self.flush_queue(); break
                elif event.type == pygame.KEYDOWN:
                    # throttle keyboard repeat
                    if pygame.time.get_ticks()-key_ms>110:
                        key_ms=pygame.time.get_ticks()
                        if ctrl:
                            if event.key==pygame.K_q:
                                if not self.journal: utils.save()
                                going=False; break
                            else:
                                ctrl=False
                        if event.key in (pygame.K_LCTRL,pygame.K_RCTRL):
                            ctrl=True; break
                        self.do_key(event.key); g.redraw=True
                        self.flush_queue()
                elif event.type == pygame.KEYUP:
                    ctrl=False
            if not going: break
            self.process()
            g.grid.update()
            if g.redraw:
                self.display()
                if g.version_display: utils.version_display()
                g.screen.blit(g.pointer,g.pos)
                pygame.display.flip()
                g.redraw=False
            g.clock.tick(40)

if __name__=="__main__":
    pygame.init()
    pygame.display.set_mode((1024,768),pygame.FULLSCREEN)
    game=Boxes()
    game.journal=False
    game.run()
    pygame.display.quit()
    pygame.quit()
    sys.exit(0)
