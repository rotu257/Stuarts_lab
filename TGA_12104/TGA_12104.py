#!/usr/bin/python

import usb
import usb.core
import usb.util
from optparse import OptionParser
import sys

class TGA_12104():
        def __init__(self,query=None,command=None,kar=None,amplitude=None,frequency=None,period=None):
            self.command = None
            
            dev = usb.core.find(idVendor=0x103e,idProduct=0x03f2)
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
            
            if kar:
                self.init_karen_meas()
                self.exit()
            
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
                self.amplitude(str(amplitude))
            if frequency:
                self.frequency(str(frequency))
            if period:
                self.period(str(period))
            
            self.exit()
        
        def amplitude(self,command):
            """ Change amplitude in Vpp """
            command = 'AMPL ' + command
            self.write(command)
            
        def frequency(self,command):
            """ Change the frequency in Hz """
            command = 'WAVFREQ ' + command
            self.write(command)
            
        def period(self,command):
            """ Change the period in s """
            command = 'WAVPER ' + command
            self.write(command)
            
        def init_karen_meas(self):
            """ setup the function generator for karen measurment """
            self.write('SETUPCH 1')
            self.write('ARB PZTRAMP')
            self.amplitude(str(2))           # 2 Vpp
            self.period(str(0.01))            # 10 ms
            self.write('OUTPUT ON')
            self.exit()
            
        def exit(self):
            self.write('LOCAL')
            sys.exit()

        def write(self,query):
            self.string = query + '\r\n'
            self.ep_out.write(self.string)
            
        def read(self):
            rep = self.ep_in.read(2000000)
            const = ''.join(chr(i) for i in rep)
            const = const#[:const.find('\r\n')]
            return const

        def idn(self):
            self.ep_out.write('*IDN?\r\n')
            

if __name__ == '__main__':

    usage = """usage: %prog [options] arg
               
               
               EXAMPLES:
                   


               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-k", "--karen", type="str", dest="kar", default=None, help="Set ON karen's measurment." )
    parser.add_option("-a", "--amplitude", type="float", dest="amp", default=None, help="Set the amplitude." )
    parser.add_option("-f", "--frequency", type="float", dest="freq", default=None, help="Set the frequency." )
    parser.add_option("-p", "--period", type="float", dest="per", default=None, help="Set the period." )
    (options, args) = parser.parse_args()
    
    ### Start the talker ###
    TGA_12104(query=options.que,command=options.com,kar=options.kar,amplitude=options.amp,frequency=options.freq,period=options.per)
