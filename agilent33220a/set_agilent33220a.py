#!/usr/bin/python

import visa as v
from optparse import OptionParser
import sys
import time
from numpy import zeros,ones,linspace


class agilent33220a():
        def __init__(self,query=None,command=None,IP_ADDRESS=None,offset=None,amplitude=None,frequency=None,ramp=None):
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
                self.inst.write('VOLT '+amplitude)
            if offset:
                self.inst.write('VOLT:OFFS '+offset)
            if frequency:
                self.inst.write('FREQ '+frequency)
                
            if ramp:
                self.ramp(ramp)
            
            self.exit()
        
        def ramp(self,ramp):
            l   = list(zeros(5000) - 1)
            lll = list(ones(5000))
            ll  = list(linspace(-1,1,100+ramp))
            l.extend(ll);l.extend(lll)
            s = str(l)[1:-1]
            self.inst.write('DATA VOLATILE,'+s)

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
                   


               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-r", "--ramp", type="float", dest="ramp", default=None, help="Turn on ramp mode." )
    parser.add_option("-o", "--offset", type="str", dest="off", default=None, help="Set the offset value." )
    parser.add_option("-a", "--amplitude", type="str", dest="amp", default=None, help="Set the amplitude." )
    parser.add_option("-f", "--frequency", type="str", dest="freq", default=None, help="Set the frequency." )
    parser.add_option("-i", "--ip_address", type="str", dest="ip_address", default='172.24.23.119', help="Set the Ip address to use for communicate." )
    (options, args) = parser.parse_args()
    
    ### Start the talker ###
    agilent33220a(query=options.que,command=options.com,IP_ADDRESS=options.ip_address,ramp=options.ramp,offset=options.off,amplitude=options.amp,frequency=options.freq)
