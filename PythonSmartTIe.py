# By John Gallaugher https://gallaugher.com  Twitter: @gallaugher  YouTube: bit.ly/GallaugherYouTube
#
# Portions of the LED code adapted from the great tutorial for the
# Animated NeoPixel Glow Fur Scarf - tutorial by Erin St. Blaine & Michael Sklar at:
# https://learn.adafruit.com/animated-neopixel-gemma-glow-fur-scarf
#
# Meant to be used with an Adafruit CircuitPlayground Express Bluefruit (CPXb)
# and the free Adafruit Bluefruit app (only tested on iOS but Android should work).
# To use:
#  - Save this code on the CircuitPlayground Express Bluefruit
#  - Run the Bluefruit app
#  - Press "Connect" on the CPXb from the app's device list listed. It should begin with CIRCUITPY
#  - Select "Controller"
#  - Select Color Picker, choose a color, and press the "Send Selected Color" button to set
#    all colors on the tie
#  - If you return to the controller "< Controller" in upper-right, you can select "Control Pad"
#  - #1 does a "Larson Scan" Battlestar Galactica-style back & forth light in selected color
#  - #2 does a pulsing blue in and out fade_color
#  - #3 pulses through Red and Gold (closest I could get to Maroon & Gold - my Uni's colors)
#  - #4 does a rainbow_stripe pulsing strobe. Cue the EDM music.
#  - Up arrow stops animations & shows a single light in the selected color.
#    if the light is already showing, it will move the light "up" until it reaches the "top" of the tie.
#  - Down arrow stops animations & shows a single light in the selected color.
#    if the light is already showing, it will move the light "down" until it reaches the "bottom" of the tie.
#  - Left and Right arrows run the Larson Scan animation faster (right) or slower (left)

import adafruit_fancyled.adafruit_fancyled as fancy
import board
import neopixel
import digitalio
import time
from digitalio import DigitalInOut, Direction, Pull
from adafruit_ble.uart_server import UARTServer

from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.color_packet import ColorPacket
from adafruit_bluefruit_connect.button_packet import ButtonPacket

uart_server = UARTServer()
run_animation = False
animation_number = -1

led_pin = board.A1  # which pin your pixels are connected to
num_leds = 5  # how many LEDs you have
brightness = 1.0  # 0-1, higher number is brighter
saturation = 255  # 0-255, 0 is pure white, 255 is fully saturated color
steps = 0.01  # how wide the bands of color are.
offset = 0  # cummulative steps
fadeup = True  # start with fading up - increase steps until offset reaches 1

# initialize list with all pixels off
palette = [0] * num_leds

# This is where any attempt to move a pixel will start
light_position = -1

# Time between flashes in the larson routine
wait_time = 0.1
wait_increment = 0.02
min_wait_time = 0.02
max_wait_time = 1.0

# set an initial color to use in case the user uses arrows before choosing a color. 
color = [0, 0, 255] # Bright Blue
fade_color = [0, 0, 64] # Deeper Blue

# Declare a NeoPixel object on led_pin with num_leds as pixels
# No auto-write.
# Set brightness to max.
# We will be using FancyLED's brightness control.

# "pixels" will refer to the cpx's 10 onboard neopixels
# pixel = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.2, auto_write=False)
# "strip" will refer to neopixel strand attached to the cpx, with data pin at A1
strip = neopixel.NeoPixel(led_pin, num_leds, brightness=1, auto_write=False)

ledmode = 0  # button press counter, switch color palettes
button = digitalio.DigitalInOut(board.BUTTON_A)
button.switch_to_input(pull=digitalio.Pull.DOWN)

# FancyLED allows for assigning a color palette using these formats:
# * The first (5) palettes here are mixing between 2-elements
# * The last (3) palettes use a format identical to the FastLED Arduino Library
# see FastLED - colorpalettes.cpp

