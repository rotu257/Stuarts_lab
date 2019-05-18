#!/usr/bin/python  
# -*- coding: utf-8 -*-

"""Loot at 2D dynamic or static data"""
from matplotlib.pyplot import axes, plot, figure, draw, show, rcParams
from matplotlib.widgets import Slider, Cursor
from numpy import array, roll, arange, sin, concatenate,\
        fromfile, int8, reshape, memmap, zeros, fromstring
from tempfile import TemporaryFile
from numpy.random import randn
import time
import sys
import commands as C
import matplotlib as mpl
from optparse import OptionParser
import vxi11 as vxi
from multiprocessing import Process, Queue, Manager, Pipe
from multiprocessing.managers import SyncManager
import gobject

mpl.pyplot.switch_backend('GTkAgg')

IP = '169.254.108.195'

class ytViewer(object):
    def __init__(self, chan, host=IP, fold=1111, nmax=560, shear=0,NORM=True):
        self.UPDATE = True
        
        ########################### Setting up the processes ########################
        # set up communication between plotter and worker
        self.worker_connection, self.plotter_connection = Pipe()
        self.q = Queue()
        
        # set up shared variables
        self.params = Manager().dict({'chan':'CHAN1','host':host,'toggle':False,'SAVE':False})
        self.worker = Process(target=Acquire, args=(self.params, self.worker_connection,self.q))
        params = self.params   #Opening
        self.worker.start()
        ############################################################################
        
        self.flag_save = 1
        self.channel   = chan
        self.t             = time.time()
        self.NORM     = NORM
        self.NMAX     = nmax
        self.fold         = fold
        
        # create figure and timer
        self.fig = figure(figsize=(12,20))
        
        self.data = randn(self.NMAX*self.fold).reshape(self.NMAX,self.fold)
        self.processed_data = self.data
        
        # abscise and ordinates
        self.X0 = 0
        self.Y0 = 0
        self.Xrange = arange(self.data.shape[1])
        self.Yrange = arange(self.data.shape[0])
        
        # create image display
        self.ax = axes([0.1,0.3,0.6,0.5])
        if not self.NORM:
            self.im = self.ax.imshow(self.data, interpolation='nearest', aspect='auto',
		    origin='lower', vmin=0, vmax=255)
        else:
	        self.im = self.ax.imshow(self.data, interpolation='nearest', aspect='auto',
		    origin='lower', vmin=self.data.min(), vmax=self.data.max())
        
        self.cursor = Cursor(self.ax, useblit=True, color='red', linewidth=2)

        # create slider
        self.shearsliderax = axes([0.1,0.85,0.6,0.02])
        self.shearslider = Slider(self.shearsliderax,'Shear',-0.5,0.5,shear,'%1.2f')
        self.shearslider.on_changed(self.updateshear)

        # create horizontal cut
        self.axh = axes([0.1,0.1,0.6,0.1])
        self.hline, = self.axh.plot(self.Xrange, self.data[self.X0,:])

        # create vertical cut
        self.axv = axes([0.8,0.3,0.1,0.5])
       # self.vline, = self.axv.plot(data2[:,self.Y0], self.Yrange)

        self.set_cut_limits()

        # process data:
        self.shear_value = shear
        self.post_process()

        # connect to mouse events
        cid = self.fig.canvas.mpl_connect('motion_notify_event', self.mousemove)
        #cid = self.fig.canvas.mpl_connect('button_press_event', self.mouseclick)
        cid2 = self.fig.canvas.mpl_connect('key_press_event', self.keypress)

        gobject.idle_add(self.update_plot)
        show()


    def update_plot(self):
        while self.UPDATE: 
            print 'loading data:',time.time()-self.t
            self.t = time.time()
            
            ### receive from pipe ###
            self.bin_data   = self.plotter_connection.recv()
            self.data         = fromstring(self.bin_data, dtype=int8)
            self.processed_data = self.data[:self.NMAX*self.fold].reshape(self.NMAX,self.fold)
            print 'data loaded, update plot:',time.time()-self.t
            self.t = time.time()
            
            self.im.set_data(self.processed_data)    # ou .transpose()    ???
            
            #self.vline.set_ydata(self.processed_data[0])
            
            #self.post_process()
            print 'plot updated:',time.time()-self.t
            self.t = time.time()
            
            draw()
            
            return True
        return False

    def updateshear(self, value):
        self.shear_value = round(value,2)
        self.post_process()

    def post_process(self):
        # this should be called from outside so
        # that all processing is done in one shot
        
        #self.shear()
        self.im.set_data(self.processed_data)
        #self.update_cuts()

    def shear(self):
        # we can shear the data in order to compensate
        # for the incorrect folding
        if self.shear_value == 0: 
            self.processed_data = self.data
            return
        dd = self.data.copy()
        for i in range(0,self.data.shape[0]):
            dd[i,:] = roll(self.data[i,:], int(i*self.shear_value))
        self.processed_data = dd

    def keypress(self, event):
        if event.key == 'q': # eXit
            del event
            time.sleep(1)                                       # increase this value if oscillo bug when exiting 
            self.worker.terminate()
            sys.exit()
        elif event.key=='n':
            del event
            self.NORM = not(self.NORM)
            if not self.NORM:
                self.ax.clear()
                self.im = self.ax.imshow(self.processed_data, interpolation='nearest', aspect='auto',
                origin='lower', vmin=0, vmax=255)
            else:
                self.ax.clear()
                self.im = self.ax.imshow(self.processed_data, interpolation='nearest', aspect='auto',
                origin='lower', vmin=self.processed_data.min(), vmax=self.processed_data.max())
        elif event.key == ' ': # play/pause
            params              = self.params
            params['toggle'] = not(params['toggle'])
            self.params        = params
            #self.toggle_update()
        elif event.key == 'S':
            params = self.params
            params['SAVE']         = True
            self.params = params
            time.sleep(1)
            filename = 'Image_'+str(self.flag_save)+'_DSA'+str(self.channel)
            self.fig.savefig(filename+'.png')
            self.flag_save = self.flag_save + 1
        else:
            print 'Key '+str(event.key)+' not known'
            
    def mousemove(self, event):
        # called on each mouse motion to get mouse position
        if event.inaxes!=self.ax: return
        self.X0 = int(event.xdata+0.5)
        self.Y0 = int(event.ydata+0.5)
        self.update_cuts()

    def update_cuts(self):
        # called on each mouse motion to update profiles
        self.hline.set_ydata(self.processed_data[self.Y0,:])
        #self.vline.set_xdata(self.data2[:,self.X0])
        draw()
        
    def set_cut_limits(self):
        # set correct limits for the profiles
        self.axh.set_xlim(0,self.processed_data.shape[1])
        #self.axh.set_ylim(self.processed_data.min(), self.processed_data.max())
        self.axh.set_ylim(0, 255)
        #self.axv.set_xlim(self.processed_data.min(), self.processed_data.max())
        self.axv.set_xlim(0, 255)
        self.axv.set_ylim(0,self.processed_data.shape[0])
        
    def toggle_update(self):
            self.UPDATE = not(self.UPDATE)
            if self.UPDATE:
                gobject.idle_add(self.update_plot)

