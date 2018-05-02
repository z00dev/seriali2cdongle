"""
.. module:: max7219

**************
MAX7219 Module
**************

    This Module exposes all functionalities of Maxim MAX7219 Led Display driver 
    (`datasheet <https://datasheets.maximintegrated.com/en/ds/MAX7219-MAX7221.pdf>`_).

"""

import spi

class MAX7219(spi.Spi):
    """

.. class:: MAX7219(spidrv, cs, clk=1000000)

    Creates an intance of a new MAX7219.

    :param spidrv: SPI Bus used '( SPI0, ... )'
    :param cs: Chip Select
    :param clk: Clock speed, default 100kHz

    Example: ::

        from maxim.max7219 import max7219

        ...

        display = max7219.MAX7219(SPI0, D17)
        display.set_led(row, col, 1) # set to on the led in 0x0 position

    """

    # Register Address Map
    DIGIT0          = 1
    DIGIT1          = 2
    DIGIT2          = 3
    DIGIT3          = 4
    DIGIT4          = 5
    DIGIT5          = 6
    DIGIT6          = 7
    DIGIT7          = 8
    NO_OP           = 0x00
    SHUTDOWN        = 0x0C
    SHUTDOWN_MODE   = 0
    SHUTDOWN_NORMAL = 1
    DECODE_MODE     = 0x09
    INTENSITY       = 0x0A
    SCAN_LIMIT      = 0x0B
    DISPLAY_TEST    = 0x0F

    #Table of characters and digits on 7-Segment Displays
    char_table = bytes((
        0b01111110,0b00110000,0b01101101,0b01111001,0b00110011,0b01011011,0b01011111,0b01110000,
        0b01111111,0b01111011,0b01110111,0b00011111,0b00001101,0b00111101,0b01001111,0b01000111,
        0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,
        0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,
        0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,
        0b00000000,0b00000000,0b00000000,0b00000000,0b10000000,0b00000001,0b10000000,0b00000000,
        0b01111110,0b00110000,0b01101101,0b01111001,0b00110011,0b01011011,0b01011111,0b01110000,
        0b01111111,0b01111011,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,
        0b00000000,0b01110111,0b00011111,0b00001101,0b00111101,0b01001111,0b01000111,0b00000000,
        0b00110111,0b00000000,0b00000000,0b00000000,0b00001110,0b00000000,0b00000000,0b00000000,
        0b01100111,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,
        0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00001000,
        0b00000000,0b01110111,0b00011111,0b00001101,0b00111101,0b01001111,0b01000111,0b00000000,
        0b00110111,0b00000000,0b00000000,0b00000000,0b00001110,0b00000000,0b00010101,0b00011101,
        0b01100111,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,
        0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000
    ,))


    def __init__(self, spidrv, cs, clk=1000000):
        spi.Spi.__init__(self, cs, spidrv, clock=clk)
        self.max_devices = 1

        # The array for shifting the data to the devices
        self.spidata = bytearray(16)

        # We keep track of the led-status for all 8 devices in this array
        self.status = bytearray(64)

        for i in self.status:
            self.status[i] = 0x00

        for i in range(self.max_devices):
            self._write(self.DISPLAY_TEST, 0)
            # scanlimit is set to max on startup
            self.set_scan_limit(0x07)
            # decode is done in source
            self._write(self.DECODE_MODE, 0)
            self.clear_display()
            # we go into shutdown-mode on startup
            self.shutdown(True)

    # Write value to BUS
    def _write(self, opcode, data):
        # Create an array with the data to shift out
        buffer = bytearray(0)
        maxbytes = self.max_devices * 2

        for i in range(maxbytes):
            self.spidata[i] = 0

        # Put our device data into the array
        self.spidata[1] = opcode
        self.spidata[0] = data

        for i in range(maxbytes, 0, -1):
                buffer.append(self.spidata[i-1])

        self.lock()

        # enable the line
        self.select()

        try:
            self.write(buffer)
        except Exception as e:
            print(e)
        finally:
            self.unselect()
            self.unlock()

