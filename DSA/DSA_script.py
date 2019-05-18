#!/usr/bin/python  
# -*- coding: utf-8 -*-
   
"""

Module to acquire data from DSA 91304A agilent scope.

Module has been written by Bruno Garbin around Jun 2016.

MORE:
    -Think to :DIGITIZE CHAN...  for large arrays because of the velocity gain
    
"""

import vxi11 as vxi
import numpy
from pylab import plot,subplot,title,xlim,clf
import sys
from optparse import OptionParser
import commands as C
import time

IP        = "169.254.108.195"
PORT      = 5025                            # agilent requirement listening port
PORT_TYPE = 'inst0'                           # agilent ethernet requirement

class DSA_fast_oscillo():
    def __init__(self,channel=None,filename=None,host=IP,INTERACTIVE=True,MEAS=None,IP=IP):
        #try:
        print host
        self.sock = vxi.Instrument(host)
        self.sock.write(':WAVeform:TYPE RAW')
        self.sock.write(':WAVEFORM:BYTEORDER LSBFirst')
        self.sock.write(':TIMEBASE:MODE MAIN')
        self.sock.write(':WAV:SEGM:ALL ON')
    #except:
            #print "Wrong IP, Listening port or bad connection \nCheck cables first"
            #sys.exit()
            
        if INTERACTIVE:
            pass
        else:
            if channel is None:
                print 'You must provide at least one channel'
                sys.exit()
            if filename is None:
                print 'WARNING: filename is set to DEFAULT'
                filename = 'DEFAULT'
                
            t = time.time()
            ### Acquire ###
            
            if MEAS:
                for i in range(MEAS):
                    self.stop()
                    print str(i+1)
                    self.get_data(chan=channel[0],filename=str(i+1),PLOT=False,typ='BYTE',SAVE=True,LOG=False)
                    self.run()
                    time.sleep(0.050)
            else:
                for i in range(len(channel)):
                    self.stop()
                    print 'trying to get channel',channel[i]
                    self.get_data(chan=channel[i],filename=filename,PLOT=False,typ='BYTE',SAVE=True)
            
            print 'Measurment time', time.time() - t
            
            self.run()
        
    def get_data(self,chan='CHAN1',filename='test_save_file_',PLOT=False,typ='BYTE',SAVE=False,LOG=True):
        
        self.sock.write(':WAVEFORM:SOURCE ' + chan)
        self.sock.write(':WAVEFORM:FORMAT ' + typ)
        self.sock.write(':WAV:DATA?')
        self.data = self.sock.read_raw()
        if typ != "ASCII":
            self.data = self.data[10:]   #  10 and was determined in fonction of the size of crapping points to the beginning (probably header => to verify)
            
        ### TO SAVE ###
        if SAVE:
            temp = C.getoutput('ls').splitlines()                           # if file exist => exit
            for i in range(len(temp)):
                temp_filename = filename + '_DSA' + chan
                if temp[i] == temp_filename:
                    print '\nFile ', temp_filename, ' already exists, change filename or remove old file\n'
                    sys.exit()
            
            f = open(filename + '_DSA' + chan,'w')                   # Save data
            f.write(self.data)
            f.close()
            if LOG:
                self.preamb = self.get_log_data(chan=chan)             # Save scope configuration
                f = open(filename + '_DSA' + chan + '.log','w')
                f.write(self.preamb)
                f.close()
            print  chan + ' saved'
        
        ### TO PLOT ###
        elif not(SAVE) and PLOT:
            if typ != "ASCII":
                self.trace = numpy.fromstring(self.data, dtype=numpy.int8)
            else: 
                self.trace = numpy.fromstring(self.data,dtype='float',sep=',')[:-1]
            if PLOT:
                plot(self.trace)
            
            print 'data',len(self.data)
            print 'trace',len(self.trace)
        
    def get_log_data(self,chan='CHAN1'):
        self.sock.write(':WAVEFORM:SOURCE ' + chan)
        self.sock.write(':WAVEFORM:PREAMBLE?')
        return self.sock.read()
        
    def reset(self):
        self.sock.local()
        self.sock.clear()
        self.sock.local()
        self.sock.write('*RST')

    def cmd(self,string):
        "Take a sting and write it to the oscillo"
        self.sock.write(string)            
    def run(self):
        self.sock.write(':RUN')
    def stop(self):
        self.sock.write(':STOP')
    def disconnect(self):
        self.sock.close()
        
    def idn(self):
        self.cmd("*IDN?")  
        print "Scope identifies as: ", resp()
    
    def test_get_trace_byte(self,chan='CHAN1',):
        """Acquire two times the same data to compare byte mode with ascii one (ASCII being the reference)"""
        self.stop()
        self.sock.write(':WAVEFORM:SOURCE ' + chan)
        clf()
        
        subplot(211);title('Mode: ASCII',fontsize='x-large')
        self.sock.write(':WAVEFORM:FORMAT ASCII')
        print 'Acquiring ASCII'
        self.sock.write(':WAV:DATA?')
        self.data = self.sock.read_raw()
        print 'ASCII acquired'
        self.trace = numpy.fromstring(self.data,dtype='float',sep=',')[:-1]
        #temp = self.data.rstrip().rsplit(',')[:-1]
        #self.trace = [eval(temp[i]) for i in xrange(len(temp))]
        plot(self.trace)
        xlim(0,100)
        print 'trace ascii    len:',len(self.trace), '    max:' ,max(self.trace), '    min:',min(self.trace)
        
        subplot(212);title('Mode: BYTE',fontsize='x-large')
        self.sock.write(':WAVEFORM:FORMAT BYTE')
        print 'Acquiring BYTE'
        self.sock.write(':WAV:DATA?')
        self.data = self.sock.read_raw()[10:]  
        print 'BYTE acquired'
        self.trace = numpy.fromstring(self.data, dtype=numpy.int8) 
        plot(self.trace)
        xlim(0,100)
        print 'trace byte    len:',len(self.trace), '    max:' ,max(self.trace), '    min:',min(self.trace)

        self.run()

