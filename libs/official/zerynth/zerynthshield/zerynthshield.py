"""
.. module:: zerynthshield

**********************
Zerynth Shield Library
**********************

This module contains class definitions and instances for Zerynth Shield's sensors.
Furthermore it takes care of multi-device pin compatibility providing generic names for every useful pin on the shield.
Every sensor of the Zerynth Shield is instanced as a child class of the Digital or the Analog Sensor class (as defined in :ref:`Smart Sensors Library <smartSensors>`).
Moreover, few peculiar methods are added.
The class inherits the whole set of sampling methods included in the :ref:`Digital <digitalSensor>` or :ref:`Analog <analogSensor>` Sensor Library (startSampling, doEverySample, addCheck,...)

Pin names:

    * zerynthshield.temperature_pin
    * zerynthshield.light_pin
    * zerynthshield.microphone_pin
    * zerynthshield.iremitter_pin
    * zerynthshield.irreceiver_pin
    * zerynthshield.touch_pin
    * zerynthshield.buzzer_pin
    * zerynthshield.led_pin

Sensors:

    * light (analogSensors): it is an instance of the analogSensor class configured for the Zerynth Shield light sensor
    * microphone (analogSensors): it is an instance of the analogSensor class configured for the Zerynth Shield microphone
    * temperature (analogSensors): it is an instance of the analogSensor class configured for the Zerynth Shield temperature sensor
    * touch (digitalSensors): it is an instance of the digitalSensor class configured for the Zerynth Shield touch sensor    


For example, sampling the temperature in Celsius can be done with::

    zerynthshield.temperature.setNormFunc(zerynthshield.toCelsius)
    zerynthshield.temperature.startSampling(1000,None,"norm")

The smartsensors lib allows the definition of a function to be called periodically. See the smartsensors lib documentation for more details.     

An Arduino-like style is also supported::

    while True:
        zerynthshield.temperature.getCelsius()
        sleep(1000)

"""

from smartsensors import analogSensors
from smartsensors import digitalSensors
import icu
import pwm


class ZPin():
    pass

if  __defined(LAYOUT, "arduino_uno"):

    # common
    aux1 = ZPin()
    aux1.ADC = A0.ADC
    aux1.DIO = A0

    aux2 = ZPin()
    aux2.ADC = A1.ADC
    aux2.DIO = A2

    aux3 = ZPin()
    #aux3.PWM = D11.PWM
    aux3.DIO = D11

    aux4 = ZPin()
    #aux4.PWM = D12.PWM
    aux4.DIO = D12

    aux5 = ZPin()
    aux5.DIO = D13
    #aux5.PWM = D13.PWM

    aux6 = ZPin()
    aux6.DIO = A2
    aux6.ADC = A2.ADC

    aux7 = ZPin()

    aux8 = ZPin()


    temperature_pin = A4
    light_pin = A5
    microphone_pin = A3
    iremitter_pin=D6.PWM
    irreceiver_pin=D2.ICU
    touch_pin=D7
    buzzer_pin=D8.PWM
    led_pin=D9

if __defined(BOARD,"st_nucleof401re"):
    aux1.PWM = A0.PWM
    # aux1.ICU = A0.ICU

    aux2.PWM = A1.PWM
    # aux2.ICU = A1.ICU

    aux3.MOSI = D11.MOSI
    aux3.ADC = D11.ADC

    aux4.MISO = D12.MISO
    aux4.ADC = D12.ADC

    aux5.SCLK = D13.SCLK
    aux5.ADC = D13.ADC

    # aux6.PWM = D14.PWM

    aux7.DIO = D15
    # aux7.ICU = D15.ICU
    # aux7.PWM = D15.PWM
    aux7.SCL = D15.SCL

    aux8.DIO = D14
    aux8.SDA = D14.SDA

if __defined(BOARD, "arduino_due"):
    aux3.MOSI = D63.MOSI # ?

    aux4.MISO = D62.MISO

    aux5.SCK = D64.SCLK

    aux7.DIO = D21
    aux7.SCL = D21.SCL

    aux8.DIO = D20
    aux8.SDA = D20.SDA

if  __defined(LAYOUT,"particle"):

    # common

    aux1 = ZPin()
    aux1.ADC = A3.ADC
    aux1.DIO = A3

    # aux2.ICU = A7.ICU
    aux2 = ZPin()

    aux3 = ZPin()
    aux3.DIO = D2
    # aux3.MOSI = D2.MOSI

    aux4 = ZPin()
    aux4.DIO = D3
    aux4.MISO = D3.MISO

    aux5 = ZPin()
    aux5.DIO = D4
    aux5.SCLK = D4.SCLK

    aux6 = ZPin()
    aux6.DIO = D5

    aux7 = ZPin()
    aux7.DIO = D0
    aux7.PWM = D0.PWM
    aux7.SDA = D0.SDA
    aux7.ICU = D0.ICU

    aux8 = ZPin()
    aux8.DIO = D1
    aux8.PWM = D1.PWM
    aux8.SCL = D1.SCL
    # aux8.ICU = D1.ICU

    temperature_pin = A1
    light_pin = A0
    microphone_pin = A2
    iremitter_pin=A5.PWM
    irreceiver_pin=A4.ICU
    touch_pin=D7
    led_pin=D6

if __defined(BOARD,"particle_photon"):
    aux2.ADC = D9.ADC
    aux2.PWM = D9.PWM
    aux2.DIO = D9
    buzzer_pin=D8
elif __defined(BOARD,"particle_core"):
    aux2.ADC = A7.ADC
    aux2.PWM = A7.PWM
    aux2.DIO = A7
    buzzer_pin=A6



