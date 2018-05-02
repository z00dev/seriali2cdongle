"""
.. module:: sensors

.. _gen_sensors:

**********************
Generic Sensor Library
**********************

This module contains class definitions for sensors. The Sensor class provides methods for handling generic sensors connected to specific pins of a device. It also provides easily accessible attributes for useful parameters automatically evaluated during the acquisition.

Every Sensor instance implements the following methods:

    * getRaw: reads a raw value from the sensor and returns it
    * setNormFunc: sets a normalization function
    * getNormalized: reads a raw value from the sensor and returns a normalized one
    * currentSample: returns last read sample
    * previousSample: returns the last but one read sample
    * doEverySample: appends to a list a function to be executed every time a get function is called
    * resetSampleActions: resets Actions list
    * addCheck: appends to a list a couple of a condition to be checked every time a get function is called the action to be executed if the condition is verified
    * resetChek: resets Checks list
    * startSampling: sets a sampling interval
    * stopSampling: clears the sampling interval
    * wait: sleeps
    * setObservationWindow: sets the length of the window used to evaluate a set of useful parameters
    * setSamplingTime: sets the private attribute _samplingTime (use carefully)

Every Sensor instance provides the following parameters evaluated in a window of n acquisitions (both in sampling mode and simple get calls):

    * currentAverage: moving average for last n samples
    * currentDerivative: last sample minus penultimate sample, all divided by sampling time in seconds (only sampling mode)
    * currentTrend: last sample minus first sample of the window, all divided by sampling time in seconds (only sampling mode)
    * minSample: smallest sample of the window
    * maxSample: greatest sample of the window

And the following attributes to control the process of evaluation of the parameters:    

    * skipEval: if True skips the whole process of evaluation
    * storeAverage: if False skips average evaluation
    * storeTrend: if False skips trend evaluation
    * storeMinMax: if False skips min and max evaluation

"""

import timers
import hwtimers

class Sensor:
    """
    ================
    The Sensor class
    ================
    
    .. class:: Sensor
    
        This is the base class for generic sensors connected to pins
    

    """

    def __init__(self):
        self._sampleBuffer = None 
        self.storeMinMax = False
        self.storeAverage = False 
        self.storeTrend = False
        self.skipEval = False
        self._currentSample = None
        self._observationWindowN = None
        self._observationWindowT = None
        self._samplingGetType = None
        self._everySampleActions = [] 
        self.resetCheck()
        self.highPrecision = False
        self._readFunc = None
        self.normFunc  = None
        self._samplingTimer = None

    def _resetSamplingParams(self):
        """
        .. method:: _resetSamplingParams()
        
            Resets sampling parameters
        """
        self._currentBufferIndex = -1
        if self.storeAverage:
            self.currentAverage = None
        if self.storeTrend:
            self.currentTrend = None
        self.currentDerivative = None
        if self.storeMinMax:
            self.minSample = None
            self.maxSample = None
        self._samplingTime = None

    def setObservationWindow(self,n):
        """
        .. method:: setObservationWindow(n)
        
            Sets the length of the window (n) used to evaluate a set of useful parameters.
            Needed to evaluate those parameters during manual acquisition (calling getRaw/getNormalized functions), in sampling mode (entered by startSampling call) the length is given as a parameter of startSampling method.
            
            .. note:: **self._samplingTime** can be found set in:
                        
                        * sampling mode: setObservationWindow should not have been called
                        * get mode: self._samplingTime has been manually set because samplingTime dependent parameters (like trend and derivatived) are necessary in a non-sampling mode (should be very rare)
            
        """
        self._observationWindowN = n
        if self._samplingTime:
            self._observationWindowT = n*self._samplingTime

    def setSamplingTime(self,time):
        """
        .. method:: setSamplingTime(time)
        
            Manually sets _samplingTime private attribute. 

            .. warning:: **Use carefully** setObservationWindow method

            This attribute is automatically set when startSampling method is called.
        

        """
        self._samplingTime = time

    def currentSample(self):
        """
        .. _currentSample:

        .. method:: currentSample()
        
            Returns last read sample: stored as the last element of the buffer list.

            The buffer is a list of _observationWindowN elements if the window evaluation process is not skipped, as a private attribute otherwise.
        """
        if self.skipEval:
            return self._currentSample
        if self._currentBufferIndex != -1:
            return self._sampleBuffer[self._currentBufferIndex]

    def previousSample(self):
        """
        .. method:: previousSample()
        
            Returns last but one read sample: stored in the buffer list (see :ref:`currentSample <currentSample>`)
            
            .. note:: Not available if evaluation process is skipped
        """
        return self._sampleBuffer[(self._currentBufferIndex-1) % self._observationWindowN]

    def _evalParams(self,val):
