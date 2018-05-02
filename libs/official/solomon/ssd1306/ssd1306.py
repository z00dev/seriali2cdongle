"""
.. module:: ssd1306

**************
SSD1306 Module
**************

This Module exposes all functionalities of Solomon SSD1306 OLED Display driver (`datasheet <https://www.olimex.com/Products/Modules/LCD/MOD-OLED-128x64/resources/SSD1306.pdf>`_).


    """


import spi

# Constants
SETCONTRAST              = 0x81
DISPLAYALLON_RESUME      = 0xA4
DISPLAYALLON             = 0xA5
NORMALDISPLAY            = 0xA6
INVERTDISPLAY            = 0xA7
DISPLAYOFF               = 0xAE
DISPLAYON                = 0xAF
SETDISPLAYOFFSET         = 0xD3
SETCOMPINS               = 0xDA
SETVCOMDETECT            = 0xDB
SETDISPLAYCLOCKDIV       = 0xD5
SETPRECHARGE             = 0xD9
SETMULTIPLEX             = 0xA8
SETLOWCOLUMN             = 0x00
SETHIGHCOLUMN            = 0x10
SETSTARTLINE             = 0x40
MEMORYMODE               = 0x20
COLUMNADDR               = 0x21
PAGEADDR                 = 0x22
COMSCANINC               = 0xC0
COMSCANDEC               = 0xC8
SEGREMAP                 = 0xA0
CHARGEPUMP               = 0x8D
EXTERNALVCC              = 0x1
SWITCHCAPVCC             = 0x2

# Scrolling constants
ACTIVATE_SCROLL                      = 0x2F
DEACTIVATE_SCROLL                    = 0x2E
SET_VERTICAL_SCROLL_AREA             = 0xA3
RIGHT_HORIZONTAL_SCROLL              = 0x26
LEFT_HORIZONTAL_SCROLL               = 0x27
VERTICAL_AND_RIGHT_HORIZONTAL_SCROLL = 0x29
VERTICAL_AND_LEFT_HORIZONTAL_SCROLL  = 0x2A

OLED_TEXT_ALIGN_NONE    = 0
OLED_TEXT_ALIGN_LEFT    = 0x1
OLED_TEXT_ALIGN_RIGHT   = 0x2
OLED_TEXT_ALIGN_CENTER  = 0x3
OLED_TEXT_VALIGN_TOP    = 0x10
OLED_TEXT_VALIGN_BOTTOM = 0x20
OLED_TEXT_VALIGN_CENTER = 0x30

OLED_TEXT_ALIGN = [
    OLED_TEXT_ALIGN_NONE,
    OLED_TEXT_ALIGN_LEFT,
    OLED_TEXT_ALIGN_RIGHT,
    OLED_TEXT_ALIGN_CENTER,
    OLED_TEXT_VALIGN_TOP,
    OLED_TEXT_VALIGN_BOTTOM,
    OLED_TEXT_VALIGN_CENTER
]

