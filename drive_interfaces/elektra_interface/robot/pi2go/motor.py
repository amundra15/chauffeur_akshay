# Pi2Go basic motor sketch - for the first episode of my robot tutorial series.
# In truth this program is very simple - the parts where it captures key presses is the daunting bit.
# Try to work through it slowly and you'll soon understand!

# Use the arrow keys to control the direction of the Pi2Go and use the 'greater than' and 'less than'
# keys to edit the speed!

import pi2go, time
from time import sleep
import socket
# Reading a button press from your keyboard, don't worry about this too much!
import sys
import tty
import termios
#from ultra import degree
#from ultra.py import *

UP = 0
DOWN = 1
RIGHT = 2
LEFT = 3

turnflag = 's'

UDP_IP = "10.42.0.144"
UDP_PORT = 5009

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

def readchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    if ch == '0x03':
        raise KeyboardInterrupt
    return ch

def readkey(getchar_fn=None):
    getchar = getchar_fn or readchar
    c1 = getchar()
    if ord(c1) != 0x1b:
        return c1
    c2 = getchar()
    if ord(c2) != 0x5b:
        return c1
    c3 = getchar()
    return ord(c3) - 65  # 0=Up, 1=Down, 2=Right, 3=Left arrows

# End of the functions that read your keyboard

speed = 0 #start with zero speed
roll = 100 #to discretize turn.
pi2go.init()

# Main body of code - this detects your key press and changes direction depending on it
try:
    while True:
        #keyp = readkey()	#uncomment to receive command from keyboard
        keyp, addr = sock.recvfrom(1024)	#uncomment to receive command from algo.
        #print "received"

        if keyp == 'w' or keyp == UP:			#wont be used
            pi2go.forward(speed)
            print 'Forward', speed
        elif keyp == 's' or keyp == DOWN:		#wont be used
            pi2go.reverse(speed)
            print 'Backward', speed

        elif keyp == 'd' or keyp == RIGHT:
            pi2go.spinRight(speed, roll)
            #pi2go.forward(speed)
            print 'Spin Right', roll
            print 'turnspeed', speed
            turnflag = 'r'
            #print 'turnflag' , turnflag
        elif keyp == 'a' or keyp == LEFT:
            pi2go.spinLeft(speed, roll)
            #pi2go.forward(speed)
            print 'Spin Left', roll
            print 'turnspeed',  speed
            turnflag = 'l'
            #print 'turnflag' , turnflag

        elif keyp == 'h': 
            speed = 0
            pi2go.forward(speed)
            print 'Car stopped'
        elif keyp == 'r':
            speed = 40
            pi2go.forward(speed)
            print 'Car resumed'


        elif keyp == '.' or keyp == '>':		#wont be used
            speed = min(100, speed+10)
            print 'Speed+', speed
        elif keyp == ',' or keyp == '<':		#wont be used
            speed = max (0, speed-10)
            print 'Speed-', speed


        elif keyp == 'x':
    		if turnflag == 'l':				#Wheel at left
			print 'Spin right to centre'
			pi2go.spinRight(speed, roll)
                        time.sleep(0.21)		#0.9 for road, 0.21 when in air
                        pi2go.forward(speed)
                        turnflag = 's'

                elif turnflag == 'r':				#Wheel at right
			print 'Spin left to centre'
			pi2go.spinLeft(speed, roll)
                        time.sleep(0.21)		#0.9 for road, 0.21 when in air
                        pi2go.forward(speed)
                        turnflag = 's'

        elif keyp == ' ':
            pi2go.stop()
            print 'Stop'

        elif keyp == 'c':
            pi2go.turnstop()
            print 'turnstop'

        elif ord(keyp) == 3:
            break

# When you want to exit - press ctrl+c and it will generate a keyboard interrupt - this is handled nicely here!
except KeyboardInterrupt:
    pi2go.cleanup()
