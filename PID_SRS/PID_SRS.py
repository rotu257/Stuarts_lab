#!/usr/bin/python

import visa as v
from optparse import OptionParser
import sys
import time

class TGA_12104():
        def __init__(self,query=None,command=None,port=None,setpoint=None,auto_lock=None,lock=None,unlock=None):
            
            rm = v.ResourceManager('@py')
            self.PID = rm.get_instrument('GPIB::2::INSTR')
            self.PID.write('CEOI ON')
            self.PID.write('EOIX ON')
            
            self.write('CONN '+port+',"CONAME"')
            self.write('TERM LF')
            
            self.write('*IDN?')
            print '\nCONNECTING to module on PORT', port,':',self.read()
            
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
            
            if lock:
                self.write('AMAN 1')
            elif unlock:
                self.write('AMAN 0')
            
            if auto_lock:
                self.re_lock(port)
            if setpoint:
                self.write('SETP '+setpoint)
            
            self.exit()
        
        def re_lock(self,port):
            self.write('AMAN 0')
            time.sleep(0.1)
            if port=='3':
                self.write('MOUT 0')
            elif port=='5':
                self.write('MOUT 5')
            time.sleep(0.1)
            self.write('AMAN 1')
        
        def exit(self):
            self.write('CONAME')
            sys.exit()

        def write(self,query):
            self.PID.write(query)
            
        def read(self):
            return self.PID.read()
            

if __name__ == '__main__':

    usage = """usage: %prog [options] arg
               
               EXAMPLES:
                   set_PIDSRS -i 5 -s 
                   Active the locking of the port 5


               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-a", "--autolock", action = "store_true", dest="autolock", default=False, help="Enable auto locking." )
    parser.add_option("-l", "--lock", type="str", dest="lock", default=None, help="Lock" )
    parser.add_option("-u", "--unlock", type="str", dest="unlock", default=None, help="Unlock" )
    parser.add_option("-i", "--port", type="str", dest="port", default='5', help="Port for the PID freme to apply the command to" )
    parser.add_option("-s", "--setpoint", type="str", dest="setpoint", default=None, help="Setpoint value to be used" )
    (options, args) = parser.parse_args()
    
    ### Start the talker ###
    TGA_12104(query=options.que,command=options.com,port=options.port,setpoint=options.setpoint,auto_lock=options.autolock,lock=options.lock,unlock=options.unlock)