class SSD1306(spi.Spi):
    """
.. class: SSD1306(drv, cs, rst, dc, clock=8000000):

    Creates an intance of a new SSD1306.

    :param spidrv: SPI Bus used '( SPI0, ... )'
    :param cs: Chip Select
    :param rst: Reset pin
    :param dc: Data/Command control pin
    :param clk: Clock speed, default 8MHz

    Example: ::

        from solomon.ssd1306 import ssd1306

        ...

        oled = ssd1306.SSD1306(SPI0,D17,D16,D6)
        oled.init()
        oled.on()
    """
    def __init__(self, drv, cs, rst, dc, clock=8000000):
        spi.Spi.__init__(self,cs,drv,clock)
        self.dc=dc
        self.rst=rst
        self.font_init = False
        self.dynamic_area = {
            "x": 0,
            "y": 0,
            "width": 0,
            "height": 0,
            "buffer": None
        }
        pinMode(self.dc,OUTPUT)
        pinMode(self.rst,OUTPUT)
        self._reset()
        self.buf = bytearray(1)
        self.c_buf = None
  
    def _reset(self):
        digitalWrite(self.rst,0)
        sleep(2)
        digitalWrite(self.rst,1)
        sleep(2)
        
    def _command(self,cmd):
        self.select()
        digitalWrite(self.dc,0)
        self.buf[0]=cmd
        self.write(self.buf)
        self.unselect()
        
    def _data(self,data):
        self.select()
        digitalWrite(self.dc,1)
        self.buf[0]=data
        self.write(self.buf)
        self.unselect()

    def _set_page(self,page):
        page=0xb0|page;
        self._command(page)

    def _set_column(self,col):
        self._command(0x0f&col)
        self._command(0x10|(col>>4))

    def _check_coordinates(self,x,y,w,h):
        if x >= self._screen_width or y >= self._screen_height:
            raise ValueError
        if y+h > self._screen_height:
            raise ValueError
        if x+w > self._screen_width:
            raise ValueError

    def _prepare(self,x,y,w,h,fill):
        for page in range((y//8),((y+h-1)//8)+1):
            if page == y//8 and page == ((y+h-1)//8):
                bb = 0xFF << (y%8) & 0xFF
                if (y+h)%8 != 0:
                    bb &= 0xFF >> (8-((y+h)%8)) & 0xFF
            elif page == y//8:
                bb = 0xFF << (y%8) & 0xFF
            elif page == ((y+h-1)//8) and (y+h)%8 != 0:
                bb = 0xFF >> (8-((y+h)%8)) & 0xFF
            else:
                bb = 0xFF
            if fill == False:
                bb = ~bb&0xFF
            count = 0
            while count < w:
                if fill == False:
                    self._buf_display[(page*self._screen_width)+x+count] &= bb
                else:
                    self._buf_display[(page*self._screen_width)+x+count] |= bb
                count +=1
    
    def init(self, screen_width=96, screen_height=40):
        """

.. method:: init(screen_width=96, screen_height=40)

        Initialize the SSD1306 setting all internal registers and the display dimensions in pixels.

        :param screen_width: width in pixels of the display (max 128); default 96
        :param screen_height: height in pixels of the display (max 64); default 40
        
        """
        if screen_width > 128 or screen_height > 64:
            raise ValueError
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._screen_pages = screen_height//8
        self._buf_display = bytearray(self._screen_width*self._screen_pages)
        cc = 0
        while cc < self._screen_width*self._screen_pages:
            self._buf_display[cc] = 0x00
            cc +=1
        self._column_offset = (128-screen_width)
        self._raw_offset = 0
        self._command(SETDISPLAYCLOCKDIV)   #set display clock divide ratio 
        self._command(0x80)                 #0x80 
        self._command(SETMULTIPLEX)         #set mux ratio
        self._command(self._screen_height-1)
        self._command(SETDISPLAYOFFSET)     #set display offset
        self._command(0x00)                 #0x00
        self._command(SETSTARTLINE)         #Set Display Start Line
        self._command(CHARGEPUMP)           #Charge Pump Setting
        self._command(0x14)                 #0x14 Enable charge pump during display on
        self._command(SEGREMAP | 0x01)      #0xA1 Set Remap
        self._command(COMSCANDEC)           #Set COM Output Scan Direction 
        self._command(SETCOMPINS)           #Set COM Pins Hardware Configuration
        self._command(0x12)                 #0x12 Alternative COM pin configuration
        self._command(SETCONTRAST)          #set contrast control
        self._command(0xAF)                 #0xAF  
        self._command(SETPRECHARGE)         #Set Pre-charge Period
        self._command(0xF1)                 #0xF1
        self._command(SETVCOMDETECT)        #Set VCOMH Deselect Level 
        self._command(0x40)                  
        self._command(DISPLAYALLON_RESUME)  #disable entire display on
        self._command(NORMALDISPLAY)        #set normal display

    def on(self):
        """

.. method:: on()

        Turns on the display.

        """
        self._command(DISPLAYON)
        
    def off(self):
        """

.. method:: off()

        Turns off the display.

        """
        self._command(DISPLAYOFF)

    def invert(self):
        """

.. method:: invert()

        Sets the display in complementary mode.

        """
        self._command(INVERTDISPLAY)
        
    def normal(self):
        """

.. method:: normal()

        Sets the display in normal mode.

        """
        self._command(NORMALDISPLAY)

    def _set_font(self, font=None):
        try:
            if font != None:
                self.font = font
                self.first_char = font[2] | font[3] << 8
                self.last_char = font[4] | font[5] << 8
                self.font_height = font[6] 
        except Exception as e:
            print("font not recognized:", e)

    def _set_text_prop(self, align=OLED_TEXT_ALIGN_CENTER):
        if align not in OLED_TEXT_ALIGN:
            align = OLED_TEXT_ALIGN_CENTER
        self.align = align

    def _get_text_width(self, text):
        t_width = 0
        for c in text:
            index = 8 + ((ord(c) - self.first_char) << 2)
            t_width += self.font[index]
            # insert 1 px for space
            t_width += 1
        # remove last space
        t_width -= 1
        return t_width

    def _add_text(self, text, fill):
        t_width = self._get_text_width(text)
        if self.dynamic_area["width"]<t_width or self.dynamic_area["height"]<self.font_height:
            self.dynamic_area["width"] = t_width
            self.dynamic_area["height"]=self.font_height
        y = (self.dynamic_area["height"] - self.font_height) >> 1
        if self.align == OLED_TEXT_ALIGN_LEFT:
            x = 0
        elif self.align == OLED_TEXT_ALIGN_RIGHT:
            x = self.dynamic_area["width"] - t_width
        elif self.align == OLED_TEXT_ALIGN_CENTER:
            x = ((self.dynamic_area["width"] - t_width)//2)
        elif self.align == OLED_TEXT_ALIGN_NONE:
            x = 0
        # write the characters into designated space, one by one
        self._create_text_background(fill)
        for c in text:
            c_width = self._write_c_to_buf(c, fill)
            idx = ((y*self.dynamic_area["width"]) + x)
            self._add_char_to_dynamic_area(idx, c_width)
            x += c_width + 1
            self.c_buf = None

    def _create_text_background(self, fill=True):
        count = 0
        area = self.dynamic_area["width"]*self.dynamic_area["height"]
        self.dynamic_area["buffer"] = bytearray(area)
        while count < area:
            if fill == False:
                self.dynamic_area["buffer"][count] = 0xFF
            else:
                self.dynamic_area["buffer"][count] = 0x00
            count +=1

    def _add_char_to_dynamic_area(self, idx, c_width, c_height):
        x_count = 0
        for b in self.c_buf:
            self.dynamic_area["buffer"][idx] = b
            x_count += 1
            if x_count == c_width:
                x_count = 0
                idx += (self.dynamic_area["width"]-c_width)
            idx += 1

    def _write_c_to_buf(self, c, fill=True):
        idx = 8 + ((ord(c) - self.first_char) << 2)
        c_width = self.font[idx]
        offset = self.font[idx+1] | (self.font[idx+2] << 8) | (self.font[idx+3] << 16)
        area = self.font_height*c_width
        self.c_buf = bytearray(area)
        cnt = 0
        x_count = 0
        while cnt < area:
            if x_count == 0:
                mask = 1
                byte = self.font[offset]
            if (byte & mask) != 0:
                if fill == False:
                    self.c_buf[cnt] = 0x00
                else:
                    self.c_buf[cnt] = 0xFF
            else:
                if fill == False:
                    self.c_buf[cnt] = 0xFF
                else:
                    self.c_buf[cnt] = 0x00
            mask = mask << 1
            cnt += 1
            x_count += 1
            if x_count == c_width:
                x_count = 0
                offset += 1
        return c_width
    
    def set_contrast(self, contrast=0x7F):
        """

.. method:: set_contrast(contrast=0x7F)

        Sets the contrast of the display.

        :param contrast: value of the contrast to be set (from 0 to 255), default 0x7F

        """
        if contrast < 0 or contrast > 255:
            raise ValueError
        self._command(SETCONTRAST)
        self._command(contrast)
    
    def _send_data(self):
        for page in range(0,self._screen_pages):
            self._set_column(self._column_offset)
            self._set_page(page)            
            self.select()
            digitalWrite(self.dc,1)
            self.write(self._buf_display[page*self._screen_width:((page+1)*self._screen_width)])
            self.unselect()
    
    def clear(self):
        """

.. method:: clear()

        Clears the display.

        """
        cc = 0
        while cc < self._screen_width*self._screen_pages:
            self._buf_display[cc] = 0x00
            cc +=1
        self._send_data()
    
    def fill_screen(self):
        """
.. method:: fill_screen()

        Fills the entire display (white screen in normal mode).

        """
        cc = 0
        while cc < self._screen_width*self._screen_pages:
            self._buf_display[cc] = 0xFF
            cc +=1
        self._send_data()

    def fill_rect(self, x, y, w, h, fill=True):
        """
.. method:: fill_rect(x, y, w, h, fill=True)

        Draws a filled rectangular area in the screen.

        :param x: x-coordinate for left high corner of the rectangular area
        :param y: y-coordinate for left high corner of the rectangular area
        :param w: width of the rectangular area
        :param h: height of the rectangular area
        :param fill(*bool*): flag for filling the rectagnular area. If True draws white area, otherwise black area (in normal mode); default True

        .. note:: If the display is set in complementary mode (see :func:`invert()` function), fill flag set to True will draw black area and set to False will draw a white area.

        """
        self._check_coordinates(x,y,w,h)    
        self._prapare(x,y,w,h,fill)
        self._send_data()
        
    def draw_img(self, bytes, x, y, w, h, fill=True):
        """
.. method:: draw_img(image, x, y, w, h, fill=True)

        Draws the image passed in bytearray format as argument.

        :param bytes: bytearray composing the image to draw in the oled display
        :param x: x-coordinate for left high corner of the image
        :param y: y-coordinate for left high corner of the image
        :param w: width of the image
        :param h: height of the image
        :param fill(*bool*): flag for filling the image. If True draws image in standard color, otherwise draws the image in inverted color (display in normal mode); default True.

        .. note:: If the display is set in complementary mode (see :func:`invert()` function), fill flag set to True will draw the image in inverted color and set to False will draw the image in normal color.

        .. note :: To obtain a converted image in hex array format, you can go and use this `online tool <http://www.digole.com/tools/PicturetoC_Hex_converter.php>`_.
                   
                   After uploading your image, you can resize it setting the width and height fields; you can also choose the code format (HEX:0x recommended) and the color format
                   ("Black/White for all draw image function" recommended).
                   
                   Clicking on the "Get C string" button, the tool converts your image with your settings to a hex string that you can copy and paste inside a bytearray in your project and privide to this function.

        """
        self._check_coordinates(x,y,w,h)
        row = w//8
        if w%8 != 0:
            row += 1
        for ypix in range(0,h):
            for xpix in range(0,w):
                if bytes[ypix*row + (xpix//8)] & (1<<(7-(xpix%8))):
                    self._prepare(x+xpix,y+ypix,1,1,fill)
        self._send_data()
        

    def draw_pixel(self, x, y, fill=True):
        """
.. method:: draw_pixel(x, y, fill=True)

        Draws a single pixel in the screen.

        :param x: pixel x-coordinate
        :param y: pixel y-coordinate
        :param fill(*bool*): flag for filling the pixel. If True draws white pixel, otherwise black pixel (in normal mode); default True

        .. note:: If the display is set in complementary mode (see :func:`invert()` function), fill flag set to True will draw black pixel and set to False will draw a white pixel.
        
        """
        self._check_coordinates(x,y,1,1)
        self._prepare(x,y,1,1,fill)
        self._send_data()

    def draw_text(self, text, x=None, y=None, w=None, h=None, align=None, fill=True):
        """
.. method:: draw_text(text, x=None, y=None, w=None, h=None, align=None, fill=True)

        Prints a string inside a text box in the screen.

        :param text: string to be written in the display
        :param x: x-coordinate for left high corner of the text box; default None
        :param y: y-coordinate for left high corner of the text box; default None
        :param w: width of the text box; default None
        :param h: height of the text box; default None
        :param align: alignment of the text inside the text box (1 for left alignment, 2 for right alignment, 3 for center alignment); default None
        :param fill(*bool*): flag for filling the text. If True draws white text in black background, otherwise black text in white background (in normal mode); default True

        .. note:: If the display is set in complementary mode (see :func:`invert()` function), fill flag set to True will draw black text in white background and set to False will draw a white text in black background.
        
        .. note:: If only text argument is provided, an automatic text box is created with the following values:

                    * x = 0
                    * y = 0
                    * w = min text width according to the font
                    * h = max char height according to the font
                    * align = 3 (centered horizontally)
                    * fill = True

        """
        if not self.font_init:
            from solomon.ssd1306 import fonts
            self._set_font(font=fonts.guiFont_Tahoma_7_Regular)
            self.font_init = True
        if align != None:
            self._set_text_prop(align=align)
        else:
            self._set_text_prop()
        if x is None:
            x = 0
        if y is None:
            y = 0
        if w is None:
            w = self._get_text_width(text)
        if h is None:
            h = self.font_height
        self.dynamic_area["x"] = x
        self.dynamic_area["y"] = y
        self.dynamic_area["width"] = w
        self.dynamic_area["height"] = h
        self._add_text(text, fill)
        count = 0
        for ypix in range(0,self.dynamic_area["height"]):
            for xpix in range(0,self.dynamic_area["width"]):
                if self.dynamic_area["buffer"][count]:
                    self._prepare(x+xpix,y+ypix,1,1,True)
                else:
                    self._prepare(x+xpix,y+ypix,1,1,False)
                count += 1
        self._send_data()
        self.dynamic_area["buffer"] = None
