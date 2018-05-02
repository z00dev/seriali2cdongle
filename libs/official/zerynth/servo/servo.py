"""
.. module:: servo 

*************
Servo Library
*************

This module contains class definitions for servo motors. 

The Servo class provides methods for handling generic servo motors connected to PWM enabled pins. It also provides easily accessible attributes for the control of motor positions with pulse width or angle inputs.

Every Servo instance implements the following methods:

    * attach: connects the servo motor and sets the default position
    * detach: sets the PWM pulse width of the instanced servo to 0 thus disconnecting the motor
    * moveToDegree: sets the servo position to the desired angle passed as float
    * moveToPulseWidth: sets the servo position to the desired raw value expressed as pulse width (int) microseconds
    * getCurrentPulseWidth: returns the current servo position in pulse width (int) microseconds
    * getCurrentDegree: returns the current position in degrees
    """


import pwm

class Servo():
    
    """
    ==================
    Servo class
    ==================
    
    .. class:: Servo(pin,min_width=500,max_width=2500,default_width=1500,period=20000)
    
        Creates a Servo instance:

            * **pin**: it is the pin where the servo motor signal wire is connected. The pin requires PWM functionality and its name has to be passed using the DX.PWM notation
            * **min_width**: it is the min value of the control PWM pulse width (microseconds). It has to be tuned according to servo capabilities. Defaults is set to 500.  
            * **max_width**: it is the max value of the control PWM pulse width (microseconds). It has to be tuned according to servo capabilities. Defaults is set to 2500.  
            * **default_width**: it is the position where the servo motor is moved when attached. It is expressed in microseconds and the default is set to 1500 corresponding to 90 degrees if the min-max range is set as default. 
            * **period**: it is the period of the PWM used for controlling the servo expressed in microseconds. Default is 20000 microseconds that is the most used standard.

        After initialization the servo motor object is created and the controlling PWM set to 0 leaving the servo digitally disconnected
    """
    def __init__(self,pin,min_width=500,max_width=2500,default_width=1500,period=20000):
        
        self.pin=pin
        self.minWidth=min_width
        self.maxWidth=max_width
        self.defaultPosition=default_width
        self.currentPosition=default_width
        self.period=period
        pwm.write(self.pin,self.period,0,MICROS)
        
    def map_range(self,x, in_min, in_max, out_min, out_max):
        if x < in_min:
            x = in_min    
        elif x > in_max: 
            x = in_max
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min    

 
    def attach(self):
        """
        .. method:: attach()
        
            Writes **default_width** to the servo associated PWM, enabling the motor and moving it to the default position. 
        """

        pwm.write(self.pin,self.period,self.defaultPosition,MICROS)

            
    def detach(self):
        """
        .. method:: detach()

            Writes 0 to the servo associated PWM disabling the motor. 
        """        
        
        pwm.write(self.pin,self.period,0,MICROS)

        
    def moveToDegree(self,degree):
        """
        .. method:: moveToDegree(degree)
    
            Moves the servo motor to the desired position expressed in degrees (float). 
        """        
        
        width=int(self.map_range(degree,0,180,self.minWidth,self.maxWidth))
        
        if width != self.currentPosition:            
            self.currentPosition=width
            pwm.write(self.pin, self.period,self.currentPosition,MICROS)
    
        
    def moveToPulseWidth(self,width):
        """
        .. method:: moveToPulseWidth(width)
    
            Moves the servo motor to the desired position expressed as pulse width (int) microseconds. The input has to be in min_width:max_width range. 
        """        

        if width< self.minWidth:
            width=self.minWidth
        elif width > self.maxWidth:
            width=self.maxWidth
        
        if width != self.currentPosition:            
            self.currentPosition=int(width)
            pwm.write(self.pin, self.period,self.currentPosition,MICROS)

        
    def getCurrentPulseWidth(self):
        """
        .. method:: getCurrentPulseWidth()
    
            Returns the servo motor position as pulse width (microseconds). 
        """                    
        
        return self.currentPosition

        
    def getCurrentDegree(self):
        """
        .. method:: getCurrentDegree()
    
            Returns the servo motor position as degrees. 
        """                    

        degree=self.map_range(self.currentPosition,self.minWidth,self.maxWidth,0,180)
        return degree
     
        
    