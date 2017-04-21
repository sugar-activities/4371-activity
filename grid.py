# grid.py

import g,random,pygame,utils

GOLD,PURPLE=(255,217,115),(255,0,255)

# squares are numbered 0 to 24
# edges are numbered 0 to 59

class Edge:
    def __init__(self,x1,y1,x2,y2):
        self.x1=x1; self.y1=y1; self.x2=x2; self.y2=y2
        self.gold=False

class Square:
    def __init__(self,sq_edges,x,y):
        self.sq_edges=sq_edges # [N,S,W,E]
        self.owner=0 # owner=0, 1(player), 2(computer) g.current
        self.x=x; self.y=y

    def new_box(self):
        for edge in self.sq_edges:
            if not edge.gold: return False
        return True

    def golds(self):
        n=0
        for edge in self.sq_edges:
            if edge.gold: n+=1
        return n      

class Grid:
    def __init__(self):
        self.edges=[]; self.squares=[]; self.counts=[25,0,0]; self.last=None
        self.owners_save=[]; self.golds_save=[]; self.counts_save=[]
        self.new_square=None; self.new_square_ms=0
        self.edge_flash=None; self.glow=None
            
        # horizontal edges
        y=g.y0
        for r in range(6):
            x=g.x0
            for c in range(5):
                edge=Edge(x,y,x+g.dd+g.ww,y+g.ww)
                self.edges.append(edge)
                x=x+g.dd
            y=y+g.dd
        # vertical edges
        y=g.y0
        for r in range(5):
            x=g.x0
            for c in range(6):
                edge=Edge(x,y,x+g.ww,y+g.dd+g.ww)
                self.edges.append(edge)
                x=x+g.dd
            y=y+g.dd
        # squares
        s=0; y=g.y0+g.ww/2
        for r in range(5):
            x=g.x0+g.ww/2
            for c in range(5):
                t=r*6+30+c
                sq_edges=[]
                for n in [s,s+5,t,t+1]: sq_edges.append(self.edges[n])
                square=Square(sq_edges,x,y)
                self.squares.append(square)
                s+=1
                x=x+g.dd
            y=y+g.dd

    def setup(self):
        self.counts=[25,0,0]
        for square in self.squares:
            square.owner=0
        for edge in self.edges:
            edge.gold=False
        self.ms=pygame.time.get_ticks(); self.n=0; self.new_square=None
        self.easy_square=None

    def easy(self):
        g.current=1
        # find box with all edges empty
        ok=False
        for i in range(100):
            square=self.squares[random.randint(0,24)]
            if square.golds()==0: ok=True; break
        if not ok: return # give up
        ind2=random.randint(0,3)
        for i in range(4):
            hv='h'
            if ind2>1: hv='v'
            edge=square.sq_edges[ind2]; edge.gold=True
            self.edge_flash=edge
            ind2+=1
            if ind2==4: ind2=0
        self.edge_flash.gold=False
        self.glow=g.glow_h
        if hv=='v': self.glow=g.glow_v
            
    def start(self):
        d=pygame.time.get_ticks()-self.ms
        if self.n==0 or d<0 or d>50:
            g.redraw=True
            self.n+=1
            r=random.randint(0,59)
            if self.edges[r].gold: return #****
            self.edges[r].gold=True
            if self.check_boxes(True): self.edges[r].gold=False; return #****
            self.ms=pygame.time.get_ticks()
            if self.n>=20:
                g.state=1
                if g.won<4:
                    self.easy() # setup one easy with 3 edges gold
                    self.check_boxes()
                    if self.counts[1]==0: # make sure we have 1 filled in box
                        # find box with all edges empty
                        ok=False
                        for i in range(100):
                            square=self.squares[random.randint(0,24)]
                            if square.golds()==0: ok=True; break
                        if ok:
                            for ind in range(4):
                                edge=square.sq_edges[ind]
                                if edge!=self.edge_flash: edge.gold=True # v21
                        self.check_boxes()
        
    def draw(self):
        g.screen.blit(g.grid_img,(g.x0,g.y0))
        for edge in self.edges:
            if edge.gold:
                colour=GOLD
                if edge==self.last: colour=PURPLE
                pygame.draw.rect(\
                    g.screen,colour,\
                    (edge.x1,edge.y1,edge.x2-edge.x1,edge.y2-edge.y1))
        for square in self.squares:
            img=g.xo
            if square.owner==2: img=g.wizard
            if square.owner>0:
                if square!=self.new_square:
                    g.screen.blit(img,(square.x,square.y))
        if self.new_square==None:
            if self.edge_flash!=None and g.state==1:
                d=g.sy(.8); edge=self.edge_flash
                g.screen.blit(self.glow,(edge.x1-d,edge.y1-d))

    def click(self):
        n=0; d=g.sy(.5)
        for edge in self.edges:
            if not edge.gold:
                x1=edge.x1+d; y1=edge.y1-d; x2=edge.x2-d; y2=edge.y2+d
                if utils.mouse_in(x1,y1,x2,y2):
                    self.last=None
                    edge.gold=True; self.edge_flash=None
                    if not self.check_boxes():
                        self.ms=pygame.time.get_ticks()
                        g.state=2
                    return True
            n+=1;
            if n==30: d=-d
        return False

    def wizard(self):
        d=pygame.time.get_ticks()-self.ms
        ms=(80*self.counts[0])+800 # goes from 2800 to 800
        if g.won>5: ms=200
        if d<0 or d>ms:
            self.wizard_move()
            g.redraw=True
            self.ms=pygame.time.get_ticks()

    def wizard_move(self):
        self.last=None
        for edge in self.edges:
            if not edge.gold:
                edge.gold=True
                if self.check_boxes(): return
                edge.gold=False
        ind=random.randint(0,len(self.edges)-1)
        for i in range(60):
            edge=self.edges[ind]
            if not edge.gold:
                if not self.gift(edge):
                    edge.gold=True; g.state=1; self.last=edge; return
            ind+=1
            if ind==60: ind=0
        # have to give away
        min=1000
        for edge in self.edges:
            if not edge.gold:
                n=self.damage(edge)
                if n<min: min=n; best_edge=edge
        best_edge.gold=True; g.state=1; self.last=best_edge; return

    def check_boxes(self,test=False):
        found=False
        for square in self.squares:
            if square.owner==0:
                if square.new_box():
                    if test:
                        return True
                    else:
                        square.owner=g.current
                        self.new_square=square
                        self.new_square_ms=pygame.time.get_ticks()
                        self.counts[0]-=1
                        self.counts[g.current]+=1
                        found=True
        return found

    def gift(self,edge0):
        for square in self.squares:
            for edge in square.sq_edges:
                if edge==edge0:
                    if square.golds()==2: return True
                    break
        return False

    # how many squares will this edge give away?
    def damage(self,edge0):
        self.save()
        n1=self.counts[0]
        edge0.gold=True
        self.check_boxes()
        found=True
        while found and self.counts[0]>0:
            found=False
            for edge in self.edges:
                if not edge.gold:
                    edge.gold=True
                    if self.check_boxes(): found=True; break
                    edge.gold=False
        n2=self.counts[0]
        self.restore()
        return (n1-n2)

    def save(self):
        self.owners_save=[]
        for square in self.squares: self.owners_save.append(square.owner)
        self.golds_save=[]
        for edge in self.edges: self.golds_save.append(edge.gold)
        self.counts_save=utils.copy_list(self.counts)
        
    def restore(self):
        ind=0
        for square in self.squares: square.owner=self.owners_save[ind]; ind+=1
        ind=0
        for edge in self.edges: edge.gold=self.golds_save[ind]; ind+=1
        self.counts=utils.copy_list(self.counts_save)

    def update(self):
        if self.new_square<>None:
            ms=32*self.counts[0] # will go from 800 to 0
            if g.won>5: ms=50
            d=pygame.time.get_ticks()-self.new_square_ms
            if d<0 or d>ms:
                self.new_square=None
                g.redraw=True
        
                        
                                  
       
                
    