#         """
#         .. method:: _evalParams(val)
        
#         Private method to evaluate window parameters ( currentAverage, currentDerivative, currentTrend, minSample, maxSample )
# based on current and last _observationWindowN read values.
#                 Controlled by boolean attributes: storeAverage, storeTrend, storeMinMax
        
#         Args:
#             val (TYPE): Description
#         """
        if self._currentBufferIndex == -1:
            self._sampleBuffer = self._observationWindowN*[None]
        self._currentBufferIndex = ((self._currentBufferIndex+1) % self._observationWindowN)
        rmSample = self.currentSample()
        #N.B.currentBufferIndex now points at oldest sample ( currentSample call )
        self._sampleBuffer[self._currentBufferIndex] = val
        if self.storeAverage:
            if self.currentAverage:
                if self.highPrecision:
                    self.currentAverage = (((self.currentAverage*self._observationWindowN)+val-rmSample)/self._observationWindowN)
                else:
                    self.currentAverage = (((self.currentAverage*self._observationWindowN)+val-rmSample)//self._observationWindowN)
            else:
                if self._currentBufferIndex == (self._observationWindowN-1):
                    if self.highPrecision:
                        self.currentAverage = (sum(self._sampleBuffer) / self._observationWindowN)
                    else:
                        self.currentAverage = (sum(self._sampleBuffer) // self._observationWindowN)
        if self.storeMinMax or self.storeTrend:
            oldestIndex  = ((self._currentBufferIndex+1) % self._observationWindowN)
            oldestSample = self._sampleBuffer[oldestIndex]
        if self._samplingTime:
            if type(self.previousSample()) != PNONE:
                if self.highPrecision:
                    self.currentDerivative = ((val - self.previousSample()) / (self._samplingTime/1000))
                else:
                    self.currentDerivative = ((val - self.previousSample()) // (self._samplingTime/1000))
            if self.storeTrend:
                if type(oldestSample) != PNONE:
                    if self.highPrecision:
                        self.currentTrend = ((val - oldestSample)/(self._observationWindowT/1000))
                    else:
                        self.currentTrend = ((val - oldestSample)//(self._observationWindowT/1000))
        if self.storeMinMax:
            if type(oldestSample) != PNONE:
                if type(self.minSample) == PNONE:
                    self.minSample = min(*self._sampleBuffer)
                    self.maxSample = max(*self._sampleBuffer)
                else:
                    ### eval min
                    if rmSample == self.minSample:
                        if val > self.minSample:
                            self.minSample = min(*self._sampleBuffer)
                        else:
                            self.minSample = val
                    else:
                        if val < self.minSample:
                            self.minSample = val
                    ### eval max
                    if rmSample == self.maxSample:
                        if val < self.maxSample:
                            self.maxSample = max(*self._sampleBuffer)
                        else:
                            self.maxSample = val
                    else:
                        if val > self.maxSample:
                            self.maxSample = val

    def _getValue(self,get_type):
#         """
# .. method:: _getValue(get_type)

#         Main acquisition method: 

#             * get_type can be "raw" or "norm" that stand respectively for raw and normalized acquisition.
#             * pin can be both real pin and a tuple containing a sensor object and a parameter to read.
#             * _evalParams is called only if skipEval is False and _observationWindowN is set
#             * _everySampleActions and current object checks are performed ( see :ref:`doEverySample <doEverySample>`, addCheck_ )
#               both passing current object to these functions.

#         """
        if type(self.pin) == 0:
            val = self._readFunc(self.pin)
        elif type(self.pin) == PTUPLE:
            if self.pin[1] == "currentAverage":
                val = getattr(self.pin[0],"currentAverage")
            elif self.pin[1] == "currentDerivative":
                val = getattr(self.pin[0],"currentDerivative")
        if type(val) != PNONE:
            if get_type == "norm":
                if not self.normFunc:
                    return False
                val = self.normFunc(val,self)
            if self.skipEval:
                self._currentSample = val
            else:
                if self._observationWindowN:
                    self._evalParams(val)

            if (len(self._everySampleActions) != 0):
                for action in self._everySampleActions:
                    action(self)
            if (len(self._checkConditions) != 0):
                self._checkCurrentObj()

        return val

    def getRaw(self):
        """
        .. method:: getRaw()
        
            Main acquisition method for raw data

        """

        return self._getValue("raw")

    def getNormalized(self):
        """
        .. method:: getNormalized()

            Main acquisition method for normalized data
        """
        return self._getValue("norm")

    
    def doEverySample(self,to_do):
        """
        .. _doEverySample:

        .. method:: doEverySample(to_do)

            Appends a function to the list of those to be executed when _getValue is called.
            
            .. note:: **_getValue** is called both in sampling and manual acquisition mode.
            
            Example::
                
                def out(obj):
                    print(obj.currentSample())

                mySensor.doEverySample(out)

                ### 'out' is executed in both cases:
                mySensor.startSampling(...)
                mySensor.getRaw()

            Returns self to allow a compact code::

                mySensor.doEverySample(out).addCheck(...).startSampling(...)
        """
        self._everySampleActions.append(to_do)
        return self

    def resetSampleActions(self):
        """
        .. method:: resetSampleActions()

            Resets _everySampleActions list
        """
        self._everySampleActions = []

    def _checkCurrentObj(self):
#         """
# .. method:: _checkCurrentObj()

#         Iterates through _checkConditions and executed _checkFunctions if they are verified
#         """
        for i in range(0,len(self._checkFunctions)):
            if self._checkConditions[i](self):
                self._checkFunctions[i](self)

    def addCheck(self,condition,to_do):
        """
        .. method:: addCheck(condition,to_do)
        
            Appends a condition to those to be checked every time _getValue is called and a function to the list of those to be executed when their conditions are verified.
                    
            'condition' must be a function that takes the current sensor object as a parameter and returns a boolean value::
            
                        def averageGreaterThanThreshold(obj):
                            if type(obj.currentAverage) != PNONE:
                                if obj.currentAverage > 50:
                                    return True
                                else:
                                    return False
                            else:
                                return False
            
            'to_do' must be a function that takes the current sensor object as a parameter and performs some actions::
            
                        def succeed(obj):
                            print("Average is greater than threshold!")
                            print(obj.currentAverage)
            
            Returns self to allow a compact code (see :ref:`doEverySample <doEverySample>`)
            

        """
        self._checkConditions.append(condition)
        self._checkFunctions.append(to_do)
        return self

    def resetCheck(self):
        """
        .. method:: resetCheck()

            Resets _checkFunctions and _checkConditions lists
        """
        self._checkFunctions = [] 
        self._checkConditions = []

    def setNormFunc(self,fn):
        """
        .. method:: setNormFunc(fn)

            Sets a normalization function. 
            A normalization function takes the last raw acquired value and the current sensor
            object as parameters. 
            Example::

                def normalizeData(val,obj):
                    return obj.scale*(val/100)

            It is recommended to use only *static* parameters stored in current object like scale factors.
            .. note:: In the object passed, obj.currentSample() returns the last but one read value because
            the buffer list is updated only after the normalization.

            Returns self to allow a compact code (see :ref:`doEverySample <doEverySample>`)
        """
        self.normFunc = fn
        return self

    def _microSample(self):
        # """
        # .. method:: _microSample()

        # Starts a loop to acquire samples every _samplingTime microseconds
        # """
        while True:
            if self._samplingTime:
                self._getValue(self._samplingGetType)
                hwtimers.sleep_micros(self._samplingTime)
            else:
                break

    def _sample(self):
        # """
        # .. method:: _sample()

        # Performs a _getValue call according to the type specified in startSampling call
        # """
        if self._samplingTime:
            self._getValue(self._samplingGetType)

    def startSampling(self,time,observation_window,get_type = "raw",time_unit = MILLIS):
        """
        .. method:: startSampling(time,observation_window,get_type,time_unit)

            Starts reading samples every _samplingTime.
            Length of _observationWindowN to evaluate window parameters, type of
            acquisition and time_unit characterize the acquisition itself.
            If no observation_window is passed the evaluation of window parameters is skipped.

            Returns self to allow a compact code (see :ref:`doEverySample <doEverySample>`)
        """
        self._samplingTime = time
        self._samplingGetType = get_type
        if type(observation_window) != PNONE:
            self._observationWindowN = observation_window
            self._observationWindowT = observation_window * time
        else:
            self.skipEval = True
        if time_unit == MILLIS:
            self._samplingTimer = timers.timer()
            self._samplingTimer.interval(self._samplingTime,self._sample)
        elif time_unit == MICROS:
            thread(self._microSample)
        return self

    def stopSampling(self):
        """
        .. method:: stopSampling()

            Depending on mode:

                * sampling mode: clears timer interval and stops sampling
                * non sampling mode: resets sampling parameters
            
            Returns self to allow a compact code (see :ref:`doEverySample <doEverySample>`)
        """
        if self._samplingTimer:
            self._samplingTimer.clear()
        self._resetSamplingParams()
        return self

    def wait(self,time):
        """
        .. method:: wait(time)

            Sleeps for *time* milliseconds and returns self to allow a compact code::

            mySensor.doEverySample(out).startSampling(...).wait(5000).stopSampling()
        """
        sleep(time)
        return self

