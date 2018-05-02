"""
.. _digitalSensor

.. module: digitalSensor

**********************
Digital Sensor Library
**********************

This module contains class definitions for digital sensors. DigitalSensor class is a subclass of the generic Sensor class and provides a simple way to handle sensors sensing quantities that can assume only two different values.

Every DigitalSensor instance inherits the whole set of methods from generic Sensor class and it also implements the following methods:

    * onSequence: see method :ref:`onSequence <onSequence>`
    * onRiseAndFall: see method :ref:`onRiseAndFall <onRiseAndFall>`
    * onFallAndRise: see method :ref:`onFallAndRise <onFallAndRise>`
    * onRise: alias for onPinRise on the instance pin
    * onFall: alias for onPinFall on the instance pin

An instance of a digitalSensor can be used both in interrupt mode and sampling mode.
    """

import timers
from smartsensors import sensors

class DigitalSensor(sensors.Sensor):
    """
    ==================
    DigitalSensor class
    ==================
    
    .. class:: DigitalSensor(pin)
    
        This is the class for handling digital sensors and any other boolean input connected to digital pins.   

    """

    def __init__(self,pin):
        sensors.Sensor.__init__(self)
        pinMode(pin,INPUT)
        self.pin = pin
        self.storeAverage = True
        self.highPrecision = True
        self._readFunc = digitalRead
        self._onPinEdges = [ onPinRise, onPinFall ]
        self._sequenceFunctions = None
        self._sequenceLongFunction = None
        self._sequenceTimes = None
        self._resetSamplingParams()

    def _sequenceReset(self):
        self._sequenceStep = 0
        self._timerMax = None
        self._timerMin = None
        self._onPinEdges[self._sequenceStart](self.pin,self._startTimerMin)

    def _checkTiming(self):
        if type(self._timerMax) == 0:
            self._sequenceLongFunction()
            self._sequenceReset()
        if self._timerMin:
            self._timerMin.cancel()
            self._sequenceReset()
            return
        self._timerMax.clear()
        self._timerMax = None
        # valid timing
        if self._sequenceFunctions[self._sequenceStep]:
            self._sequenceFunctions[self._sequenceStep]()
        if (self._sequenceStep+1 <= self._sequenceLength):
            self._sequenceStep += 1
            self._startTimerMin()
        else:
            self._sequenceReset()

    def _markTimerMax(self):
        self._timerMax = 1

    def _startTimerMax(self):
        self._timerMin = None
        self._timerMax = timers.timer()
        if self._sequenceLongFunction and self._sequenceStep == 0:
            self._timerMax.one_shot(self._sequenceTimes[self._sequenceStep][1],self._markTimerMax)
        else:
            self._timerMax.one_shot(self._sequenceTimes[self._sequenceStep][1],self._sequenceReset)

    def _startTimerMin(self):
        self._timerMin = timers.timer()
        self._timerMin.one_shot(self._sequenceTimes[self._sequenceStep][0],self._startTimerMax)
        curr_edge = (((self._sequenceStart + self._sequenceStep)%2)^1)
        self._onPinEdges[curr_edge](self.pin,self._checkTiming)

    def onSequence(self,first,times,to_dos,long_fn = None):
        """
        .. _onSequence:

        .. method:: onSequence(first,times,to_dos,long_fn)
        
        Sets functions to be executed in a sequence of pin values changes respecting precise time constraints.
        
        
        * first: is the value of the pin from which the method waits for the first change
        * times: is a list of min and max times of persistence in a precise state before changing it to opposite one
        * to_dos: is a list of functions to be executed at every step of the sequence
        * long_fn: is a function to be executed if the first max time constraint is exceeded
         
        Example::
        
            def hello():
                print("hello")
            def world():
                print("world")
            def longworld():
                print("longworld")

            mySensor.onSequence(0,[[15,30],[15,30]],[hello,world],longworld)

        Assuming to start from a 0 value on the pin, when the value changes to 1, a timer starts to check the
        persistance in this state. When the value returns to 0, if the time passed in a HIGH state is:

            * less than 15 milliseconds the sequence restarts
            * more than 30 milliseconds *longworld* function is called and then the sequence restarts
            * between 15 and 30 milliseconds the function *hello* is executed and the sequence goes on.
              For the second step the same assumptions are valid: if the time constraints are respected
              *world* function is called, otherwise the sequence restarts ( long_fn is called only if the
              first max bound is not respected ). To be noticed that the second step analyze the persistance
              at **LOW** level in this case.
        
        
        """
        self._sequenceLength = len(times)-1
        self._sequenceTimes = times
        self._sequenceFunctions = to_dos
        self._sequenceLongFunction = long_fn
        self._sequenceStart = first
        self._sequenceReset()

    def onRiseAndFall(self,min_time,max_time,to_do,long_fn = None):
        """
        .. _onRiseAndFall:

        .. method:: onRiseAndFall(min_time,max_time,to_do,long_fn = None)
        
        Sets *to_do* as the function to be executed when the value of the pin changes from 0 to 1 ( onRise ) and again from 1 to 0 ( andFall ).
        The value must stay HIGH at least *min_time* (make sure the transition is voluntary, not due to noise) and less than *max_time*.
        
        There is the possibility to also set a *long_fn* which is executed is the *max_time* bound is overcome.
        
        * min_time: the minimum duration of the signal to be considered as a real event
        * max_time: the maximum duration of the signal that if passed will trigger a "long" event 
        * to_do: the function called if the signal state change is between min and max time
        * long_fn: the function called if the signal state change is longer than max time
        """
        self.onSequence(0,[[min_time,max_time]],[to_do],long_fn)

    def onFallAndRise(self,min_time,max_time,todo,long_fn = None):
        """
        .. _onFallAndRise:

        .. method:: onFallAndRise(min_time,max_time,to_do,long_fn = None)
        
        Sets *to_do* as the function to be executed when the value of the pin changes from 1 to 0 ( onFall ) and again from 0 to 1 ( andRise ).
        The value must stay LOW at least *min_time* (make sure the transition is voluntary, not due to noise) and less than *max_time*.
        
        There is the possibility to also set a *long_fn* which is executed if the *max_time* bound is overcome.
        
        * min_time: the minimum duration of the signal to be considered as a real event
        * max_time: the maximum duration of the signal that if passed will trigger a "long" event 
        * to_do: the function called if the signal state change is between min and max time
        * long_fn: the function called if the signal state change is longer than max time
        """
        self.onSequence(1,[[min_time,max_time]],[todo],long_fn)

    def onRise(self,todo):
        onPinRise(self.pin,todo)

    def onFall(self,todo):
        onPinFall(self.pin,todo)
