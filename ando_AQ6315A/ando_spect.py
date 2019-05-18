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

GPIB_PORT = 2

class ando6315A():
        def __init__(self,query=None,command=None,FORCE=False,PORT=GPIB_PORT,filename=None,SAVE=True):
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
                
            if filename:
                self.lambd,self.amp = self.get_data()
                self.amp = [eval(self.amp[i]) for i in range(len(self.amp))]

                ### TO SAVE ###
                if SAVE:
                    temp_filename = filename + '_ANDO'
                    temp = C.getoutput('ls').splitlines()                           # if file exist => exit
                    for i in range(len(temp)):
                        if temp[i] == temp_filename and not(FORCE):
                            print '\nFile ', temp_filename, ' already exists, change filename, remove old file or use -F option to overwrite\n'
                            sys.exit()

                    savetxt(temp_filename,(self.lambd,self.amp))
                
        def get_data(self):
            print "ACQUIRING..."
            data    = self.query("LDATA").split(',')[1:] 
            stopWL  = float(self.query("STPWL?"))
            startWL = float(self.query("STAWL?"))
            X = linspace(startWL,stopWL,len(data))
            return X,data

        def singleSweep(self):
            s = self.write("SGL")
            return s
        
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
    parser.add_option("-q", "--query", type="str", dest="com", default=None, help="Set the query to use." )
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to execute." )
    parser.add_option("-i", "--gpib_port", type="str", dest="gpib_port", default='2', help="Set the gpib port to use." )
    parser.add_option("-o", "--filename", type="string", dest="filename", default=None, help="Set the name of the output file" )
    parser.add_option("-F", "--force", type="string", dest="force", default=None, help="Allows overwriting file" )
    (options, args) = parser.parse_args()

    ### Start the talker ###
    ando6315A(query=options.com,PORT=options.gpib_port,filename=options.filename,FORCE=options.force)
