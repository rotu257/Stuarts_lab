#!/usr/bin/python  
# -*- coding: utf-8 -*-

from optparse import OptionParser
from pylab import plot,draw,savefig,xlabel,ylabel,ylim
from numpy import *
import os
import sys
import commands as C
import quick_plot as QP

class job_noel():
    def __init__(self,SAVE):
        
        # To instanciate the quick plot class
        QPI = QP.quick_plot(filename='USELESS',SAVE=SAVE)
        
        ## To query the value of the piezo and use as min of the ramp
        ST = C.getoutput('TLB_6700 -c SOURce:VOLTage:PIEZo?')
        
        STEP = 0.3                  # Step to use for the piezo in purcent
        MIN = eval(ST.split()[-1])  # Min value as the one you were at
        MAX = 100 + STEP            # Max value possible 100 purcent

        for piezo in arange(MIN,MAX,STEP):
            print 'Value of the piezo:', piezo
            QPI.filename = str(piezo)
            
            ## to set the value of the piezo of the TLB
            C.getoutput('TLB_6700 -p %f' %piezo)
            
            ## to get the data from the OSA
            C.getoutput('get_YOKO -t -i 169.254.166.208 -o %s' %piezo)

            ## to plot the data quickly
            QPI.plot()



if __name__ == "__main__":
    usage = """usage: %prog [options] arg
               
    EXAMPLES:
        job_noel.py -s
        
        
    """
    
    parser = OptionParser(usage)
    parser.add_option("-s", "--save", action = "store_true", dest="save", default=False, help="Do you want to save?" )
    (options, args) = parser.parse_args()
    
    job_noel(SAVE=options.save)
