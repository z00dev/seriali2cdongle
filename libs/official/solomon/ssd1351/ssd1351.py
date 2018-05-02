"""
.. module:: ssd1351

**************
SSD1351 Module
**************

This Module exposes all functionalities of Solomon SSD1351 Color OLED Display driver (`datasheet <https://developer.mbed.org/media/uploads/GregC/ssd1351-revision_1.3.pdf>`_).

.. note:: Only 65k color depth is supported; 262k color depth will be available soon.


    """


import spi

# Constants
SETCONTRAST             = 0x81
DISPLAYALLON_RESUME     = 0xA4
DISPLAYALLON            = 0xA5
NORMALDISPLAY           = 0xA6
INVERTDISPLAY           = 0xA7
DISPLAYOFF              = 0xAE
DISPLAYON               = 0xAF
SETDISPLAYOFFSET        = 0xD3
SETCOMPINS              = 0xDA
SETVCOMDETECT           = 0xDB
SETDISPLAYCLOCKDIV      = 0xD5
SETPRECHARGE            = 0xD9
SETMULTIPLEX            = 0xA8
SETLOWCOLUMN            = 0x00
SETHIGHCOLUMN           = 0x10
SETSTARTLINE            = 0x40
MEMORYMODE              = 0x20
COLUMNADDR              = 0x21
PAGEADDR                = 0x22
COMSCANINC              = 0xC0
COMSCANDEC              = 0xC8
SEGREMAP                = 0xA0
CHARGEPUMP              = 0x8D
EXTERNALVCC             = 0x1
SWITCHCAPVCC            = 0x2

# Scrolling constants
ACTIVATE_SCROLL                         = 0x2F
DEACTIVATE_SCROLL                       = 0x2E
SET_VERTICAL_SCROLL_AREA                = 0xA3
RIGHT_HORIZONTAL_SCROLL                 = 0x26
LEFT_HORIZONTAL_SCROLL                  = 0x27
VERTICAL_AND_RIGHT_HORIZONTAL_SCROLL    = 0x29
VERTICAL_AND_LEFT_HORIZONTAL_SCROLL     = 0x2A

DELAYS_HWFILL = 3
DELAYS_HWLINE = 1

# SSD1351 Commands
CMD_SETCOLUMN          = 0x15
CMD_SETROW             = 0x75
CMD_WRITERAM           = 0x5C
CMD_READRAM            = 0x5D
CMD_SETREMAP           = 0xA0
CMD_STARTLINE          = 0xA1
CMD_DISPLAYOFFSET      = 0xA2
CMD_DISPLAYALLOFF      = 0xA4
CMD_DISPLAYALLON       = 0xA5
CMD_NORMALDISPLAY      = 0xA6
CMD_INVERTDISPLAY      = 0xA7
CMD_FUNCTIONSELECT     = 0xAB
CMD_DISPLAYOFF         = 0xAE
CMD_DISPLAYON          = 0xAF
COM_SCAN_INC           = 0xC0
COM_SCAN_DEC           = 0xC8
CMD_PRECHARGE          = 0xB1
CMD_DISPLAYENHANCE     = 0xB2
CMD_CLOCKDIV           = 0xB3
CMD_SETVSL             = 0xB4
CMD_SETGPIO            = 0xB5
CMD_PRECHARGE2         = 0xB6
CMD_SETGRAY            = 0xB8
CMD_USELUT             = 0xB9
CMD_PRECHARGELEVEL     = 0xBB
CMD_VCOMH              = 0xBE
CMD_CONTRASTABC        = 0xC1
CMD_CONTRASTMASTER     = 0xC7
CMD_MUXRATIO           = 0xCA
CMD_COMMANDLOCK        = 0xFD
CMD_HORIZSCROLL        = 0x96
CMD_STOPSCROLL         = 0x9E
CMD_STARTSCROLL        = 0x9F
SET_COM_PINS           = 0xDA

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

