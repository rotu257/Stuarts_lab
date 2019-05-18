#!/usr/bin/python

import vxi11 as v
from optparse import OptionParser
import sys
import commands as C
import time
from numpy import fromstring,int8,int16,float64,sign

IP = '169.254.166.210'


conv = ['T0','T1','A','B','C','D','E','F','G','H']
conv2 = ['T0','AB','CD','EF','GH']

class DG645():
        def __init__(self,channel= None, query=None,command=None, delay= None, voltage = None, trigger = None, polarity = None, level= None, disp = None):
          
            ### Initiate communication ###
            self.command = command
            self.scope = v.Instrument(IP)
            self.disp = disp
       
            if query:
                self.command = query
                print '\nAnswer to query:',self.command
                rep = self.query(self.command)
                print rep,'\n'
                
            elif command:
                self.command = command
                print '\nExecuting command',self.command
                self.write(self.command)
                print '\n'
                
            if delay:
                self.ad_delay(channel, delay)
                    
            if voltage:
                #voltage adjust
                print 'Adjust Voltage: ' + channel + ' '+voltage+'V\n'
                self.write('LAMP'+str(conv2.index(channel))+','+voltage)
                
            if trigger: 
                print 'Adjust Trigger: ' +trigger+'Hz\n'
                self.write('TRAT'+trigger)
                
                if disp:
                    print 'Trig Freq     :'+ self.query('TRAT?')+'Hz\n'
                    disp = False
            
            if polarity:
                print 'Adjust Polarity: '+channel+'-'+polarity+'\n'
                self.write('LPOL'+str(conv2.index(channel))+','+polarity)
            
            if level: 
                print 'Adjust Level: '+channel+' '+level+'\n'
                self.write('LOFF'+str(conv2.index(channel))+','+level)
                
            if disp:
                if (channel == []):
                    for chan in conv2[1:5]:
                        self.ch_disp(chan)
                        
                else: 
                    self.ch_disp(channel)
                  
            sys.exit()
            
            
#########################################
        # PRINT OUT CODE 
        def ch_disp(self,channel):
            
            ch1 = str(conv.index(channel[0]))
            tmpdelay = self.query('DLAY?'+ch1)
            tmpdelay = tmpdelay.split(',')
            
            
            if len(channel) == 2:
                ch = str(conv2.index(channel))
                ch2 = str(conv.index(channel[1]))
                
                tmpdelay2 = self.query('DLAY?'+ch2)
                tmpdelay2 = tmpdelay2.split(',')
          
                print '==========CH:'+channel+'=============='
                print 'Level Amplitude  :  '+self.query('LAMP?'+ch)+' V'
                print 'Level Offset     :  '+self.query('LOFF?'+ch)+' V'
                print 'Level Polarity   :  '+self.query('LPOL?'+ch)+'\n'
                print 'Delay           '+channel[0]+':  '+ conv[int(tmpdelay[0])]+tmpdelay[1]+' s'
                print 'Delay           '+channel[1]+':  '+ conv[int(tmpdelay2[0])]+tmpdelay2[1]+' s\n' 
            
            else:
                print '==========CH:'+channel+'=============='
                print 'Delay           '+channel+':  '+ conv[int(tmpdelay[0])]+tmpdelay[1]+' s\n' 
        
                             
        #Channel delay code block 
        def ad_delay(self, channel, delay):
            
            if len(channel) == 2:
                ch1 = str(conv.index(channel[0]))
                ch2 = str(conv.index(channel[1]))
                
            else:
                ch1 = '0'
                ch2 = str(conv.index(channel))
                    
            print 'Adjust Delay: ' + channel + ' '+delay+'s\n'
            self.write('DLAY'+ch2+','+ch1+','+delay,)
                
            
############# BASIC FUNCTIONS#############
        def query(self, cmd, nbytes=1000000):
            """Send command 'cmd' and read 'nbytes' bytes as answer."""
            self.write(cmd+'\n')
            r = self.read(nbytes)
            
            return r
        
        def read(self,nbytes=1000000):
           
            return self.scope.read(nbytes)
        
        def write(self,cmd):
          
            self.scope.write(cmd)
        
if __name__ == '__main__':

    usage = """usage: %prog [options] arg

               EXAMPLES:
                  level change : DG645 AB -v 3 
                  delay change : DG645 AB -d 10e-6 
                  delay wrt t0 : DG645 A -d 10e-6
                  trigger      : DG645 -f 1000000    
                  polarity     : DG645 AB -p 1  / DG645 AB -p 0
                  offset       : DG645 AB -l 2       2v level offset on AB
                  
               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-d", "--delay", type="str", dest="delay", default=None, help="Set the delay (s)")
    parser.add_option("-x", "--display", action = "store_true", dest ="disp", default=False, help="disp")
    parser.add_option("-a", "--voltage", type="str", dest="voltage", default=None, help="Set the amplitude (V)")
    parser.add_option("-f", "--freq", type="str", dest="freq", default=None, help="Set the trigger (Hz)")
    parser.add_option("-p", "--polarity", type="str", dest="pol", default=None, help="Set the level polarity if 1, then up if 0, then down")
    parser.add_option("-l", "--level", type="str", dest="level", default=None, help="Set the level")
    # parser.add_option("-b", "--burst",type="str", dest="level",deafult= None, help="burst options")
    (options, args) = parser.parse_args()

    chan = []
    #Errors for options that do not require a channel input
    # command, query, display, 
    # voltage, freq, polarity, level

    if (options.voltage) or (options.delay) or (options.pol) or (options.level):
    	if (len(args) == 0):
    		print '\nYou must provide at least one edge\n'
    		sys.exit()

    	if (options.pol) or (options.voltage) or (options.level):
            if (len(args[0])==1):
                print '\nYou must provide a channel'
                sys.exit()
                
        if (args[0] in conv) or (args[0] in conv2):
            chan = args[0].upper() 
            
        else:       
            print '\nYou must provide a channel or edge'
            sys.exit()
         

    if (options.disp) and (len(args) !=0):
        if (args[0] in conv) or (args[0] in conv2):
            chan = args[0].upper() 
            
        else:       
            print '\nYou must provide a channel or edge'
            sys.exit()
    
    
    
    ### Start the talker ###
    DG645(channel= chan, query=options.que,command=options.com,delay=options.delay,voltage= options.voltage, trigger = options.freq, polarity= options.pol,level = options.level, disp = options.disp)
    
       # photonetics(query=options.que,command=options.com,PORT=options.gpib_port,amplitude=options.amplitude)
