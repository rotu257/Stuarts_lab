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

GPIB_PORT = '5'

class keopsys():
        def __init__(self,query=None,command=None,PORT=GPIB_PORT):
            ### establish GPIB communication ###
            r          = v.ResourceManager('@py')
            self.scope = r.get_instrument('GPIB::'+PORT+'::INSTR')
            
            if query:                                         # to execute command from outside
                print '\nAnswer to query:',query
                self.write(query+'\n')
                rep = self.read()
                print rep,'\n'
                sys.exit()
            elif command:
                self.command = command
                print '\nExecuting command',self.command
                self.scope.write(self.command)
                print '\n'
                sys.exit()
                

            sys.exit()


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


if __name__ == '__main__':

    usage = """usage: %prog [options] arg
               
               
               EXAMPLES:
                   


               """
    parser = OptionParser(usage)
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to execute." )
    parser.add_option("-i", "--gpib_port", type="str", dest="gpib_port", default='2', help="Set the gpib port to use." )
    (options, args) = parser.parse_args()

    ### Start the talker ###
    keopsys(query=options.que,command=options.com,PORT=options.gpib_port)