pinMode(iremitter_pin,OUTPUT)
digitalWrite(iremitter_pin,0)
pinMode(buzzer_pin,OUTPUT)
digitalWrite(buzzer_pin,0)

#### generic normFunc

def toFloat(val,obj):
    return val/4096

####


class TouchSensor(digitalSensors.DigitalSensor):
    """
    ================
    TouchSensor class
    ================
    
    .. class:: TouchSensor
    
        This class provides simple methods for the detection of single and double touch on the Zerynth Shield integrated capacitive touch sensor.
        
        An instance of the class is available by calling the zerynthshield.touch attribute.
    """
    def __init__(self):        
        
        digitalSensors.DigitalSensor.__init__(self,touch_pin)
    
    def onSingleTouch(self,min_time,max_time,to_do,long_fn = None):
        """
        .. method:: onSingleTouch(min_time,max_time,to_do,long_fn = None)
    
            Sets a to_do function to be executed when a touch occurs and lasts more than min_time and less than max_time (expressed in milliseconds), if max_time limit is exceeded long_fn is called.

        Args:
            * min_time (int): minimum touch time 
            * max_time (int): maximum touch time after that the touch is not considered anymore as a single touch but as a long touch
            * to_do (function): function to be executed when a single-touch occurs 
            * long_fn (function, optional): function to be executed when a long touch occurs  

        """
        
        self.onRiseAndFall(min_time,max_time,to_do,long_fn)
    
    def onDoubleTouch(self,min_time,max_time,max_interval,first_action,second_action,long_fn = None):
        """
        .. method:: onDoubleTouch(min_time,max_time,to_do,long_fn = None)
        
            Sets a first_action function to be executed when a touch occurs and lasts more than min_time and less than max_time (expressed in milliseconds), if max_time limit is
            exceeded long_fn is executed. 

            When first_action constrains are respected, if a second touch occurs at most after max_interval milliseconds and the length of the touch is between min_time and max_time, then second_action function is called.
    
        Args:
            * min_time (int): minimum touch time 
            * max_time (int): maximum touch time after that the touch is not considered anymore as a single touch but as a long touch
            * max_interval (int): the maximum time span between touches to consider a double touch event instead of two separated single touches.
            * first_action (function): function to be executed when a single-touch occurs 
            * second_action (function, optional): function to be executed when a double touch occurs
            * long_fn (function, optional): function to be executed when a long touch occurs
        """
        self.onSequence(0,[[min_time,max_time],[15,max_interval],[min_time,max_time]],[first_action,None,second_action],long_fn)

touch = TouchSensor()

####

class LightSensor(analogSensors.AnalogSensor):
    """
    =================
    LightSensor class
    =================
    
    .. class:: LightSensor
    
        This class provides a default getFloat() normalization method for the photoresistor integrated in the Zerynth Shield.

        An instance of the class is available by calling the zerynthshield.light attribute.
    """
    def __init__(self):
        analogSensors.AnalogSensor.__init__(self,light_pin)
        self.normName = None

    def getFloat(self):
        """
        .. method:: getFloat()
        
           Returns samples normalized between 0 and 1.
        """
        if not self.normName == "float":
            self.normName = "float"
            self.normFunc = toFloat
        return self.getNormalized()

light = LightSensor()

####

def toCelsius(val,obj):
    return (val * 0.0953) - 53.704

class TemperatureSensor(analogSensors.AnalogSensor):
    """
    =======================
    TemperatureSensor class
    =======================
    
    .. class:: TemperatureSensor
    
        This class provides two default normalization method for the temperature sensor: getFloat() and getCelsius()

        An instance of the class is available by calling the zerynthshield.temperature attribute.
    
    """
    def __init__(self):
        analogSensors.AnalogSensor.__init__(self,temperature_pin)
        self.normName = None

    def getCelsius(self):
        """
        .. method:: getCelsius()
        
            Returns samples directly converted in celsius degrees.
        """
        if not self.normName == "celsius":
            self.normName = "celsius"
            self.normFunc = toCelsius
        return self.getNormalized()

    def getFloat(self):
        """
        .. method:: getFloat()
        
            Returns samples normalized between 0 and 1.
        """
        if not self.normName == "float":
            self.normName = "float"
            self.normFunc = toFloat
        return self.getNormalized()

    #def startSampling(self,time,observation_window,get_type="raw",time_unit=MILLIS):
    #    if get_type == "celsius":
    #        self.normFunc = toCelsius
    #    elif get_type == "float":
    #        self.normFunc = toFloat
    #    super().startSampling(time,observation_window,"norm",time_unit)

temperature = TemperatureSensor()

####

class MicrophoneSensor(analogSensors.AnalogSensor):
    """
    ======================
    MicrophoneSensor class
    ======================
    
    .. class:: MicrophoneSensor
    
        This class provides a default getFloat() normalization method for the microphone.

        An instance of the class is available by calling zerynthshield.microphone attribute.

        zerynthshield.microphone.skipEval (see Sensor class) is set to true because of the
        high sampling frequencies that may be needed by the sensor.
    
    """
    def __init__(self):
        analogSensors.AnalogSensor.__init__(self,microphone_pin)
        self.normName = None

    def getFloat(self):
        """
        .. method:: getFloat()
        
            Returns samples normalized between 0 and 1.
        """
        if not self.normName == "float":
            self.normName = "float"
            self.normFunc = toFloat
        return self.getNormalized()

microphone = MicrophoneSensor()
microphone.skipEval = True

####

# class IRReceiver():

#     def __init__(self):
#         self.pin = irreceiver_pin

#     def capture(self,max_samples,time_window):
#         return icu.capture(self.pin,LOW,max_samples,time_window,pull=HIGH)

# irreceiver = IRReceiver()
