"""
.. module:: ws2812.ledstrips

*********************
WS2812 RGB Led Module
*********************

This module implements the Zerynth driver for the Worldsemi WS2812 Intelligent Control RGB Led assembled in any form, ledstrip, or ring.
(`datasheet <http://www.world-semi.com/DownLoadFile/108>`_).

    """

@native_c("ws2812_ledstrip_on",["csrc/ledstrips/*"])
def ws2812_ledstrip_on(pin,colors):
    pass


def add_color(r1,g1,b1,r2,g2,b2):
    """
.. function:: add_color(r1,g1,b1,r2,g2,b2)

   Returns a tuple (r,g,b) where r=r1+r2, g=g1+g2, b=b1+b2. In case of overflow, components are capped to 255

    """
    r = min(r1+r2,255)
    g = min(g1+g2,255)
    b = min(b1+b2,255)
    return (r,g,b)


def first_color(r1,g1,b1,r2,g2,b2):
    """
.. function:: first_color(r1,g1,b1,r2,g2,b2)

   Always returns (r1,g1,b1) unless all the components are zero. In that case it returns (r2,g2,b2)

    """
    if g1 or r1 or b1:
        return (r1,g1,b1)
    else:
        return (r2,g2,b2)
    
def second_color(r1,g1,b1,r2,g2,b2):
    """
.. function:: second_color(r1,g1,b1,r2,g2,b2)

   Always returns (r2,g2,b2) unless all the components are zero. In that case it returns (r1,g1,b1)

    """
    if g2 or r2 or b2:
        return (r2,g2,b2)
    else:
        return (r1,g1,b1)




class LedStrip():
    """
==============
LedStrip class
==============


.. class:: LedStrip(pin,nleds)

    This class abstracts a ledstrip. It needs to know which *pin* the ledstrip is wired to and how many leds it is composed of (*nleds*).
    The *pin* is automatically set to the correct mode and initially set to zero.

    """    
    def __init__(self,pin,nleds):
        self.colors = bytearray(nleds*3)
        self.pin = pin
        pinMode(pin,OUTPUT_PUSHPULL)
        digitalWrite(pin,0)

    def on(self):
        """
.. method:: on()

    Turns on the ledstrip, colouring each led with the configuration set with methods like :meth:`set`.

        """
        #self.drv.__ctl__(0,self.pin,self.colors)
        ws2812_ledstrip_on(self.pin,self.colors)
                
    def set(self,n,r,g,b):
        """
.. method:: set(n,r,g,b)

    Sets the *nth* led of the strip to the *r*, *g*, *b* color specified. The led will change color only after the next call to :meth:`on`.

    An equivalent and valid syntax is ledstrip[n]=(r,g,b).

        """
        self.colors[n*3] = g
        self.colors[n*3+1] = r
        self.colors[n*3+2] = b

    def setall(self,r,g,b):
        """
.. method:: setall(r,g,b)

    Sets all the leds of the strip to the *r*, *g*, *b* color specified. The led will change color only after the next call to :meth:`on`.
        """
        for t in range(0,len(self.colors),3):
            self.colors[t] = g
            self.colors[t+1] = r
            self.colors[t+2] = b

    def clear(self):
        """
.. method:: clear()

    Sets all the leds of the strip to off. The leds will turn off after the next call to :meth:`on`.
        """

        for t in range(0,len(self.colors)):
            self.colors[t] = 0



    def __setitem__(self, key, value):
        self.colors[key*3] = value[1]
        self.colors[key*3+1] = value[0]
        self.colors[key*3+2] = value[2]

    def __getitem__(self, key):
        return (self.colors[key*3+1],self.colors[key*3],self.colors[key*3+2])


    def lshift(self):
        """
.. method:: lshift()

    Shifts to the left all the leds by one. The leds will change color only after the next call to :meth:`on`.
        """
        g = self.colors[0]
        r = self.colors[1]
        b = self.colors[2]

        self.colors = self.colors[3:]
        self.colors.append(g)
        self.colors.append(r)
        self.colors.append(b)

    def rshift(self):
        """
.. method:: rshift()

    Shifts to the right all the leds by one. The leds will change color only after the next call to :meth:`on`.
        """

        g = self.colors[-3]
        r = self.colors[-2]
        b = self.colors[-1]
        self.colors = self.colors[0:-3]

        t = bytearray(3)
        t[0]=g
        t[1]=r
        t[2]=b
        t.extend(self.colors)
        self.colors=t


    def brightness(self,brt):
        """
.. method:: brightness(brt)

    Multiplies all the led color by *brt*, a float between 0 and 1. The leds will change color only after the next call to :meth:`on`.
        """
        for t in range(0,len(self.colors)):
            self.colors[t] = int(self.colors[t]*brt)

    def set_fading(self,r,g,b,pos=0):
        nleds = len(self.colors)//3
        cleds = 0
        while cleds<nleds:
            self.colors[3*pos]= g-(g//nleds*cleds)
            self.colors[3*pos+1]= r-(r//nleds*cleds)
            self.colors[3*pos+2]= b-(b//nleds*cleds)
            pos=(pos+1)%nleds
            cleds+=1


    def merge(self,lstrip,fun=add_color):
        """
.. method:: merge(lstrip,fun=add_color)

    Merges *lstrip* with the current strip (*self*).
    The resulting colors are calculated by applying *fun* to every corresponding pair of leds in the ledstrips.

    The signature of fun must be *fun(r1,g1,b1,r2,b2,g2)* where r1,g1,b1 are the color components of the first strip
    and r2,g2,b2 are the color components of the second strip. The default *add_color* sums colors component by component.

    Merging strips is very useful for animations. Indeed one can build different layers on different strips, animate them
    separately and merge them in one single strip to be showed.

        """
        for t in range(0,len(self.colors),3):
            r,g,b= fun(self.colors[t+1],self.colors[t],self.colors[t+2],lstrip.colors[t+1],lstrip.colors[t],lstrip.colors[t+2])
            self.colors[t] =g
            self.colors[t+1] =r
            self.colors[t+2] =b



