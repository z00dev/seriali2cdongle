"""
.. module:: rtttl

*************
RTTTL Library
*************

This module contains class definitions for the “RTTTL” melody player to be used for driving buzzers or speakers connected to PWM pins.

The format of RTTTL notation is similar to the Music Macro Language found in BASIC implementations present on many early microcomputers. Various RTTTL melodies can be founded and downloaded `here <http://ez4mobile.com/nokiatone/rtttf.htm>`_ and many other websites.
    """

import pwm

tunes = {
"b2":123,
"c3":131,
"c#3":139,
"d3":147,
"d#3":156,
"e3":165,
"f3":175,
"f#3":185,
"g3":196,
"g#3":208,
"a3":220,
"a#3":233,
"b3":247,
"c4":262,
"c#4":277,
"d4":294,
"d#4":311,
"e4":330,
"f4":349,
"f#4":370,
"g4":392,
"g#4":415,
"a4":440,
"a#4":466,
"b4":494,
"c5":523,
"c#5":554,
"d5":587,
"d#5":622,
"e5":659,
"f5":698,
"f#5":740,
"g5":784,
"g#5":831,
"a5":880,
"a#5":932,
"b5":988,
"c6":1047,
"c#6":1109,
"d6":1175,
"d#6":1245,
"e6":1319,
"f6":1397,
"f#6":1480,
"g6":1568,
"g#6":1661,
"a6":1760,
"a#6":1865,
"b6":1976,
"c7":2093,
"c#7":2217,
"d7":2349,
"d#7":2489,
"e7":2637,
"f7":2794,
"f#7":2960,
"g7":3136,
"g#7":3322,
"a7":3520,
"a#7":3729,
"b7":3951,
"c8":4186,
"c#8":4435,
"d8":4699,
"d#8":4978,
"p2":0,
"p3":0,
"p4":0,
"p5":0,
"p6":0,
"p7":0,
"p8":0
}



class tune():
    """
    .. class:: tune(txt)
    
        This is the class for creating the melody to be played by the RTTTL player.
        The melody is passed as string
    """
    def __init__(self,txt):
        fields = txt.split(":")
        self.name = fields[0]
        self.stopped = True
        self.lastnote = 0
        tmp = fields[1].strip(" ").split(",")
        self.duration = int(tmp[0].split("=")[1])
        self.octave = int(tmp[1].split("=")[1])
        self.tempo = int(tmp[2].split("=")[1])
        sng = fields[2].split(",")
        self.notes = []
        self.times = []
        for note in sng:
            d = 0
            n = ""
            m = 0
            status = 0                
            for x in note:

                if x>="1" and x<="9":
                    if status==0:
                        d=d*10+int(x)
                    else:
                        status=2
                        n=n+x
                elif x==".":
                    m = 1
                else:
                    n=n+x
                    status=1
            if d==0:
                d=self.duration
            if status==1:
                n=n+str(self.octave)
            if m==1:
                d=d+d//2
            self.notes.append(n)
            self.times.append(d)

    def stop(self):
        self.stopped=True

    def play(self,pin,callback=None,restart=False):
        """
        .. method:: play(pin,callback=None,restart=False)
        
            Starts playing the melody actuating the PWM on the selected pin.

            It is also possible to pass a function as callback that will be called every time a note is played. 
            The callback passes the played note to the called function.

            Moreover, loop play is also possible by setting the restart parameter to True.
            
            * pin: Dx.PWM, it is the pin where the buzzer is connected.
            * callback: the function to be called every time a note is played. Played note will be passed to the called function.
            * restart: it activates the playloop.
        """
        self.stopped=False
        onebeat = 60000//(self.tempo//4)
        note1 = 0
        if restart:
            note1=self.lastnote
        for i in range(note1,len(self.notes)):
            
            if self.stopped:
                self.lastnote=i
                return
            if callback:
                callback(self.notes[i])
            if tunes[self.notes[i]]==0:
                duty=0    
            else:    
                freq = 1000000//tunes[self.notes[i]]
                duty=freq//2
            pwm.write(pin,freq,duty,MICROS)
            dur=onebeat//self.times[i]
            sleep(dur)
        self.stopped=True
        pwm.write(pin,freq,0,MICROS)

    def setbpm(self,bpm):
        """
        .. method:: setbpm(bpm)
        
            Changes the melody speed.

            bpm: RTTTL melodies include tempo definition in BPM, however through this function it is possible to manually change the melody speed.
        
        """
        self.tempo=bpm




#song = tune("MacGyver:d=4,o=5,b=160:8c6,8c6,8c6,8c6,8c6,8c6,2b,8f#,8a,8p,2g,8c6,8c6,8p,b,8a,8b,8a,8g,8p,e6,a.,16p,b.,16p,c6,8b,8a,c6")


#song.play(11)