#     def get_device_count(self):
#         """
# .. method:: get_device_count()

#             Returns the number of devices attached.

#         """
#         return self.max.devices

    def shutdown(self, powerdown):
        """
.. method:: shutdown(powerdown)

        Function to shutdown the display attached

        :param powerdown: Boolean ``True`` or ``False``
        
        """
        if powerdown:
            self._write(self.SHUTDOWN, self.SHUTDOWN_MODE)
        else:
            self._write(self.SHUTDOWN, self.SHUTDOWN_NORMAL)

    def set_scan_limit(self, limit):
        """
.. method:: set_scan_limit(limit) *only for 7-segments Display*

        Method that is used for seven segment displays that limits the number of digits.

        :param limit: number of banks (values 0 to 7).
        
        """
        if (limit >= 0) and (limit < 8):
            self._write(self.SCAN_LIMIT, limit)

    def set_intensity(self, intensity):
        """
.. method:: set_intensity(intensity)

        Sets the intensity of the LEDs output.

        :param intensity: light output intensity (values 0 to 15).
        
        """
        if (intensity >= 0) and (intensity < 16):
            self._write(self.INTENSITY, intensity)

    def clear_display(self):
        """
.. method:: clear_display()

        Clears the display by setting all LEDs to 0.

        """
        for i in range(8):
            self.status[i] = 0
            self._write(i + 1, self.status[i])


    def set_led(self, row, column, state):
        """
.. method:: set_led(row, column, state)

        Allows the control of a single LED.

        :param row: is the row (values 0 to 7)
        :param column: is the column (values 0 to 7)
        :param state: is ``True`` for Led ON, and ``False`` for Led OFF

        """
        if (row < 0) or (row > 7) or (column < 0) or (column > 7):
            return

        val = 0x80 >> column;

        if state:
            self.status[row] = self.status[row] | val
        else:
            val =~ val
            self.status[row] = self.status[row] & val

        self._write(row + 1, self.status[row])


    def set_row(self, row, state):
        """
.. method:: set_row(row, state)

        Sets an entire row.
        
        :param row: row to control (values from 0 to 7)
        :param state: is ``True`` for Led ON, and ``False`` for Led OFF

        """
        if (row < 0) or (row > 7):
            return

        for i in range(8):
            self.set_led(row, i, 1)


    def set_column(self, col, state):
        """
.. method:: set_column(col, state)

        Sets an entire column.
        
        :param column: column to control (values from 0 to 7)
        :param state: is ``True`` for Led ON, and ``False`` for Led OFF

        """
        if (col < 0) or (col > 7):
            return
        
        for i in range(8):
            self.set_led(i, col, 1)

    def set_digit(self, digit, value, dp):
        """
.. method:: set_digit(digit, value, dp) *only for 7-segments Display*

        Used with 7 segment displays to set a digit to display on the 7 segments.

        :param digit: is the bank from 0 to 7 to display
        :param value: is the number value
        :param dp: is the decimal point

        """
        if (digit < 0) or (digit > 7) or (value > 15):
            return
        v = self.char_table[value]

        if dp:
            v |= 0x80
        self.status[digit] = v
        self._write(digit + 1, v)

    def set_char(self, digit, value, state):
        """
.. method:: set_char(dev_num, digit, value, state) *only for 7-segments Display*

        :param digit: is the bank from 0 to 7 to display
        :param value: is the character value
        :param state: is ``True`` for Led ON, and ``False`` for Led OFF
        
        """
        if (digit < 0) or (digit > 7):
            return
        
        index = value
        if index > 127:
            #no defined beyond index 127, so we use the space char
            index = 32

        v = self.char_table[index]

        if state:
            v |= 0x80
        self.status[digit] = v
        self._write(digit+1, v)