class Acquire():
    def __init__(self, parameters=dict({'chan':'CHAN1','host':IP,'toggle':False,'SAVE':False}), pipe=None, queue=None):
        self.UPDATE =False
        self.flag_save = 1
        
        self.parameters = parameters
        self.set_parameters(self.parameters)
        self.toggle2       = False
        
        if pipe is not None:
            self.pipe = pipe
            self.UPDATE = True
            self.q = queue
            
        try:
            self.sock = vxi.Instrument('169.254.108.195')
            self.sock.write(':WAVeform:TYPE RAW')
            self.sock.write(':WAVEFORM:BYTEORDER LSBFirst')
            self.sock.write(':TIMEBASE:MODE MAIN')
            self.sock.write(':WAVEFORM:SOURCE ' + parameters['chan'])
            self.sock.write(':WAVEFORM:FORMAT BYTE')
        except:
            print "Wrong IP, Listening port or bad connection \n Check cables first"

        self.load_data_loop()
        #self.processed = randn(1000000)[:self.NMAX*self.fold].reshape(self.NMAX,self.fold)
        
    def load_data_loop(self):
        parameters = self.parameters
        while self.UPDATE:
            self.set_parameters(self.parameters)
            self.load_data()
            self.pipe.send(self.bin_data)
            if self.toggle:
                print 'YEP'
                self.toggle_update_oscillo(parameters['toggle'])
                parameters['toggle'] = not(parameters['toggle'])
                self.parameters = parameters
            elif self.SAVE:
                self.Save()
                parameters['SAVE'] = False
                self.parameters = parameters
            
            
    def load_data(self):
   #     self.processed = randn(1000000)[:self.NMAX*self.fold].reshape(self.NMAX,self.fold)
        self.sock.write(':WAV:DATA?')
        self.bin_data = self.sock.read_raw()[10:]

    def toggle_update_oscillo(self,toggle):
            if not(self.toggle2):
                self.toggle2 = not(self.toggle2)
                self.stop()
            else:
                self.toggle2 = not(self.toggle2)
                self.run()

    def Save(self):
        if self.UPDATE: self.stop                               # set pause if not already
        filename = 'Image_'+str(self.flag_save)+'_DSA'+str(self.chan)
        print 'Saving to files ', filename
        ff = open(filename,'w')
        ff.write(self.bin_data)
        ff.close()
        self.sock.write(':WAVEFORM:SOURCE ' + self.chan)
        self.sock.write(':WAVEFORM:PREAMBLE?')
        self.preamble = self.sock.read()
        f = open(filename+'_log','w')
        f.write(self.preamble)
        f.close()

        self.flag_save = self.flag_save + 1

    def run(self):
        self.sock.write('RUN')
    
    def stop(self):
        self.sock.write('STOP')
        
    def set_parameters(self, parameters):
        for p in parameters.keys():
            setattr(self, p, parameters[p])
    
if __name__=='__main__':
    usage = """usage: %prog [options] arg
               
               EXAMPLES:
                   scope_DSA -f 1000 -n 2000 1
               Show the interactive space/time diagram for 1000pts folding and 2000 rt


               """
    parser = OptionParser(usage)
    parser.add_option("-f", "--fold", type="int", dest="prt", default=364, help="Set the value to fold for yt diagram." )
    parser.add_option("-n", "--nmax", type="int", dest="nmax", default=560, help="Set the value to the number of roundtrip to plot." )
    (options, args) = parser.parse_args()

    if len(args) == 0:
        print "\nEnter one channel\n"
    elif len(args) == 1:
        chan= 'CHAN' + str(args[0])
    else:
        print "\nEnter ONLY one channel\n"
    
    ### begin TV ###
    ytViewer(chan, host=IP, fold=options.prt, nmax=options.nmax)
      
#        ytExplorer(filename=sys.argv[1], rt=int(sys.argv[2]))


