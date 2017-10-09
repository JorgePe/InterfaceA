#!/usr/bin/env python3

#
# The LEGO Interface A Python Turtle
# https://youtu.be/NVY-Ho8WwiI
# http://ofalcao.pt/blog/2017/lego-interface-a-the-python-turtle
#
# This works on Ubuntu 17.04 with pylibftdi-0.16.1.2
# with a Sparkfun Breakout Board for FT232RL USB to Serial
# https://www.sparkfun.com/products/12731
#
# It defines 6 output pins and 2 input pins
# Need sudo to run or create an udev rule
#
#  To stop have to use Ctrl+C
# better press RED STOP button before start and stop the script
# to prevent leaving motors running
#

from pylibftdi import BitBangDevice
import contextlib

from time import sleep

FTDI_SN = 'A105BPBO'      # Serial Number of the FTDI device, see dmesg
DIRECTION = 0x3F          # six LSB are output(1), two MSB are input(0)

# Bit masks for each pin
OUT0 = 0x01               # TXD
OUT1 = 0x02               # RXD
OUT2 = 0x04               # RTS#
OUT3 = 0x08               # CTS#
OUT4 = 0x10               # DTR#
OUT5 = 0x20               # DSR#
INP6 = 0x40               # DCD#
INP7 = 0x80               # RI#

#COMMAND_DELAY = 0.0025
COMMAND_DELAY = 0.005
LOOP_DELAY = 0.1

def zero_all():
    # resets all output pins
    bb.port = 0x00

#
# set()
#   puts output [0..5] at high level
#

def set(b):
    if b == 0:
        bb.port |= OUT0
    elif b == 1:
        bb.port |= OUT1
    elif b == 2:
        bb.port |= OUT2
    elif b == 3:
        bb.port |= OUT3
    elif b == 4:
        bb.port |= OUT4
    elif b == 5:
        bb.port |= OUT5


#
# reset()
#   puts output [0..5] at low level
#

def reset(b):
    if b == 0:
        bb.port &= (0xFF - OUT0)
    elif b == 1:
        bb.port &= (0xFF - OUT1)
    elif b == 2:
        bb.port &= (0xFF - OUT2)
    elif b == 3:
        bb.port &= (0xFF - OUT3)
    elif b == 4:
        bb.port &= (0xFF - OUT4)
    elif b == 5:
        bb.port &= (0xFF - OUT5)

#
# toggle()
#   changes output [0..5] state
#

def toggle(b):
    # b is the index of the bit to toggle (0 to 5)
    if b == 0:
        if (bb.port & OUT0) == OUT0:
            bb.port &= (0xFF-OUT0)     # clear
        else:
            bb.port |= OUT0            # set
    elif b == 1:
        if (bb.port & OUT1) == OUT1:
            bb.port &= (0xFF-OUT1)     # clear
        else:
            bb.port |= OUT1            # set
    elif b == 2:
        if (bb.port & OUT2) == OUT2:
            bb.port &= (0xFF-OUT2)     # clear
        else:
            bb.port |= OUT2            # set
    elif b == 3:
        if (bb.port & OUT3) == OUT3:
            bb.port &= (0xFF-OUT3)     # clear
        else:
            bb.port |= OUT3            # set
    elif b == 4:
        if (bb.port & OUT4) == OUT4:
            bb.port &= (0xFF-OUT4)     # clear
        else:
            bb.port |= OUT4            # set
    elif b == 5:
        if (bb.port & OUT5) == OUT5:
            bb.port &= (0xFF-OUT5)     # clear
        else:
            bb.port |= OUT5            # set


#
# bridge()
#   i.e. a pair of ports
#   possible pairs: A = OUT 0+1, B=2+3, C=4+5
#   possible commands: L(eft), R(ight), B(reak), C(oast)
#   not sure if Break acts different of Coast
#

def bridge(pair, command):

    if pair == 'A':
        if command == 'L':
            # set 0 and reset 1
            set(0)
            reset(1)
        elif command == 'R':
        # reset 0 and set 1
            reset(0)
            set(1)
        elif command == 'B':
        # set 0 and 1
            set(0)
            set(1)
        elif command == 'C':
        # reset 0 and 1
            reset(0)
            reset(1)
    elif pair == 'B':
        if command == 'L':
            # set 2 and reset 3
            set(2)
            reset(3)
        elif command == 'R':
        # reset 2 and set 3
            reset(2)
            set(3)
        elif command == 'B':
        # set 2 and 3
            set(2)
            set(3)
        elif command == 'C':
        # reset 2 and 3
            reset(2)
            reset(3)
    elif pair == 'C':
        if command == 'L':
            # set 4 and reset 5
            set(4)
            reset(5)
        elif command == 'R':
        # reset 4 and set 5
            reset(4)
            set(5)
        elif command == 'B':
        # set 4 and 5
            set(4)
            set(5)
        elif command == 'C':
        # reset 0 and 1
            reset(0)
            reset(1)


#
# turtle()
#   a turtle has 2 motors (bridge A and B)
#   and 1 optosensor at Input 6
#

def turtle_front():
    bridge('A', 'L')
    bridge('B', 'L')
    sleep(COMMAND_DELAY)
    bridge('A', 'C')
    bridge('B', 'C')


def turtle_back():
    bridge('A', 'R')
    bridge('B', 'R')
    sleep(COMMAND_DELAY)
    bridge('A', 'C')
    bridge('B', 'C')


def turtle_left():
    bridge('A', 'L')
    bridge('B', 'R')
    sleep(COMMAND_DELAY)
    bridge('A', 'C')
    bridge('B', 'C')


def turtle_right():
    bridge('A', 'R')
    bridge('B', 'L')
    sleep(COMMAND_DELAY)
    bridge('A', 'C')
    bridge('B', 'C')


# Main

# auto_detach = False is needed as a workaround to prevent
# segmentation faults when accessing the FTDI device
# see pylibftdi issue #25

bb = BitBangDevice(FTDI_SN, auto_detach=False)
bb.direction = DIRECTION

zero_all()

#
# optosensor only detects black to white transition
# loop left-front until inp6 off then right a bit
#


while True:

    # Poll inputs
    read = bb.port
#        print('IN7:', '1' if (read & INP7) == INP7 else '0',
#              ' IN6:', '1' if (read & INP6) == INP6 else '0', '\r', end='')
    if read & INP6 == INP6:
        inp6 = '1'
    else:
        inp6 = '0'

    if read & INP7 == INP7:
        inp7 = '1'
    else:
        inp7 = '0'

    if inp6 == '0':
        # transition B-W or just over B
        # right a bit
        turtle_right()
        turtle_right()
        turtle_right()
        turtle_right()
        turtle_right()
        turtle_right()
    else:
        # white
        #  front and left a bit
        turtle_front()
        turtle_left()

    sleep(LOOP_DELAY)