# Erin St. Blaine offers these colors in her tutorial
# https://learn.adafruit.com/animated-neopixel-gemma-glow-fur-scarf/circuitpython-code
# I don't use them all, so feel free to experiment.

blue = [fancy.CRGB(0, 0, 0),
          fancy.CRGB(75, 25, 255)]

forest = [fancy.CRGB(0, 255, 0),  # green
          fancy.CRGB(255, 255, 0)]  # yellow

ocean = [fancy.CRGB(0, 0, 255),  # blue
         fancy.CRGB(0, 255, 0)]  # green

purple = [fancy.CRGB(160, 32, 240),  # purple
          fancy.CRGB(238, 130, 238)]  # violet

# An approximation of Maroon & Gold - my school colors
school_colors = [fancy.CRGB(215, 0, 0),  # purple
          fancy.CRGB(255, 215, 0)]  # violet

all_colors = [fancy.CRGB(0, 0, 0),  # black
              fancy.CRGB(255, 255, 255)]  # white

washed_out = [fancy.CRGB(0, 0, 0),  # black
              fancy.CRGB(255, 0, 255)]  # purple

rainbow = [0xFF0000, 0xD52A00, 0xAB5500, 0xAB7F00,
           0xABAB00, 0x56D500, 0x00FF00, 0x00D52A,
           0x00AB55, 0x0056AA, 0x0000FF, 0x2A00D5,
           0x5500AB, 0x7F0081, 0xAB0055, 0xD5002B]

rainbow_stripe = [0xFF0000, 0x000000, 0xAB5500, 0x000000,
                  0xABAB00, 0x000000, 0x00FF00, 0x000000,
                  0x00AB55, 0x000000, 0x0000FF, 0x000000,
                  0x5500AB, 0x000000, 0xAB0055, 0x000000]

heat_colors = [0x330000, 0x660000, 0x990000, 0xCC0000, 0xFF0000,
               0xFF3300, 0xFF6600, 0xFF9900, 0xFFCC00, 0xFFFF00,
               0xFFFF33, 0xFFFF66, 0xFFFF99, 0xFFFFCC]

# mimics a larson scanner like Cylons in battlestar galactica
def larson():
    for i in range(0, num_leds+1):
        if i-2 >= 0 and i-2 <= num_leds-1:
            strip[i-2] = ([0, 0, 0])
        if i-1 >= 0 and i-1 <= num_leds-1:
            strip[i-1] = (fade_color)
        if i >= 0 and i <= num_leds-1:
            strip[i] = (color)
        strip.write()
        time.sleep(wait_time)

    for i in range(num_leds-1, -2, -1):
        if i+2 <= num_leds-1 and i+2 >= 0:
            strip[i+2] = ([0, 0, 0])
        if i+1 <= num_leds-1 and i+1 >= 0:
            strip[i+1] = (fade_color)
        if i <= num_leds-1 and i >= 0:
            strip[i] = (color)
        strip.write()
        time.sleep(wait_time)

    # turn off pixel 0 so it doesn't linger
    strip[0] = ([0, 0, 0])
    strip.write()

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if (pos < 0) or (pos > 255):
        return (0, 0, 0)
    if pos < 85:
        return (int(pos * 3), int(255 - (pos * 3)), 0)
    elif pos < 170:
        pos -= 85
        return (int(255 - pos * 3), 0, int(pos * 3))
    else:
        pos -= 170
        return (0, int(pos * 3), int(255 - pos * 3))

