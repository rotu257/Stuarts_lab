#!/usr/bin/python

import vxi11 as v
from optparse import OptionParser
import sys
import commands as C
import time
from numpy import fromstring,int8,int16,float64,sign

IP = '169.254.166.206'

class DG645():
        def __init__(self,query=None,command=None):

            ### Initiate communication ###
            self.command = command
            self.scope = v.Instrument(IP)
            
            if query:
                self.command = query
                print '\nAnswer to query:',self.command
                rep = self.query(self.command)
                print rep,'\n'
            elif command:
                self.command = command
                print '\nExecuting command',self.command
                self.scope.write(self.command)
                print '\n'
                
                
                   
        sys.exit()
            
        
        def query(self, cmd, nbytes=1000000):
            """Send command 'cmd' and read 'nbytes' bytes as answer."""
            self.write(cmd)
            r = self.read(nbytes)
            return r
        
        def read(self,nbytes=1000000):
            self.scope.read(nbytes)
        
        def write(self,cmd):
            self.scope.write(cmd)
        
if __name__ == '__main__':

    usage = """usage: %prog [options] arg

               EXAMPLES:
                  
               

               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    (options, args) = parser.parse_args()
    
    
    ### Start the talker ###
    DG645(channel=chan,encoding=options.encoding,spe_mode=options.spe_mode,query=options.que,command=options.com,filename=options.filename,FORCE=options.force,FACT=options.spe_fact)
    
