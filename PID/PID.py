#!/usr/bin/python

import visa as v
from optparse import OptionParser
import sys
import time

PORT = '5'

class TGA_12104():
        def __init__(self,query=None,command=None,kar=None,auto_lock=None):
            self.command = None
            
            rm = v.ResourceManager('@py')
            self.PID = rm.get_instrument('GPIB::2::INSTR')
            self.PID.write('CEOI ON')
            self.PID.write('EOIX ON')
            
            self.write('CONN '+PORT+',"CONAME"')
            self.write('TERM LF')
            
            self.write('*IDN?')
            print '\nCONNECTING to module:',self.read()
            
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
            
            if auto_lock:
                self.re_lock()
            
            self.exit()
        
        def re_lock(self):
            self.write('AMAN 0')
            time.sleep(0.1)
            self.write('AMAN 1')
        
        def exit(self):
            self.write('CONAME')
            sys.exit()

        def write(self,query):
            self.PID.write(query)
            
        def read(self):
            rep = self.PID.read()
            return rep

        def idn(self):
            self.ep_out.write('*IDN?\r\n')
            

if __name__ == '__main__':

    usage = """usage: %prog [options] arg
               
               
               EXAMPLES:
                   


               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-a", "--autolock", type="str", dest="autolock", default=None, help="Enable auto locking." )
    (options, args) = parser.parse_args()
    
    ### Start the talker ###
    TGA_12104(query=options.que,command=options.com,auto_lock=options.autolock)