def remapRange(value, leftMin, leftMax, rightMin, rightMax):
    # this remaps a value fromhere original (left) range to new (right) range
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (int)
    valueScaled = int(value - leftMin) / int(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return int(rightMin + (valueScaled * rightSpan))

def schoolColors(offset, fadeup, palette):
    blank = [0, 0, 0]
    color1 = [100, 0, 0]
    color2 = [100, 30, 0]
    strip.fill(blank)
    strip.write()

    strip.fill(color1)
    strip.write()
    time.sleep(0.2)
    strip.fill(blank)
    strip.write()
    time.sleep(0.15)
    strip.fill(color1)
    strip.write()
    time.sleep(0.2)
    strip.fill(blank)
    strip.write()
    time.sleep(1.0)

    strip.fill(color2)
    strip.write()
    time.sleep(0.2)
    strip.fill(blank)
    strip.write()
    time.sleep(0.2)
    strip.fill(color2)
    strip.write()
    time.sleep(0.2)
    strip.fill(blank)
    strip.write()
    time.sleep(1.0)


def buttonAnimation(offset, fadeup, palette):
    # for x in range(0, 200):
    if ledmode != 0: # if not larson
        for i in range(num_leds):
            color = fancy.palette_lookup(palette, offset + i / num_leds)
            color = fancy.gamma_adjust(color, brightness=brightness)
            strip[i] = color.pack()
        strip.show()

        if fadeup:
            offset += steps
            if offset >= 1:
                fadeup = False
        else:
            offset -= steps
            if offset <= 0:
                fadeup = True
        return offset

while True:
    uart_server.start_advertising()
    while not uart_server.connected:
        pass

    # Now we're connected

    while uart_server.connected:
        if uart_server.in_waiting:
            packet = Packet.from_stream(uart_server)
            if isinstance(packet, ColorPacket):
                run_animation = False
                animation_number = 0
                strip.fill(packet.color)
                strip.write()
                color = packet.color
                # the // below will drop any remainder so the values remain Ints, which color needs
                fade_color = (color[0]//2, color[1]//2, color[2]//2)
                # reset light_position after picking a color
                light_position = -1

            if isinstance(packet, ButtonPacket):
                if packet.pressed:
                    if packet.button == ButtonPacket.BUTTON_1:
                        animation_number = 5
                        run_animation = True
                    elif packet.button == ButtonPacket.BUTTON_2:
                        animation_number = 2
                        palette = blue
                        run_animation = True
                        ledmode = 2
                    elif packet.button == ButtonPacket.BUTTON_3:
                        animation_number = 3
                        palette = school_colors
                        run_animation = True
                        ledmode = 3
                    elif packet.button == ButtonPacket.BUTTON_4:
                        animation_number = 4
                        run_animation = True
                        palette = rainbow_stripe
                        ledmode = 4
                        buttonAnimation(offset, fadeup, palette)
                    elif packet.button == ButtonPacket.UP or packet.button == ButtonPacket.DOWN:
                        animation_number = 0
                        run_animation = False
                        # The UP or DOWN button was pressed.
                        increase_or_decrease = 1
                        if packet.button == ButtonPacket.DOWN:
                            increase_or_decrease = -1
                        light_position += increase_or_decrease
                        if light_position >= len(strip):
                            light_position = len(strip)-1
                        if light_position <= -1:
                            light_position = 0
                        strip.fill([0, 0, 0])
                        strip[light_position] = color
                        strip.show()
                    elif packet.button == ButtonPacket.RIGHT:
                        # The RIGHT button was pressed.
                        wait_time = wait_time - wait_increment
                        if wait_time <= min_wait_time:
                            wait_time = min_wait_time
                        animation_number = 1
                        run_animation = True
                        # reset light_position after animation
                        light_position = -1
                    elif packet.button == ButtonPacket.LEFT:
                        # The LEFT button was pressed.
                        wait_time = wait_time + wait_increment
                        if wait_time >= max_wait_time:
                            wait_time = max_wait_time
                        animation_number = 1
                        run_animation = True
                        # reset light_position after animation
                        light_position = -1

        if run_animation == True:
            if animation_number == 1:
                larson()
            elif animation_number == 2 or animation_number == 3 or animation_number == 4:
                offset = buttonAnimation(offset, fadeup, palette)
            elif animation_number == 5:
                schoolColors(offset, fadeup, palette)

    # If we got here, we lost the connection. Go up to the top and start
    # advertising again and waiting for a connection.
