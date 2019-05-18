#!/usr/bin/python

import socket
from optparse import OptionParser
import sys
import time
from numpy import zeros,ones,linspace,arange,array,copy,concatenate

PORT=9221

class TTITGF3162():
        def __init__(self,channel=None,query=None,command=None,IP_ADDRESS=None,offset=None,amplitude=None,pulsEedge=None,dutycycle=None,frequency=None,bruno_mes=False):
            self.command = None
            if not(IP_ADDRESS):
                print '\nYou must provide an address...\n'
                sys.exit()
            
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((IP_ADDRESS,PORT))
            
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
                self.write('AMPL '+amplitude)
            if dutycycle:
                self.write('PULSWID '+dutycycle)
            if frequency:
                self.write('PULSFREQ '+frequency)
            if offset:
                self.write('DCOFFS '+offset)
            if pulsEedge:
                self.write('PULSEDGE '+pulsEedge)
            if bruno_mes is True:
                self.bruno_mes()
              
            #self.exit()
            
        def bruno_mes(self):
            """MUST be integer numbers"""
            MI   = -125
            MA   = 125
            INCR = 19
####################################################################
            ### CHANNEL 1
            self.write('CHN 1')
            self.write('CHN?')
            print 'Acting on channel:',self.read()
            self.write('WAVE ARB')
            self.write('ARBLOAD ARB1')
            self.write('FREQ 100')
            self.write('DCOFFS 0.05')
            self.write('AMPL 0.1')
            
            l =(125,-125,125)#arange(MI,MA,INCR)    # the ramp
#            lll = copy(l)[::-1][1:-1]
#            l = concatenate((l,lll))
            self.write_array_to_byte(l,1)

#####################################################################      
            
            
#            ### CHANNEL 1
#            self.write('CHN 1')
#            self.write('CHN?')
#            print 'Acting on channel:',self.read()
#            self.write('WAVE ARB')
#            self.write('ARBLOAD ARB1')
#            self.write('FREQ 100')
#            self.write('DCOFFS 0.05')
#            self.write('AMPL 0.1')
#            
#            l = arange(MI,MA,INCR)    # the ramp
#            lll = copy(l)[::-1][1:-1]
#            l = concatenate((l,lll))
#            self.write_array_to_byte(l,1)
#            
#            NB      = 1
#            NB_HIGH = 5
#            ### CHANNEL 2
#            self.write('CHN 2')
#            self.write('CHN?')
#            print 'Acting on channel:',self.read()
#            self.write('WAVE ARB')
#            self.write('ARBLOAD ARB2')
#            self.write('FREQ 100')
#            self.write('DCOFFS 1')
#            self.write('AMPL 1')
#            
#            ll = []          # the pulses
#            for i in range(0,len(l)):
#                for j in range(15*NB):
#                    ll.append(MI)
#                for j in range(NB_HIGH):
#                    ll.append(MA)
#                for j in range(NB):
#                    ll.append(MI)
#                    
#            self.write_array_to_byte(ll,2)
        
        def write_array_to_byte(self,l,ARB):
            ### Arguments: array, arbitrary waveform number to address the array to ###
            a = ''.join([array(l[i]).tobytes()[:2] for i in range(len(l))])
            temp = str(2*len(l))
            self.write('ARB'+str(ARB)+' #'+str(len(temp))+temp+a)
            time.sleep(0.2)
        
        def write(self,query):
            self.s.send(query+'\n')
            
        def read(self):
            rep = self.s.recv(1000)
            return rep

        def exit(self):
            sys.exit()

        def idn(self):
            self.inst.write('*IDN?')
            self.read()
            
            
if __name__ == '__main__':

    usage = """usage: %prog [options] arg
               
               EXAMPLES:
                   set_TTITGF3162 -f 80000000 -a 2
                   set_TTITGF3162 -f 80e6 -a 2
                   Note that both lines are equivalent
                   
                   Set the frequency to 80MHz and the power to 2Vpp.

            set_TTITGF3162 -c 'CHN 2' for the command option

               """
               
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-o", "--offset", type="str", dest="off", default=None, help="Set the offset value." )
    parser.add_option("-a", "--amplitude", type="str", dest="amp", default=None, help="Set the amplitude." )
    parser.add_option("-f", "--frequency", type="str", dest="freq", default=None, help="Set the frequency." )
    parser.add_option("-d", "--dutycyle", type="str", dest="dutycycle", default=None, help="Set the DUTYCYLE." )
    parser.add_option("-p", "--pulsEedge", type="str", dest="pulsEedge", default=None, help="Set the pulsEedge." )
    parser.add_option("-i", "--ip_address", type="str", dest="ip_address", default='169.254.86.108', help="Set the Ip address to use for communicate." )
    parser.add_option("-b", "--bruno_mes",action="store_true", dest="bruno_mes", default='False', help="set the generator to runn arbitrary functions." )
    (options, args) = parser.parse_args()
    
        ### Compute channels to acquire ###
    if (len(args) == 0) and (options.com is None) and (options.que is None) and not(options.bruno_mes):
        print '\nYou must provide at least one channel\n'
        sys.exit()
    elif len(args) == 1:
        chan = []
        temp_chan = args[0].split(',')                  # Is there a coma?
        for i in range(len(temp_chan)):
            chan.append('CHN' + temp_chan[i])
    else:
        chan = []
        for i in range(len(args)):
            chan.append('CHN' + str(args[i]))
    print chan
    ### Start the talker ###
    TTITGF3162(channel=chan,query=options.que,command=options.com,IP_ADDRESS=options.ip_address,offset=options.off,amplitude=options.amp,pulsEedge=options.pulsEedge,dutycycle=options.dutycycle,frequency=options.freq,bruno_mes=options.bruno_mes)
