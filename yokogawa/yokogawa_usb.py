#!/usr/bin/python

import usb
import usb.core
import usb.util
from optparse import OptionParser
import sys
import time
import numpy as np

class yoko():
        def __init__(self,query=None,lambd=None,scan=None,piezo=None,scanpiezo=None):
            dev = usb.core.find(idVendor=0x3923,idProduct=0x709b)
            dev.reset()
            dev.set_configuration()

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

            assert self.ep_out is not None
            assert self.ep_in is not None
            
            if query:                                         # to execute command from outside
                print '\nAnswer to query:',query
                self.write(query)
                rep = self.read()
                print rep,'\n'
                sys.exit()
                
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
                   


               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--query", type="str", dest="com", default=None, help="Set the query to use." )
    (options, args) = parser.parse_args()

    
    ### Start the talker ###
    yoko(query=options.com)
