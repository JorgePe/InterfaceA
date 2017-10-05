#!/usr/bin/env python3

#
# This works on Ubuntu 17.04 with pylibftdi-0.16.1.2
# with a Sparkfun Breakout Board for FT232RL USB to Serial
# https://www.sparkfun.com/products/12731
#
# It defines 6 output pins and 2 input pins
# Keyboard keys '1' to '5' are used to toggle the state of
# the output pins while the state of the input pins is
# constantly being polled
#
# The curses part was almost just copy&paste from the Web
# I'm sure code could be much more simpler and cleaner
#
# Need sudo to run or create an udev rule
#

from pylibftdi import BitBangDevice
import contextlib


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


class CursesKeyboard(object):
    def __init__(self):
        import curses
        self.key = curses.initscr()
        curses.cbreak()
        curses.noecho()
        self.key.keypad(1)
        self.key.nodelay(1)

    def read(self):
        return self.key.getch()

    def read_code(self):
        c = self.key.getch()
        if c > -1:
            return chr(c)
        return ""

    def close(self):
        import curses
        curses.nocbreak()
        self.key.keypad(0)
        curses.echo()
        curses.endwin()

    def __del__(self):
        try:
            self.close()
        except:
            pass


def zero_all():
    # resets all output pins
    bb.port = 0x00


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


def bridge(pair, command):
    # possible pairs: A = OUT 0+1, B=2+3, C=4+5
    # possible commands: L(eft), R(ight), B(reak), C(oast)
    if pair == 'A':
        if command == 'L':
            # set 0 and reset 1
            bb.port |= OUT0
            bb.port &= (0xFF - OUT1)
        elif command == 'R':
        # reset 0 and set 1
            bb.port &= (0xFF - OUT0)
            bb.port |= OUT1
        elif command == 'B':
        # set 0 and 1
            bb.port |= OUT0
            bb.port |= OUT1
        elif command == 'C':
        # reset 0 and 1
            bb.port &= (0xFF - OUT0)
            bb.port &= (0xFF - OUT1)
    elif pair == 'B':
        if command == 'L':
            # set 2 and reset 3
            bb.port |= OUT2
            bb.port &= (0xFF - OUT3)
        elif command == 'R':
        # reset 2 and set 3
            bb.port &= (0xFF - OUT2)
            bb.port |= OUT3
        elif command == 'B':
        # set 2 and 3
            bb.port |= OUT2
            bb.port |= OUT3
        elif command == 'C':
        # reset 2 and 3
            bb.port &= (0xFF - OUT2)
            bb.port &= (0xFF - OUT3)
    elif pair == 'C':
        if command == 'L':
            # set 4 and reset 5
            bb.port |= OUT4
            bb.port &= (0xFF - OUT5)
        elif command == 'R':
        # reset 4 and set 5
            bb.port &= (0xFF - OUT4)
            bb.port |= OUT5
        elif command == 'B':
        # set 4 and 5
            bb.port |= OUT4
            bb.port |= OUT5
        elif command == 'C':
        # reset 0 and 1
            bb.port &= (0xFF - OUT4)
            bb.port &= (0xFF - OUT5)


@contextlib.contextmanager
def keyboard_context():
    keyboard = CursesKeyboard()
    yield keyboard
    keyboard.close()
    zero_all()


# Main

# auto_detach = False is needed as a workaround to prevent
# segmentation faults when accessing the FTDI device
# see pylibftdi issue #25

bb = BitBangDevice(FTDI_SN, auto_detach=False)
bb.direction = DIRECTION

zero_all()
counter6 = 0
counter7 = 0

print("Use keys '1', '2', '3', '4', '5', '6' or [ASZX], [DFCV], [GHBN] or '0' or 'Q/ESC'")

with keyboard_context() as keys:
    while True:

        k = keys.read()

        # Toggle Commands for individual outputs
        if k == ord('1'):
            toggle(0)
        elif k == ord('2'):
            toggle(1)
        elif k == ord('3'):
            toggle(2)
        elif k == ord('4'):
            toggle(3)
        elif k == ord('5'):
            toggle(4)
        elif k == ord('6'):
            toggle(5)

        # Bridge Commands for pairs of outputs

        # pair A
        elif k == ord('A') or k == ord('a'):
            bridge('A','L')
        elif k == ord('S') or k == ord('s'):
            bridge('A','R')
        elif k == ord('Z') or k == ord('z'):
            bridge('A','C')
        elif k == ord('X') or k == ord('x'):
            bridge('A','B')

        # pair B
        elif k == ord('D') or k == ord('d'):
            bridge('B','L')
        elif k == ord('F') or k == ord('f'):
            bridge('B','R')
        elif k == ord('C') or k == ord('c'):
            bridge('B','C')
        elif k == ord('V') or k == ord('v'):
            bridge('B','B')

        # pair C
        elif k == ord('G') or k == ord('g'):
            bridge('C','L')
        elif k == ord('H') or k == ord('h'):
            bridge('C','R')
        elif k == ord('B') or k == ord('b'):
            bridge('C','C')
        elif k == ord('N') or k == ord('n'):
            bridge('C','B')

        # reset counters
        elif k == ord('0'):
            counter6 = 0
            counter7 = 0

        # Quit with q/Q/ESC
        # Try not to use Ctrl+C, terminal could became 'strange'
        elif k == ord('Q') or k == ord('q') or k == 27:
            break

        # Poll inputs
        read = bb.port
#        print('IN7:', '1' if (read & INP7) == INP7 else '0',
#              ' IN6:', '1' if (read & INP6) == INP6 else '0', '\r', end='')
        if read & INP6 == INP6:
            inp6 = '1'
        else:
            counter6 += 1
            inp6 = '0'

        if read & INP7 == INP7:
            inp7 = '1'
        else:
            counter7 += 1
            inp7 = '0'

        print('IN7: ', inp7, 'IN6: ', inp6, ' Counters 7: ', counter7, '6: ', counter6, '          \r', end='')