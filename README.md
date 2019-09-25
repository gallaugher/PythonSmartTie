# PythonSmartTie
# Be sure to save this code as code.py on your CircuitPlayground Express Bluefruit device.
CircuitPython Code to use a Bluefruit app to control a Neopixel strand. Used in a wearable "smart tie" project.
By John Gallaugher https://gallaugher.com  Twitter: @gallaugher  YouTube: bit.ly/GallaugherYouTube

Portions of the LED code adapted from the great tutorial for the 
Animated NeoPixel Glow Fur Scarf - tutorial by Erin St. Blaine & Michael Sklar at:
https://learn.adafruit.com/animated-neopixel-gemma-glow-fur-scarf

Meant to be used with an Adafruit CircuitPlayground Express Bluefruit (CPXb)
Created when only the Alpha version was available, but seems to work fine.
https://www.adafruit.com/product/4333

and the free Adafruit Bluefruit app (only tested on iOS but Android should work).
To use:
 - Save this code on the CircuitPlayground Express Bluefruit
 - Run the Bluefruit app
 - Press "Connect" on the CPXb from the app's device list listed. It should begin with CIRCUITPY
 - Select "Controller"
 - Select Color Picker, choose a color, and press the "Send Selected Color" button to set
   all colors on the tie
 - If you return to the controller "< Controller" in upper-right, you can select "Control Pad"
 - #1 does a "Larson Scan" Battlestar Galactica-style back & forth light in selected color
 - #2 does a pulsing blue in and out fade_color
 - #3 pulses through Red and Gold (closest I could get to Maroon & Gold - my Uni's colors)
 - #4 does a rainbow_stripe pulsing strobe. Cue the EDM music.
 - Up arrow stops animations & shows a single light in the selected color.
   if the light is already showing, it will move the light "up" until it reaches the "top" of the tie.
 - Down arrow stops animations & shows a single light in the selected color.
   if the light is already showing, it will move the light "down" until it reaches the "bottom" of the tie.
 - Left and Right arrows run the Larson Scan animation faster (right) or slower (left)
