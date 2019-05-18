#!/usr/bin/python

import visa as v
from optparse import OptionParser
import sys
import time
from numpy import zeros,ones,linspace


class agilentE8244A():
        def __init__(self,query=None,command=None,IP_ADDRESS=None,offset=None,amplitude=None,frequency=None):
            self.command = None
            if not(IP_ADDRESS):
                print '\nYou must provide an address...\n'
                sys.exit()
                
            rm = v.ResourceManager('@py')
            self.inst = rm.get_instrument('TCPIP::'+IP_ADDRESS+'::INSTR')
            
            if query:
                self.command = query
                print '\nAnswer to query:',self.command
                self.write(self.command)
                rep = self.read()
                print rep,'\n'
                self.exit()
            elif command:
                self.command = command
                print '\nExecuting command',self.command
                self.write(self.command)
                print '\n'
                self.exit()
            
            if amplitude:
                self.inst.write('POW '+amplitude)
            if frequency:
                self.inst.write('FREQ '+frequency)
                
            
            self.exit()

        def write(self,query):
            self.inst.write(query)
            
        def read(self):
            rep = self.inst.read()
            return rep

        def exit(self):
            sys.exit()

        def idn(self):
            self.inst.write('*IDN?')
            self.read()
            
            
if __name__ == '__main__':

    usage = """usage: %prog [options] arg
               
               EXAMPLES:
                   set_agilentE8244A -f 80MHz -a 20
                   
                   Set the frequency to 80MHz and the power to 20dBm.
               """
               
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-o", "--offset", type="str", dest="off", default=None, help="Set the offset value." )
    parser.add_option("-a", "--amplitude", type="str", dest="amp", default=None, help="Set the amplitude." )
    parser.add_option("-f", "--frequency", type="str", dest="freq", default=None, help="Set the frequency." )
    parser.add_option("-i", "--ip_address", type="str", dest="ip_address", default='169.254.54.215', help="Set the Ip address to use for communicate." )
    (options, args) = parser.parse_args()
    
    ### Start the talker ###
    agilentE8244A(query=options.que,command=options.com,IP_ADDRESS=options.ip_address,offset=options.off,amplitude=options.amp,frequency=options.freq)
