#! /usr/bin/python

import visa as v 
import time as t
from numpy import *
from optparse import OptionParser
import sys

class ITC_4001():
    def __init__(self,INSTR,query=None,command=None,amplitude=None):
        ### Initiate communication ###
        rm = v.ResourceManager('@py')
        try:
	    self.thorlabs = rm.get_instrument(INSTR)
        except:
            print '\nWrong connection => Check address or cables\n'
            sys.exit()

        ### Basic communications ###
        if query:
            self.command = query
            print '\nAnswer to query:',self.command
            rep = self.query(self.command)
            print rep,'\n'
            sys.exit()
        elif command:
            self.command = command
            print '\nExecuting command',self.command
            self.thorlabs.write(self.command)
            print '\n'
            sys.exit()

        ### change the value of the current ###
        if amplitude or amplitude==0:
            self.thorlabs.write('SOUR:CURR %f\n' %amplitude)
            print '\nSetting current to: ',amplitude,'V\n'


    def query(self, cmd):
        self.thorlabs.write(cmd+'\n')
        r = self.read()
        return r
    
    def read(self):
        return self.thorlabs.read()
        
if __name__=="__main__":
    
    usage = """usage: %prog [options] arg
               
               EXAMPLES:
                   set_ITC4001 -a val 1
               
               Set the pumping current to val to the instrument 1
               Instrument numner must be from 1 to 3 (as written on it) 

               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-a", "--amplitude", type="float", dest="amplitude", default=None, help="Set the pumping current value")
    (options, args) = parser.parse_args()
    
    ### Compute channels to acquire ###
    if len(args) != 1:
        print '\nYou must provide ONE address\n'
        sys.exit()
    else:
        temp_instr = eval(args[0])
    
    if temp_instr == 1:
        INSTR = 'USB::4883::32842::M00248997::INSTR'
    elif temp_instr == 2:
        INSTR = 'USB::4883::32842::M00271786'
    elif temp_instr == 3:
        INSTR = 'USB::4883::32842::M00248304'
    else:
        print '\nYou MUST provide an address\n'
        sys.exit()
    
    ### Call the class with arguments ###
    ITC_4001(INSTR,query=options.que,command=options.com,amplitude=options.amplitude)