class optimized_for_TV():
    def __init__(self,chan='CHAN1',typ='BYTE'):
        try:
            self.sock = vxi.Instrument('169.254.108.195')
            self.sock.write(':WAVeform:TYPE RAW')
            self.sock.write(':WAVEFORM:BYTEORDER LSBFirst')
            self.sock.write(':TIMEBASE:MODE MAIN')
            self.sock.write(':WAVEFORM:SOURCE ' + chan)
            self.sock.write(':WAVEFORM:FORMAT ' + typ)
        except:
            print "Wrong IP, Listening port or bad connection \n Check cables first"
            
    def get_data(self):
        self.sock.write(':WAV:DATA?')
        self.data = self.sock.read_raw()[10:]
        return numpy.fromstring(self.data, dtype=numpy.int8)

if __name__ == "__main__":
    
    usage = """usage: %prog [options] arg
               
    EXAMPLES:
    get_DSA -o my_output_file 1
    result in saving two files for the temporal trace of channel 1, the data and the scope parameters, called respectively my_output_file_DSACHAN1 and my_output_file_DSACHAN1.log
    
    get_DSA -o my_output_file 1,2
    Same as previous one but with 4 output files, two for each channel (1 and 2)
    
    
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
    parser.add_option("-o", "--filename", type="string", dest="filename", default='DEFAULT', help="Set the name of the output file" )
    parser.add_option("-m", "--measure", type="int", dest="measure", default=None, help="Set measurment number" )
    parser.add_option("-i", "--ipadd", type="string", dest="ipadd", default=IP, help="Set ip address" )
    (options, args) = parser.parse_args()
    
    ### Compute channels to acquire ###
    if len(args) == 0:
        print '\nYou must provide at least one channel\n'
        sys.exit()
    elif len(args) == 1:
        chan = []
        temp_chan = args[0].split(',')                  # Is there a coma?
        for i in range(len(temp_chan)):
            try:
                eval(temp_chan[i])
            except:
                print '\nPlease provide an existing channel (integer 1->4)\n'
                sys.exit()
            if eval(temp_chan[i]) not in [1,2,3,4]:
                print '\nPlease provide an existing channel (integer 1->4)\n'
                sys.exit()
            chan.append('CHAN' + temp_chan[i])
    else:
        chan = []
        for i in range(len(args)):
            try:
                eval(args[i])
            except:
                print '\nPlease provide an existing channel (integer 1->4)\n'
                sys.exit()
            if eval(args[i]) not in [1,2,3,4]:
                print '\nPlease provide an existing channel (integer 1->4)\n'
                sys.exit()
            chan.append('CHAN' + str(args[i]))
    print chan
    
    ### Initiate the class ###
    DSA_fast_oscillo(channel=chan,host=options.ipadd,filename=options.filename,MEAS=options.measure,INTERACTIVE=False)
    

    
