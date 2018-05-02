IR Capture, Decode and Send
==============================

Basics example showing how to capture IR packet and decode them.
The IR capture is performed through an IR demodulator connected to a pin empowered with ICU feature.
Once decoded, captured packet can be printed on the console or sent through an IR LED connected to a pin empowered with PWM feature.

At the current stage the Zerynth Infrared library decode only Samsung and NEC protocols. Other protocols will be added soon.
However, any captured packet can be stored and sent as raw packet without requiring a specific protocol decoder.

