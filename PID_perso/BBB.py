#!/usr/bin/python

from optparse import OptionParser
from numpy import mean,fromstring,int8
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.SPI as SPI


class BBB():
        def __init__(self):
            
            

        
        def exit(self):
            sys.exit()         # to set offset to 0 for disconnecting
            

if __name__ == '__main__':

    usage = """usage: %prog [options] arg
               
               
               EXAMPLES:
                   


               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-s", "--setpoint", type="float", dest="setpoint", default=0.2, help="Set the setpoint" )
    (options, args) = parser.parse_args()
    
    ### Start the talker ###
    BBB()