class SSD1351(spi.Spi):
    """
.. class: SSD1351(drv, cs, rst, dc, pwr, clock=8000000):

    Creates an intance of a new SSD1351.

    :param spidrv: SPI Bus used '( SPI0, ... )'
    :param cs: Chip Select
    :param rst: Reset pin
    :param dc: Data/Command control pin
    :param pwr: Power On pin
    :param clk: Clock speed, default 8MHz

    Example: ::

        from solomon.ssd1351 import ssd1351

        ...

        oled = ssd1351.SSD1351(SPI0,D57,D58,D59,D71)
        oled.init()
        oled.on()
        oled.fill_screen(color=0xFFFFFF)
    """
    def __init__(self, drv, cs, rst, dc, pwr, clock=8000000):
        spi.Spi.__init__(self,cs,drv,clock)
        self.dc=dc
        self.rst=rst
        self.pwr=pwr
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
        pinMode(self.pwr,OUTPUT)
        self._pwr_off()
        self._reset()
        self._pwr_on()
        self.buf = bytearray(1)
        self.s_buf = None
        self.c_buf = None
    
    def _pwr_on(self):
        digitalWrite(self.pwr,1)
        sleep(60);
    
    def _pwr_off(self):
        digitalWrite(self.pwr,0)
        sleep(2);
    
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
    
    def init(self, screen_width=128, screen_height=128):
        """

.. method:: init(screen_width=128, screen_height=128)

        Initialize the SSD1351 setting all internal registers and the display dimensions in pixels.

        :param screen_width: width in pixels of the display (max 128); default 128
        :param screen_height: height in pixels of the display (max 128); default 128
        
        """
        if screen_width > 128 or screen_height > 128:
            raise ValueError
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._column_offset = (128-screen_width)>>1
        self._raw_offset = 0
        self._bit_per_pixel = 2
        self._command(CMD_COMMANDLOCK)
        self._data(0x12) # Unlock OLED driver IC MCU interface from entering command
        self._command(CMD_COMMANDLOCK)
        self._data(0xB1) # Command A2,B1,B3,BB,BE,C1 accessible if in unlock state 
        self._command(CMD_DISPLAYOFF)
        self._command(CMD_CLOCKDIV)
        self._data(0xF1) # 7:4 = Oscillator Frequency, 3:0 = CLK Div Ratio (A[3:0]+1 = 1..16)
        self._command(CMD_MUXRATIO)
        self._data(self._screen_width-1)
        self._command(CMD_SETREMAP)
        self._data(self._screen_width)
        self._command(CMD_SETCOLUMN)
        self._data(0x00)
        self._data(self._screen_width-1)
        self._command(CMD_SETROW)
        self._data(0x00)
        self._data(self._screen_height-1)
        self._command(CMD_STARTLINE)
        self._data(0x80)
        self._command(CMD_DISPLAYOFFSET)
        self._data(self._screen_width)
        self._command(CMD_PRECHARGE)
        self._data(0x32)
        self._command(CMD_VCOMH)
        self._data(0x05)
        self._command(CMD_NORMALDISPLAY)
        self._command(CMD_CONTRASTABC)
        self._data(0x8A)
        self._data(0x51)
        self._data(0x8A)
        self._command(CMD_CONTRASTMASTER)
        self._data(0xCF)
        self._command(CMD_SETVSL)
        self._data(0xA0)
        self._data(0xB5)
        self._data(0x55)
        self._command(CMD_PRECHARGE2)
        self._data(0x01)

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

    def _scale(self, x, inLow, inHigh, outLow, outHigh):
        return int(((x - inLow) / float(inHigh) * outHigh) + outLow)

    def _encode_color(self, color):
        red = (color >> 16) & 0xFF
        green = (color >> 8) & 0xFF
        blue = color & 0xFF
        # scaled colors
        redScaled = int(self._scale(red, 0, 0xFF, 0, 0x1F))
        greenScaled = int(self._scale(green, 0, 0xFF, 0, 0x3F))
        blueScaled = int(self._scale(blue, 0, 0xFF, 0, 0x1F))
        return (((redScaled << 6) | greenScaled) << 5) | blueScaled
    
    def _set_font(self, font=None, font_color=None, encode=True):
        try:
            if font != None:
                self.font = font
                self.first_char = font[2] | font[3] << 8
                self.last_char = font[4] | font[5] << 8
                self.font_height = font[6]
            if font_color != None:
                if encode:
                    font_color = self._encode_color(font_color)
                self.font_color = font_color 
        except Exception as e:
            print("font not recognized:", e)

    def _set_text_prop(self, align=OLED_TEXT_ALIGN_CENTER, background=None, encode=True):
        if align not in OLED_TEXT_ALIGN:
            align = OLED_TEXT_ALIGN_CENTER
        if background != None:
            if encode:
                background = self._encode_color(background)
        else:
            background = 0x4471
        self.align = align
        self.background = background

    def _get_text_width(self, text):
        t_width = 0
        for c in text:
            index = 8 + ((ord(c) - self.first_char) << 2)
            t_width += self.font[index]
            # insert 1 px for space
            t_width += 1
            #print(c, t_width)
        # remove last space
        t_width -= 1
        #print(t_width)
        return t_width

    def _add_text(self, text):
        t_width = self._get_text_width(text)
        if self.dynamic_area["width"]<t_width or self.dynamic_area["height"]<self.font_height:
            #print("resize dynamic area")
            self.dynamic_area["width"] = t_width
            self.dynamic_area["height"]=self.font_height
        y = (self.dynamic_area["height"] - self.font_height) >> 1
        #print("t_width",t_width)
        if self.align == OLED_TEXT_ALIGN_LEFT:
            x = 0
        elif self.align == OLED_TEXT_ALIGN_RIGHT:
            x = self.dynamic_area["width"] - t_width
        elif self.align == OLED_TEXT_ALIGN_CENTER:
            x = ((self.dynamic_area["width"] - t_width)//2)
        elif self.align == OLED_TEXT_ALIGN_NONE:
            x = 0
        #print("x", x, "y", y, t_width)
        # write the characters into designated space, one by one
        self._create_text_background()
        for c in text:
            c_width = self._write_c_to_buf(c)
            idx = ((y*self.dynamic_area["width"]*2) + x*2)#+OLED_COLUMN_OFFSET
            self._add_char_to_dynamic_area(idx, c_width)
            x += c_width + 1
            self.c_buf = None

    def _create_text_background(self):
        d1 = self.background >> 8
        d2 = self.background & 0x00FF
        count = 0
        area = self.dynamic_area["width"]*self.dynamic_area["height"]
        self.dynamic_area["buffer"] = bytearray(area*2)
        while count < area:
            self.dynamic_area["buffer"][2*count] = d1
            self.dynamic_area["buffer"][(2*count) + 1] = d2
            count +=1

    def _add_char_to_dynamic_area(self, idx, c_width, c_height):
        x_count = 0
        for b in self.c_buf:
            self.dynamic_area["buffer"][idx] = b
            x_count += 1
            if x_count == c_width*2:
                x_count = 0
                idx += (self.dynamic_area["width"]-c_width)*2
            idx += 1

    def _write_c_to_buf(self, c):
        #print(c)
        idx = 8 + ((ord(c) - self.first_char) << 2)
        #print(idx, ord(c))
        c_width = self.font[idx]
        offset = self.font[idx+1] | (self.font[idx+2] << 8) | (self.font[idx+3] << 16)
        #print(c_width, self.font_height, offset, len(self.font))
        area = self.font_height*c_width
        self.c_buf = bytearray(area*2)
        cnt = 0
        x_count = 0
        while cnt < area:
            if x_count == 0:
                mask = 1
                byte = self.font[offset]
            #print(cnt, area, len(self.c_buf), byte)
            if (byte & mask) != 0:
                #print(((self.font_color >> 2) & 0xFF), (self.font_color & 0xFF))
                self.c_buf[cnt*2] = self.font_color >> 8
                self.c_buf[(cnt*2) + 1] = self.font_color & 0xFF
            else:
                self.c_buf[cnt*2] = self.background >> 8
                self.c_buf[(cnt*2) + 1] = self.background & 0xFF
            mask = mask << 1
            cnt += 1
            x_count += 1
            if x_count == c_width:
                x_count = 0
                offset += 1
        return c_width

    def _prepare(self, x, y, w, h):
        # check border
        if x >= self._screen_width or y >= self._screen_height:
            return None
        if y+h > self._screen_height:
            h = self._screen_height - y - 1
        if x+w > self._screen_width:
            w = self._screen_width - x - 1
        # adjust offset
        x = x+self._column_offset
        y = y+self._raw_offset
        # set location
        self._command(CMD_SETCOLUMN)
        self._data(x)
        self._data(x+w-1)
        self._command(CMD_SETROW)
        self._data(y)
        self._data(y+h-1)
        self._command(CMD_WRITERAM)
    
    def set_contrast(self, contrast=0x7F):
        """

.. method:: set_contrast(contrast=0x7F)

        Sets the contrast of the display.

        :param contrast: value of the contrast to be set (from 0 to 255), default 0x7F

        """
        if contrast > 255:
            raise ValueError
        self._command(CMD_CONTRASTMASTER)
        self._data(contrast)
    
    def _send_data(self, bytes):
        self.select()
        digitalWrite(self.dc,1)
        self.write(bytes)
        self.unselect()
    
    def clear(self):
        """

.. method:: clear()

        Clears the display.

        """
        self.fill_screen(0x000000)
    
    def fill_screen(self, color, encode=True):
        """
.. method:: fill_screen(color, encode=True)

        Fills the entire display with color code provided as argument.

        :param color: hex color code for the screen
        :param encode(*bool*): flag for enabling the color encoding; default True

        .. note:: To be compatible with the 65k color format, if a stadard hex color code (24 bit) is provided
                  it is necessary to encode it into a 16 bit format.
                  
                  If a 16 bit color code is provided, the encode flag must be set to False.

        """
        self.fill_rect(0, 0, self._screen_width, self._screen_height, color, encode)

    def fill_rect(self, x, y, w, h, color, encode=True):
        """
.. method:: fill_rect(x, y, w, h, color, encode=True)

        Draws a rectangular area in the screen colored with the color code provided as argument.

        :param x: x-coordinate for left high corner of the rectangular area
        :param y: y-coordinate for left high corner of the rectangular area
        :param w: width of the rectangular area
        :param h: height of the rectangular area
        :param color: hex color code for the rectangular area
        :param encode(*bool*): flag for enabling the color encoding; default True

        .. note:: To be compatible with the 65k color format, if a stadard hex color code (24 bit) is provided
                  it is necessary to encode it into a 16 bit format.
                  
                  If a 16 bit color code is provided, the encode flag must be set to False.

        """
        self._prepare(x, y, w, h)
        #print("not encoded", color)
        if encode:
            color = self._encode_color(color)
        #print("encoded", color)
        d1 = color >> 8
        d2 = color & 0x00FF
        count = 0
        self.s_buf = bytearray(w*h*2)
        while count < w*h:
            self.s_buf[2*count] = d1
            self.s_buf[(2*count) + 1] = d2
            count +=1
        self._send_data(self.s_buf)
        self.s_buf = None
        
    def draw_img(self, bytes, x, y, w, h):
        """
.. method:: draw_img(image, x, y, w, h)

        Draws a rectangular area in the screen colored with the color code provided as argument.

        :param image: image to draw in the oled display converted to hex array format and passed as bytearray
        :param x: x-coordinate for left high corner of the image
        :param y: y-coordinate for left high corner of the image
        :param w: width of the image
        :param h: height of the image
        
        .. note :: To obtain a converted image in hex array format, you can go and use this `online tool <http://www.digole.com/tools/PicturetoC_Hex_converter.php>`_.
                   
                   After uploading your image, you can resize it setting the width and height fields; you can also choose the code format (HEX:0x recommended) and the color format
                   (65K color recommended).
                   
                   Clicking on the "Get C string" button, the tool converts your image with your settings to a hex string that you can copy and paste inside a bytearray in your project and privide to this function.

        """
        self._prepare(x, y, w, h)
        self._send_data(bytes)
        
    def draw_pixel(self, x, y, color, encode=True):
        """
.. method:: draw_pixel(x, y, color, encode=True)

        Draws a single pixel in the screen colored with the color code provided as argument.

        :param x: pixel x-coordinate
        :param y: pixel y-coordinate
        :param color: hex color code for the pixel
        :param encode(*bool*): flag for enabling the color encoding; default True

        .. note:: To be compatible with the 65k color format, if a stadard hex color code (24 bit) is provided
                  it is necessary to encode it into a 16 bit format.
                  
                  If a 16 bit color code is provided, the encode flag must be set to False.

        """
        self._prepare(x, y, 1, 1)
        if encode:
            color = self._encode_color(color)
        d1 = color >> 8
        d2 = color & 0x00FF
        self._send_data(bytearray([d1,d2]))
        
    def draw_text(self, text, x=None, y=None, w=None, h=None, color=None, align=None, background=None, encode=True):
        """
.. method:: draw_text(text, x=None, y=None, w=None, h=None, color=None, align=None, background=None, encode=True)

        Prints a string inside a text box in the screen.

        :param text: string to be written in the display
        :param x: x-coordinate for left high corner of the text box; default None
        :param y: y-coordinate for left high corner of the text box; default None
        :param w: width of the text box; default None
        :param h: height of the text box; default None
        :param color: hex color code for the font; default None
        :param align: alignment of the text inside the text box (1 for left alignment, 2 for right alignment, 3 for center alignment); default None
        :param background: hex color code for the background; default None
        :param encode(*bool*): flag for enabling the color encoding of the font and background color; default True

        .. note:: To be compatible with the 65k color format, so if a stadard hex color code (24 bit) is provided
                  it is necessary to encode it into a 16 bit format.
                  
                  If a 16 bit color code is provided, the encode flag must be set to False.

        .. note:: If only text argument is provided, an automatic text box is created with the following values:

                    * x = 0
                    * y = 0
                    * w = min text width according to the font
                    * h = max char height according to the font
                    * color = 0xFFFF
                    * align = 3 (centered horizontally)
                    * background = 0x4471

        """
        if not self.font_init:
            from solomon.ssd1351 import fonts
            self._set_font(font=fonts.guiFont_Tahoma_7_Regular, font_color=0xFFFF, encode=False)
            self.font_init = True
        if color != None:
            self._set_font(font_color=color, encode=encode)
        else:
            self._set_font(font_color=0xFFFFFF)
        if background != None and align != None:
            self._set_text_prop(align=align, background=background, encode=encode)
        elif background != None:
            self._set_text_prop(background=background, encode=encode)
        elif align != None:
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
        self._add_text(text)
        self._prepare(self.dynamic_area["x"], self.dynamic_area["y"], self.dynamic_area["width"], self.dynamic_area["height"])
        self._send_data(self.dynamic_area["buffer"])
        self.dynamic_area["buffer"] = None
