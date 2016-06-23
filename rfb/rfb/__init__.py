DEBUG = True
import socket
from rfb.session import *
if DEBUG: from time import sleep


class RfbServer():

    def __init__(self, 
                 w, h, 
                 colourmap = None,
                 name = b'rfb', 
                 handler = RfbSession,
                 addr = ('', 5900), 
                 backlog = 3,
                ):
        self.w = w
        self.h = h
        if colourmap and len(colourmap) > 0xff:
            raise Exception('>255 colours in colourmap')
        self.colourmap = colourmap
        # rfb session init fails with 0 length name
        if len(name) < 1:
            raise ValueError('name cannot be empty')
        self.name = name
        self.handler = handler
        self.DEBUG = DEBUG
        self.sessions = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(0)
        self.s.bind(addr)
        self.s.listen(backlog)

    def serve(self, delay=1):
        while True:
            #accept new connections
            self.accept()
            # handle established connections
            self.service()
            if DEBUG: sleep(0.1) # slow down
    
    def accept(self):
        try:
            self.sessions.append( 
                self.handler(self.s.accept(),
                            self.w, 
                            self.h,
                            self.colourmap,
                            self.name
                )
            )
        except BlockingIOError:
            pass
        except Exception as err:
            if DEBUG:
                print(err)
            else:
                pass

    def service(self):
        for idx,session in enumerate( self.sessions ):
            alive = session.dispatch_msgs()
            if not alive:
                del( self.sessions[idx] )
            else:
                session.update()