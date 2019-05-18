#!/usr/bin/python

import usb
import usb.core
import usb.util
from optparse import OptionParser
import sys
import time
import numpy as np
import visa as v
import commands as C
from numpy import savetxt,linspace

GPIB_PORT = 1

class photonetics():
        def __init__(self,query=None,command=None,PORT=GPIB_PORT,amplitude=None):
            ### establish GPIB communication ###
            r          = v.ResourceManager('@py')
            self.scope = r.get_instrument('GPIB::'+PORT+'::INSTR')
            if query:                                         # to execute command from outside
                print '\nAnswer to query:',query
                self.write(query+'\n')
                rep = self.read()
                print rep,'\n'
            elif command:
                self.command = command
                print '\nExecuting command',self.command
                self.scope.write(self.command)
                print '\n'

            if amplitude: 
                amplitude = round(eval(amplitude),2)
                print '\nSetting EDFA to: ',amplitude,'mW\n'
                self.modify_amplitude_EDFA(amplitude)
                
            sys.exit()


        #####################  FUNCTIONS ##############################################
        def modify_amplitude_EDFA(self,amplitude):
            """ port 5 to be addressed """
            #Set output power units to MW and get state
            if amplitude==-1:
                self.write('CH5:DISABLE')
                print 'EDFA: DISABLE'
                sys.exit()
            self.write('MW;CH5:P=%1.2f'%amplitude)
            setpower = self.query('MW;CH5:P?')
            if  setpower == 'CH5:Disabled\n':
                self.write('CH5:ENABLE')
                print 'EDFA: ENABLE'
            setpower = self.query('MW;CH5:P?')   
            print 'EDFA:',setpower.split('=')[1]
            
        
                
        #####################  BASICS FUNCTIONS #######################################
        def query(self,query,length=1000000):
            self.write(query)
            r = self.read(length=length)
            return r
            
        def write(self,query):
            self.string = query + '\n'
            self.scope.write(self.string)
            
        def read(self,length=10000000):
            rep = self.scope.read_raw()
            return rep

        def idn(self):
            self.ep_out.write('*IDN?\r\n')
 
if __name__ == '__main__':

    usage = """usage: %prog [options] arg
               
               
               EXAMPLES:
                   


               """
    parser = OptionParser(usage)
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to execute." )
    parser.add_option("-i", "--gpib_port", type="str", dest="gpib_port", default='1', help="Set the gpib port to use." )
    parser.add_option("-a", "--amplitude", type="str", dest="amplitude", default=None, help="Set the EDFA gain")
    
    (options, args) = parser.parse_args()

    ### Start the talker ###
    photonetics(query=options.que,command=options.com,PORT=options.gpib_port,amplitude=options.amplitude)
