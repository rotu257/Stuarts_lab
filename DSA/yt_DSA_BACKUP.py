#!/usr/bin/python  
# -*- coding: utf-8 -*-

"""Look at 2D static data"""
from matplotlib.pyplot import axes, plot, figure, draw, show, rcParams
from matplotlib.widgets import Slider, Cursor
from numpy import array, roll, arange, sin, concatenate,\
        fromfile, uint8, int8, reshape, memmap, zeros, fromstring
from tempfile import TemporaryFile
from numpy.random import randn
import time
import sys
import commands as C
import matplotlib as mpl
from optparse import OptionParser
import vxi11 as vxi
import gobject
import matplotlib.pyplot as plt

plt.style.use('classic')
mpl.pyplot.switch_backend('GTkAgg')

class ytViewer(object):
    def __init__(self, filename, fold=19277, nmax=100,NORM=True,dtype=int8,DEB=0,shear_val=0.):
        self.UPDATE = True
        self.color  = True
        
        self.NORM      = NORM
        self.NMAX      = nmax
        self.fold      = fold
        self.increment = 5
        self.index     = 0
        self.shear_val = shear_val
        
        self.remove_len1 = 0
        self.remove_len2 = 1
        
        self.fig = figure(figsize=(16,7))
        
        self.data              = fromfile(filename,dtype=dtype)
        self.max_index         = int(len(self.data)/self.fold)
        self.data              = self.data[:self.max_index*self.fold]
        self.folded_data_orig2 = self.data.reshape(self.max_index,self.fold)
        self.folded_data_orig  = array(self.folded_data_orig2)
        self.folded_data_orig3 = array(self.folded_data_orig)
        self.folded_data       = self.folded_data_orig3[:self.NMAX]
        
        self.Y0 = 0
        
        self.ax = axes([0.1,0.4,0.8,0.47])
        if not self.NORM:
            self.im = self.ax.imshow(self.folded_data, interpolation='nearest', aspect='auto', origin='lower', vmin=0, vmax=255)
        else:
            self.im = self.ax.imshow(self.folded_data, interpolation='nearest', aspect='auto', origin='lower', vmin=self.data.min(), vmax=self.data.max())

        self.cursor = Cursor(self.ax, useblit=True, color='red', linewidth=2)

        self.axh = axes([0.1,0.05,0.8,0.2])
        self.hline, = self.axh.plot(self.folded_data[self.Y0,:])
        self.axh.set_xlim(0,len(self.folded_data[0,:]))
        self.axh.set_ylim(self.folded_data.min(),self.folded_data.max())
        
        # create 'remove_len1' slider
        self.remove_len1_sliderax = axes([0.1,0.925,0.8,0.02])
        self.remove_len1_slider   = Slider(self.remove_len1_sliderax,'beg',0.,self.fold*(3.5/4),self.remove_len1,'%d')
        self.remove_len1_slider.on_changed(self.update_tab)
        
        # create 'remove_len2' slider
        self.remove_len2_sliderax = axes([0.1,0.905,0.8,0.02])
        self.remove_len2_slider   = Slider(self.remove_len2_sliderax,'end',0.,self.fold*(3.5/4),self.remove_len2,'%d')
        self.remove_len2_slider.on_changed(self.update_tab)
        
        # create 'shear' slider
        self.shear_sliderax = axes([0.1,0.88,0.8,0.02])
        self.shear_slider   = Slider(self.shear_sliderax,'shear',-0.5,0.5,self.shear_val,'%1.3f')
        self.shear_slider.on_changed(self.update_shear)
        
        # create 'index' slider
        self.index_sliderax = axes([0.1,0.975,0.8,0.02])
        self.index_slider   = Slider(self.index_sliderax,'index',0,self.max_index-self.increment,0,'%d')
        self.index_slider.on_changed(self.update_param)
        
        # create 'nmax' slider
        self.nmax_sliderax = axes([0.1,0.955,0.8,0.02])
        self.nmax_slider   = Slider(self.nmax_sliderax,'nmax',0,self.max_index,self.NMAX,'%d')
        self.nmax_slider.on_changed(self.update_tab)
        
        cid  = self.fig.canvas.mpl_connect('motion_notify_event', self.mousemove)
        cid2 = self.fig.canvas.mpl_connect('key_press_event', self.keypress)

        self.axe_toggledisplay  = self.fig.add_axes([0.43,0.27,0.14,0.1])
        self.plot_circle(0,0,2,fc='#00FF7F')
        mpl.pyplot.axis('off')
        
        if self.shear_val!=0.: self.shear()
        gobject.idle_add(self.update_plot)
        show()
    
    def update_shear(self,value):
        self.shear_val = round(self.shear_slider.val,3)
        self.shear()
        self.update_tab(value)
        
    def update_param(self,value):
        self.index     = int(round(self.index_slider.val,0))
        self.update_tab(value)
        
    def shear(self):
        if self.shear_val == 0:
            pass
        dd = array(self.folded_data_orig2)
        for i in range(0,self.folded_data_orig2.shape[0]):
            dd[i,:] = roll(self.folded_data_orig2[i,:], int(i*self.shear_val))
        self.folded_data_orig = dd
        
    def update_tab(self,val):
        self.remove_len1 = int(self.remove_len1_slider.val)
        self.remove_len2 = int(self.remove_len2_slider.val)
        self.NMAX        = int(round(self.nmax_slider.val,0))
        
        self.folded_data_orig3 = array(self.folded_data_orig[:,self.remove_len1:-self.remove_len2])
        self.folded_data = self.folded_data_orig3[self.index:(self.index+self.NMAX)]
        
        self.Y0 = 0
        self.ax.clear()
        self.im     = self.ax.imshow(self.folded_data, interpolation='nearest', aspect='auto', origin='lower', vmin=self.data.min(), vmax=self.data.max())
        self.axh    = axes([0.1,0.05,0.8,0.2])
        self.axh.clear()
        self.hline, = self.axh.plot(self.folded_data[self.Y0,:])
        plt.ylim(self.folded_data.min(),self.folded_data.max())
        plt.xlim(0,len(self.folded_data[self.Y0,:]))
        draw()

    def update_plot(self):
        while self.UPDATE:
            self.folded_data = self.folded_data_orig3[self.index:(self.index+self.NMAX)]
            
            ### Update picture ###
            self.im.set_data(self.folded_data)
            self.hline.set_ydata(self.folded_data[self.Y0,:])
            self.index = self.index + self.increment
            self.index_slider.set_val(self.index)
            draw()

            return True
        return False

    def update_cut(self):
        self.hline.set_ydata(self.folded_data[self.Y0,:])
        draw()
        
    def keypress(self, event):
        if event.key == 'q': # eXit
            del event
            sys.exit()
        elif event.key=='n':
            del event
            self.NORM = not(self.NORM)
            if not self.NORM:
                self.ax.clear()
                self.im = self.ax.imshow(self.folded_data, interpolation='nearest', aspect='auto',
                origin='lower', vmin=0, vmax=255)
                self.axh.set_ylim(0, 255)
            else:
                self.ax.clear()
                self.im = self.ax.imshow(self.folded_data, interpolation='nearest', aspect='auto',
                origin='lower', vmin=self.folded_data.min(), vmax=self.folded_data.max())
                self.axh.set_ylim(self.folded_data.min(), self.folded_data.max())
        elif event.key == ' ': # play/pause
            self.toggle_update()
        else:
            print 'Key '+str(event.key)+' not known'
            
    def mousemove(self, event):
        # called on each mouse motion to get mouse position
        if event.inaxes!=self.ax: return
        self.X0 = int(round(event.xdata,0))
        self.Y0 = int(round(event.ydata,0))
        self.update_cut()
        
    def toggle_update(self):
            self.UPDATE = not(self.UPDATE)
            if self.UPDATE:
                gobject.idle_add(self.update_plot)
            self.color  = not(self.color)
            if not(self.color):
                self.patch.remove()
                self.axe_toggledisplay  = self.fig.add_axes([0.43,0.27,0.14,0.1])
                self.axe_toggledisplay.clear()
                self.plot_circle(0,0,2,fc='#FF4500')
                mpl.pyplot.axis('off')
                draw()
            else:
                self.patch.remove()
                self.axe_toggledisplay  = self.fig.add_axes([0.43,0.27,0.14,0.1])
                self.axe_toggledisplay.clear()
                self.plot_circle(0,0,2,fc='#00FF7F')
                mpl.pyplot.axis('off')
                draw()
                #gobject.idle_add(self.update_plot)
    
    def plot_circle(self,x,y,r,fc='r'):
        """Plot a circle of radius r at position x,y"""
        cir = mpl.patches.Circle((x,y), radius=r, fc=fc)
        self.patch = mpl.pyplot.gca().add_patch(cir)
        
    
if __name__=='__main__':

    usage = """usage: %prog [options] arg
               
               EXAMPLES:
                   ytExp_DSA -f 1000 -n 2000 1
               Show the interactive space/time diagram for 1000pts folding and 2000 rt acquired from the first channel


               """
    parser = OptionParser(usage)
    parser.add_option("-f", "--fold", type="int", dest="prt", default=364, help="Set the value to fold for yt diagram." )
    parser.add_option("-n", "--nmax", type="int", dest="nmax", default=560, help="Set the value to the number of roundtrip to plot." )
    parser.add_option("-d", "--deb", type="int", dest="deb", default=0, help="Change the beginning of data." )
    parser.add_option("-s", "--shear", type="float", dest="shear", default=0., help="Set initial value of the shear." )
    (options, args) = parser.parse_args()

    if len(args) == 0:
        print "\nEnter one filename\n"
    elif len(args) == 1:
        filename= str(args[0])
    else:
        print "\nEnter ONLY one filename\n"
    
    ### begin TV ###
    ytViewer(filename, fold=options.prt, nmax=options.nmax,DEB=options.deb,shear_val=options.shear)
      
#        ytExplorer(filename=sys.argv[1], rt=int(sys.argv[2]))


