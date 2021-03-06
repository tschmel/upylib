import rfb

try:
    # wipy port
    from os import urandom
    # consider machine.rng()?
    def rand():
        return urandom(1)[0] 
except:
    try:
        # unix, esp8266 ports
        from urandom import getrandbits
        def rand():
            return getrandbits(8)
    except:
        # cpython
        from random import getrandbits
        def rand():
            return getrandbits(8)

w, h, = 255, 255
rvect = 4

def update(self, parent_w, parent_h):
    if self.x+self.vector[0] <= 0 or self.x+self.w+self.vector[0] >= parent_w:
        self.vector[0] = -self.vector[0]
    if self.y+self.vector[1] <=0 or self.y+self.h+self.vector[1] >= parent_h:
        self.vector[1] = -self.vector[1]
    self.x += self.vector[0]
    self.y += self.vector[1]


class Bounce(rfb.RfbSession):

    def __init__(self, conn, w, h, name):
        super().__init__(conn, w, h, name)

        self.rectangles = [
            rfb.RRERect( # background (clear previous frame)
                0, 0,
                w, h,
                (0,0,0),
                self.bpp, self.depth, 
                self.big, self.true,
                self.masks, self.shifts
                )
        ]
        
        self.large = rfb.RRERect( # large bouncing square
                                 w//2-25, h//2-25,
                                 50, 50,
                                 (255, 255, 255),
                                 self.bpp, self.depth, 
                                 self.big, self.true,
                                 self.masks, self.shifts
                                )
        # vector must be mutable
        self.large.vector = [rand()//60, rand()//60]
        self.large.update = update

        self.small = rfb.RRESubRect( # inner square
                                    self.large.w//2, self.large.h//2,
                                    20, 20,
                                    (0,0,0),
                                    self.bpp, self.depth, 
                                    self.big, self.true,
                                    self.masks, self.shifts
                                   )
        # vector must be mutable
        self.small.vector = [rand()//60, rand()//60]
        self.small.update = update

        self.large.subrectangles.append( self.small )
        self.rectangles.append( self.large )

    def update(self):
        self.send( rfb.ServerFrameBufferUpdate( self.rectangles ) )
        self.small.update(self.small, self.large.w, self.large.h)
        self.large.update(self.large, w, h)


svr = rfb.RfbServer(w, h, name=b'bounce', handler=Bounce)
svr.serve()