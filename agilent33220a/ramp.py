#!/usr/bin/python

import visa as v
from optparse import OptionParser
import sys
import time
from  numpy import zeros,ones,linspace
from matplotlib.pyplot import plot,draw,show,figure

PORT = '5'

class TGA_12104():
        def __init__(self,query=None,command=None,kar=None,auto_lock=None,lock=None,unlock=None,PLOT=False):
            self.command = None
            
            ### agilent part ###
            rm = v.ResourceManager('@py')
            try:
                self.inst = rm.get_instrument('TCPIP::169.254.2.20::INSTR')
            except:
                print 'no instruments connected'
            
            ramp = 4000
            
            try:
                self.inst.write('VOLT '+str(1))
                self.inst.write('FREQ '+str(200))
            except:
                pass
            
            l = self.new_ramp_step(ramp)
            
            if PLOT:
                plot(l[1:-1])
                return
            
            s = str(l)[1:-1]
            self.inst.write('DATA VOLATILE,'+s)

            ### Start the cycle ###
            self.process()
    
            ### Exit ###
            self.exit()
            
        def ramp_step(self,ramp):
            l   = list(zeros(2000) - 1)
            lll = list(ones(7000))
            ll  = list(linspace(-1,1,100+ramp))
            l.extend(ll);l.extend(lll);l.extend(l4)
            return l
        
        def new_ramp_step(self,ramp):
            l   = list(zeros(2000) - 1)
            lll = list(ones(7000))
            ll  = list(linspace(-1,1,100+ramp))
            l4  = list(linspace(1,-1,ramp/3))
            l.extend(ll);l.extend(lll);l.extend(l4)
            figure()
            plot(l)
            draw()
            show(False)
            raw_input()
            
            return l
            
        def process(self):
            t = time.time()
            self.inst.write('VOLT:OFFS '+str(0.15))
            #self.inst.write('VOLT:OFFS '+str(0.15))
            self.inst.write('OUTP ON')
            self.inst.write('OUTP OFF')
            print 'Total cycle time:', time.time()-t
            
            
        def exit(self):
            sys.exit()
            

if __name__ == '__main__':

    usage = """usage: %prog [options] arg
               
               
               EXAMPLES:
                   


               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-a", "--autolock", type="str", dest="autolock", default=None, help="Enable auto locking." )
    parser.add_option("-l", "--lock", type="str", dest="lock", default=None, help="Lock" )
    parser.add_option("-u", "--unlock", type="str", dest="unlock", default=None, help="Unlock" )
    (options, args) = parser.parse_args()
    
    ### Start the talker ###
    TGA_12104(query=options.que,command=options.com,auto_lock=options.autolock,lock=options.lock,unlock=options.unlock)
