#!/usr/bin/python

import visa as v
from optparse import OptionParser
import sys
import time
import vxi11 as vxi
from numpy import mean,fromstring,int8

COLOR = 'ivory'

PLOT_ERROR = True
if PLOT_ERROR:
    from collections import deque
    import gobject
    from matplotlib.pylab import *
    from matplotlib.widgets import Slider
    matplotlib.pyplot.switch_backend('GTkagg')


class PID_perso():
        def __init__(self,query=None,command=None,setpoint=0.1):
            
            self.P = -0.1               # gain
            self.I = 13  * 10**(0)      # 1/Ti
            self.D = 0.1 * 10**(-5)     # Td
            self.setpoint = setpoint    # setpoint in volts
            
            self.previous_error = 0.
            self.integral = 0.
            
            self.UPDATE     = True
            self.size_error = 500
            self.chan       = 'CHAN2'
            self.typ        = 'ASC'
            
            r = v.ResourceManager('@py')
            
            ### Connect to te fonction generator ###
            
            try:
                self.agilent = r.get_instrument('GPIB::10::INSTR')
            except:
                print 'Problem with connection to FUNCTION GENERATOR => Check cables and address'
                
            ### Connect to the scope ###
            
            try:
                self.scope = vxi.Instrument('169.254.108.195')
                self.scope.write(':WAVeform:TYPE RAW')
                self.scope.write(':WAVEFORM:BYTEORDER LSBFirst')
                self.scope.write(':TIMEBASE:MODE MAIN')
                self.scope.write(':WAV:SEGM:ALL ON')
            except:
                print 'Problem with connection to SCOPE => Check cables and address'
      
            
            if query:
                self.command = query
                print '\nAnswer to query:',self.command
                self.scope.write(query)
                rep = self.scope.read()
                print rep,'\n'
                self.exit()
            elif command:
                self.command = command
                print '\nExecuting command',self.command
                self.write(self.command)
                print '\n'
                self.exit()
            
            print 'Communication okay'
            
            self.t  = time.time()
            self.dt = 0.1
            
            if PLOT_ERROR:
                ### Building list and figure ###
                self.deque_error = deque(list(zeros(self.size_error)))
                self.fig         = figure(31)
                
                key_connection   = self.fig.canvas.mpl_connect('key_press_event', self.keypress)
                
                self.ax          = self.fig.add_axes([0.1, 0.1, 0.8, 0.6], axisbg=COLOR)
                self.line_error, = plot(self.deque_error)
                ylim(-0.12,0.12)
                
                # Slider declarations
                self.aP        = self.fig.add_axes([0.1, 0.7, 0.8, 0.08])
                self.aP_slider = Slider(self.aP,'$P$',-1,1,self.P,'%1.5f')
                self.aP_slider.on_changed(self.update_param)
                self.aI         = self.fig.add_axes([0.1, 0.8, 0.8, 0.08])
                self.aI_slider = Slider(self.aI,'$I$',0,10**3,self.I,'%1.5f')
                self.aI_slider.on_changed(self.update_param)
                self.aD         = self.fig.add_axes([0.1, 0.9, 0.8, 0.08])
                self.aD_slider = Slider(self.aD,'$D$',10**(-5),10**(-3),self.D,'%1.5f')
                self.aD_slider.on_changed(self.update_param)
                
                gobject.idle_add(self.PID_controller_GUI)
                
                show()
                
            
            else:
                self.PID_controller()
            
        def update_param(self,val):
            self.P = round(self.aP_slider.val,5)
            self.I = round(self.aI_slider.val,5)
            self.D = round(self.aD_slider.val,5)
        
        def PID_controller(self):
            ### Controller function ###
            while self.UPDATE:
                # Get the current value
                measured_value = self.get_value()
                
                print 'average voltage:',measured_value
                
                ## Core of the controller
                error = self.setpoint - measured_value
                self.integral = self.integral + error*self.dt
                derivative = (error - self.previous_error)/self.dt
                output = self.P*(error + self.I*self.integral + self.D*derivative)
                self.previous_error = error
                
                # Send the value to the function generator
                self.send_computed_value(output)
                
                self.dt = time.time() - self.t
                self.t  = time.time()
                print self.dt
                
        
        def PID_controller_GUI(self):
            ### Controller function ###
            while self.UPDATE:
                # Get the current value
                measured_value = self.get_value()
                
                print 'average voltage:',measured_value
                
                ## Core of the controller
                error = self.setpoint - measured_value
                self.integral = self.integral + error*self.dt
                derivative = (error - self.previous_error)/self.dt
                output = self.P*(error + self.I*self.integral + self.D*derivative)
                self.previous_error = error
                
                ### Updating list and figure ###
                self.deque_error.popleft()
                self.deque_error.append(error)
                self.line_error.set_ydata(self.deque_error)
                    
                # Send the value to the function generator
                self.send_computed_value(output)
                
                self.dt = time.time() - self.t
                self.t  = time.time()
                print self.dt
                
                draw()
                return True
            return False
            
            
        def send_computed_value(self,offset):
            #offset = offset - 0.005                      # arbitrary waveform with -5mV DC and 10mV amp
            print 'OFFSET APLLIED:',offset
            if abs(offset)>=5.:
                self.agilent.write('VOLT:OFFS '+str(-0.005))
                self.previous_error = 0.
                self.integral = 0.
                #self.exit()
            else:    
                self.agilent.write('VOLT:OFFS '+str(offset))
 
 
        def get_value(self):
            """ Get the current value from the scope """
            self.scope.write(':WAVEFORM:SOURCE ' + self.chan)
            self.scope.write(':WAVEFORM:FORMAT ' + self.typ)
            
            #self.scope.write(':MEASure:VAVerage?')
            self.scope.write(':WAV:DATA?')
            return mean(eval(self.scope.read_raw()))    #mean(fromstring(self.scope.read_raw()[10:],dtype=int8))
            
        def keypress(self, event):
            if event.key == 'q':                # quit
                del event
                self.agilent.write('VOLT:OFFS '+str(-0.005))
                sys.exit()
            #elif event.key == ' ':                # pause
                #self.toggle_update()
                #del event
            else: 
                print("key ", event.key, " is not known")
        
        def exit(self):
            sys.exit()         # to set offset to 0 for disconnecting
            

if __name__ == '__main__':

    usage = """usage: %prog [options] arg
               
               
               EXAMPLES:
                   


               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-s", "--setpoint", type="float", dest="setpoint", default=0.1, help="Set the setpoint" )
    (options, args) = parser.parse_args()
    
    ### Start the talker ###
    PID_perso(query=options.que,command=options.com,setpoint=options.setpoint)
