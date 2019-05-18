#!/usr/bin/python

import usb
import usb.core
import usb.util
from optparse import OptionParser
import sys
import time
import numpy as np

class IDS2104a():
        def __init__(self,query=None,channel=None,command=None,filename=None,FORCE=False):
            dev = usb.core.find(idVendor=0x2184,idProduct=0x0014)
            print 'ok1'
            dev.reset()
            print 'ok1'
            #dev.set_configuration()
            print 'ok1'

            interface = 0
            if dev.is_kernel_driver_active(interface) is True:
                # tell the kernel to detach
                dev.detach_kernel_driver(interface)
                # claim the device
                usb.util.claim_interface(dev, interface)

            cfg = dev.get_active_configuration()
            intf = cfg[(0,0)]
            self.ep_out = usb.util.find_descriptor(intf,custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
            self.ep_in = usb.util.find_descriptor(intf,custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
            
            print self.ep_out,self.ep_in
            
            #assert self.ep_out is not None
            #assert self.ep_in is not None
            
            if query:
                self.command = query
                print '\nAnswer to query:',self.command
                rep = self.query(self.command)
                print rep,'\n'
                sys.exit()
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
        
        def write(self,query):
            self.string = query + '\r\n'
            self.ep_out.write(self.string)
            
        def read(self):
            rep = self.ep_in.read(64)
            const = ''.join(chr(i) for i in rep)
            const = const[:const.find('\r\n')]
            return const

        def idn(self):
            self.ep_out.write('*IDN?\r\n')
            
            
if __name__ == '__main__':

    usage = """usage: %prog [options] arg
               
               Think to provide a tuple of values (min,max) for the scans
               
               EXAMPLES:
                    get_IDS2104a -o my_filename 1,2
                    Last line will acquire channel 1 and 2 (that have to be active) and store them in files called my_filename_IDSCHAN1 (and 2 respectively). Files my_filename_IDSCHAN1.log (and CHAN2 respectively) are also acauired and contain the parameters of the channel to use to retrieve real datas

               """
    parser = OptionParser(usage)
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-o", "--filename", type="string", dest="filename", default=None, help="Set the name of the output file" )
    parser.add_option("-F", "--force", type="string", dest="force", default=None, help="Allows overwriting file" )
    (options, args) = parser.parse_args()
    
    ### Compute channels to acquire ###
    if (len(args) == 0) and (options.com is None) and (options.que is None):
        print '\nYou must provide at least one channel\n'
        sys.exit()
    elif len(args) == 1:
        chan = []
        temp_chan = args[0].split(',')                  # Is there a coma?
        for i in range(len(temp_chan)):
            chan.append('C' + temp_chan[i])
    else:
        chan = []
        for i in range(len(args)):
            chan.append('C' + str(args[i]))
    print 'Channel(s):   ', chan
    
    ### Start the code ###
    IDS2104a(query=options.que,channel=chan,command=options.com,filename=options.filename,FORCE=options.force)
