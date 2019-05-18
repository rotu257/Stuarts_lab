#!/usr/bin/python

import vxi11 as v
from optparse import OptionParser
import sys
import commands as C
import time

class DSO_X4154A():
        def __init__(self,channel=None,filename=None,host=None,query=None,command=None,typ="BYTE"):
            self.command = None
            self.scope = v.Instrument(host)
            self.scope.write(':WAVeform:TYPE RAW')
            self.scope.write(':WAVeform:POINTS RAW')
            self.scope.write(':WAVeform:POINTS:MODE RAW')
            self.scope.write(':WAVEFORM:BYTEORDER LSBFirst')
            self.scope.write(':TIMEBASE:MODE MAIN')
            self.scope.write(':WAV:SEGM:ALL ON')
            
            if query:
                self.command = query
                print '\nAnswer to query:',self.command
                self.scope.write(self.command)
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
                self.stop()
                for i in range(len(channel)):
                    print 'trying to get channel',channel[i]
                    self.get_data(chan=channel[i],filename=filename,SAVE=True,typ=typ)
                    
                self.run()
                sys.exit()
            
            else:
                print 'If you want to save, provide an output file name'
            
            

        def get_data(self,chan='CH1',filename='test_save_file_',PLOT=False,typ='BYTE',SAVE=False,LOG=True):
            self.scope.write(':WAVEFORM:SOURCE ' + chan)
            self.scope.write(':WAVEFORM:FORMAT ' + typ)
            self.scope.write(':WAV:DATA?')
            if typ=='ASCII':
                self.data = self.read_raw()
            elif typ=='BYTE':
                self.data = self.read_raw()[8:]
            
            self.data = self.data[:-1]     # to remove last shitty point

            ### TO SAVE ###
            if SAVE:
                temp = C.getoutput('ls').splitlines()                           # if file exist => exit
                for i in range(len(temp)):
                    temp_filename = filename + '_DSOX4154A' + chan
                    if temp[i] == temp_filename:
                        print '\nFile ', temp_filename, ' already exists, change filename or remove old file\n'
                        sys.exit()
                
                f = open(filename + '_DSOX4154A' + chan,'w')                   # Save data
                f.write(self.data)
                f.close()
                if LOG:
                    self.preamb = self.get_log_data(chan=chan)             # Save scope configuration
                    f = open(filename + '_DSOX4154A' + chan + '.log','w')
                    f.write(self.preamb)
                    f.close()
                print  chan + ' saved'
        
        def get_log_data(self,chan='CHAN1'):
            self.scope.write(':WAVEFORM:SOURCE ' + chan)
            self.scope.write(':WAVEFORM:PREAMBLE?')
            return self.scope.read()          
        
        def read_raw(self,length=100000000):
            rep = self.scope.read_raw(length)
            return rep
        
        def read(self,length=100000000):
            rep = self.scope.read(length)
            return rep
        
        def run(self):
            self.scope.write(':RUN')
        def stop(self):
            self.scope.write(':STOP')
            
if __name__ == '__main__':
    IP = '169.254.93.97'
    
    usage = """usage: %prog [options] arg
    
               WARNING: - Be sure all the channel you provide are active
               
               EXAMPLES:
                   get_DSO54853A -o filename 1,2
               Record channel 1 and 2 and create 4 files (2 per channels) name filename_DSO54853ACH1 and filename_DSO54853ACH1.log


               IMPORTANT INFORMATIONS:
                    - Datas are obtained in a binary format: int8 
                    - Header is composed as follow:
                    <format>, <type>, <points>, <count> , <X increment>, <X origin>, < X reference>, <Y increment>, <Y origin>, <Y reference>, <coupling>, <X display range>, <X display origin>, <Y display range>, <Y display origin>, <date>,
                    <time>, <frame model #>, <acquisition mode>, <completion>, <X units>, <Y units>, <max bandwidth limit>, <min bandwidth limit>    
                    - To retrieve datas (in "Units")
                    Y-axis Units = data value * Yincrement + Yorigin (analog channels) 
                    X-axis Units = data index * Xincrement + Xorigin

               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-o", "--filename", type="string", dest="filename", default=None, help="Set the name of the output file" )
    parser.add_option("-i", "--ipadd", type="string", dest="ipadd", default=IP, help="Set ip address" )

    parser.add_option("-t", "--type", type="str", dest="type", default="BYTE", help="Type of data returned (available values are 'BYTE' or 'ASCII')" )
    (options, args) = parser.parse_args()

    ### Compute channels to acquire ###
    if (len(args) == 0) and (options.com is None) and (options.que is None):
        print '\nYou must provide at least one channel\n'
        sys.exit()
    elif len(args) == 1:
        chan = []
        temp_chan = args[0].split(',')                  # Is there a coma?
        for i in range(len(temp_chan)):
            chan.append('CHAN' + temp_chan[i])
    else:
        chan = []
        for i in range(len(args)):
            chan.append('CHAN' + str(args[i]))
    print chan
    
    ### Start the talker ###
    DSO_X4154A(channel=chan,host=options.ipadd,query=options.que,command=options.com,filename=options.filename,typ=options.type)
    
