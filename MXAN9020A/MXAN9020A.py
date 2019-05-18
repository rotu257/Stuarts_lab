#!/usr/bin/env python
import vxi11 as vxi
import sys
import time
from optparse import OptionParser
import commands as C
from numpy import savetxt,linspace

HOSTNAME="169.254.124.188"

class MXAN9020A():
    def __init__(self, filename=None,query=None,command=None,host=HOSTNAME,FORCE=False,SAVE=True,trigger=False):
        ### Establish the connection ###
        self.sock = vxi.Instrument(host)
        
        if query:
            self.command = query
            print '\nAnswer to query:',self.command
            rep = self.query(self.command)
            print rep,'\n'
            sys.exit()
        elif command:
            self.command = command
            print '\nExecuting command',self.command
            self.write(self.command)
            print '\n'
            sys.exit()
        
        self.prev_state = self.query('INIT:CONT?')
        if trigger:
            self.write('*TRG')
        self.query('INIT:CONT OFF;*OPC?')
        
        if filename:
            self.lambd,self.amp = self.get_data()
            ### TO SAVE ###
            if SAVE:
                temp_filename = filename + '_MXAN9020A.txt'
                temp = C.getoutput('ls').splitlines()                           # if file exist => exit
                for i in range(len(temp)):
                    if temp[i] == temp_filename and not(FORCE):
                        print '\nFile ', temp_filename, ' already exists, change filename, remove old file or use -F option to overwrite\n'
                        sys.exit()

                savetxt(temp_filename,(self.lambd,self.amp))
        
        self.write('INIT:CONT '+self.prev_state)
                
    def get_data(self):
        data  = eval(self.query("TRAC:DATA? TRACE1"))
        start = eval(self.query("SENS:FREQ:START?"))
        stop  = eval(self.query("SENS:FREQ:STOP?"))
        X = linspace(start,stop,len(data))
        return X,data

    def write(self, msg):
        self.sock.write(msg)

    def read(self):
        msg=self.sock.read()
        return msg

    def query(self,msg,length=2048):
        """Sends question and returns answer"""
        self.write(msg)
        return(self.read())


if __name__=="__main__":
    
    usage = """usage: %prog [options] arg

               EXAMPLES:
                   get_MXA9020A -o filename
               Record the spectrum and create one file with two columns lambda,spectral amplitude

               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-o", "--filename", type="string", dest="filename", default=None, help="Set the name of the output file" )
    parser.add_option("-F", "--force", type="string", dest="force", default=None, help="Allows overwriting file" )
    parser.add_option("-i", "--ip_address", type="string", dest="ip_address", default=HOSTNAME, help="Set the ip address to establish the communication with" )
    parser.add_option("-t", "--trigger", action = "store_true", dest ="trigger", default=False, help="Make sure the instrument trigger once and finishes sweeping before acquiring the data")
    (options, args) = parser.parse_args()

    
    MXAN9020A(query=options.que,command=options.com,filename=options.filename,FORCE=options.force,host=options.ip_address,trigger=options.trigger)

