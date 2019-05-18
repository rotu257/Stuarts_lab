from numpy import *
from scipy import *
from math import *
from matplotlib.pyplot import *
import cPickle as cp
import time
import jobpython as j

import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import PDW_stuffs as P
import commands as C
from scipy.signal import savgol_filter
#mpl.pyplot.switch_backend('PS')

plt.style.use('classic')

mpl.rcParams['text.usetex'] = True
mpl.rcParams['font.family']     = 'sans-serif'
mpl.rcParams['font.sans-serif'] = 'Helvetica'
mpl.rcParams['ytick.major.size'] = 10.0
mpl.rcParams['xtick.major.size'] = 10.0
mpl.rcParams['ytick.major.width'] = 0.8
mpl.rcParams['xtick.major.width'] = 0.8
mpl.rcParams['axes.labelsize'] = 14
mpl.rcParams['xtick.labelsize'] = 12
mpl.rcParams['ytick.labelsize'] = 12
mpl.rcParams['mathtext.fontset'] = 'stix'
#mpl.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
mpl.rcParams['text.latex.unicode'] = True
mpl.rcParams['xtick.major.pad']='11'
mpl.rcParams['ytick.major.pad']='7'
mpl.rcParams['figure.subplot.bottom']=0.15
mpl.rcParams['figure.subplot.top']=0.90
mpl.rcParams['text.latex.preamble']=[r'\usepackage{mathptmx,sansmath,helvet,mathrsfs,amsmath}']
mpl.rcParams['axes.linewidth'] = 0.9

myb = '#1f77b4'
myo = '#ff7f0e'
myg = '#2ca02c'
myr = '#d62728'

def interactive_HIST():
    zero_H,zero_V = prerequisite()
    C.getoutput('rm 1_TEST*')
    
    fig = figure(101,figsize=(14,8))
    flag = 1
    while True:
        print flag
        C.getoutput('set_TTITGF3162 -c "CHNTRG TWO"')
        
        # Acquisition ...
        C.getoutput('get_DSO54853A -o 1_TEST 1,2')
        C.getoutput('get_DSA -o 1_TEST 1,2,4')
        
        # Processing and plot
        a = process_one_set(1,zero_H,zero_V,PLOT_HIST=fig)
        
        # Removing files
        C.getoutput('rm 1_TEST*')
        
        flag = flag+1
        
def interactive_double_S(meas_num=None,num_fig=123,QUICK=False,indices_1=None,indices_2=None,PLOT_TEMP=False,PLOT_HIST=False,RECUT=None,VAL=0.01,SMOOTH_HIST=False):
    """Code requirements: - temporal overlap between the triggers and signal pulses
                          - trigger positionned right in the middle of the window
                          - NO automatic thresholding of channel 3
                          - Be mindful of Switching Waves for RECUT
    """
    zero_H,zero_V = prerequisite()
    
    # Run the trigger positions once for the first data sets WARNING probably less precize
    if QUICK:
        indices_1,indices_2 = extract_temporalindices_from_trigger(1)
        print indices_1[0],indices_2[0]
        trace_TOT = C.getoutput('ls 1_*_DSACHAN3')
        trace     = fromfile(trace_TOT,int8)
        trace     = trace[:4050]
        THR_CH3   = 0.
        po = j.find_down(trace,THR_CH3)
        NB_R = 2
        if po[0]>indices_1[0]:
            di1 = po[0] - indices_1[0] -NB_R  #2pts removed for edge
            di2 = po[1] - indices_2[0] -NB_R
        else:
            di1 = po[1] - indices_1[0] -NB_R  #2pts removed for edge
            di2 = po[0] - indices_2[0] -NB_R
        print di1,di2
        higher_state_duration = 20
        RECUT = (di1,di2,higher_state_duration)
        VAL=0.05
        SMOOTH_HIST=11
    
    fig = figure(num_fig,figsize=(20,13))
    fig.clf()
    
    suptitle('Measurment '+str(meas_num)+'  (dot: pulse 1, cross: pulse 2, filled: before perturbation, unfilled: after perturbation)')
    
    subplot(421)
    title('Before perturbation')
    subplot(423)
    title('After perturbation')
    subplot(425)
    title('First pulse')
    subplot(427)
    title('Second pulse')
    subplot(122)
    title('All')
    
    idx = 1
    chi,p1_b_C1,p1_a_C1,p2_b_C1,p2_a_C1,p1_b_C2,p1_a_C2,p2_b_C2,p2_a_C2 = process_one_set(idx,zero_H,zero_V,indices_1=indices_1,indices_2=indices_2,PLOT_TEMP=PLOT_TEMP,PLOT_HIST=PLOT_HIST,RECUT=RECUT,VAL=VAL,SMOOTH_HIST=SMOOTH_HIST)
    while True:
        try:
            print 'Measurement index:',idx
            chi,p1_b_C1,p1_a_C1,p2_b_C1,p2_a_C1,p1_b_C2,p1_a_C2,p2_b_C2,p2_a_C2 = process_one_set(idx,zero_H,zero_V,indices_1=indices_1,indices_2=indices_2,PLOT_TEMP=PLOT_TEMP,PLOT_HIST=PLOT_HIST,RECUT=RECUT,VAL=VAL,SMOOTH_HIST=SMOOTH_HIST)
            figure(num_fig)
            subplot(421)
            [plot(chi,p1_b_C1[i],myb,marker='o') for i in range(len(p1_b_C1))]
            [plot(chi,p2_b_C1[i],myb,marker='P') for i in range(len(p2_b_C1))]
            [plot(chi,p1_b_C2[i],myo,marker='o') for i in range(len(p1_b_C2))]
            [plot(chi,p2_b_C2[i],myo,marker='P') for i in range(len(p2_b_C2))]
            
            subplot(423)
            [plot(chi,p1_a_C1[i],myb,marker='o',fillstyle='none') for i in range(len(p1_a_C1))]
            [plot(chi,p2_a_C1[i],myb,marker='P',fillstyle='none') for i in range(len(p2_a_C1))]
            [plot(chi,p1_a_C2[i],myo,marker='o',fillstyle='none') for i in range(len(p1_a_C2))]
            [plot(chi,p2_a_C2[i],myo,marker='P',fillstyle='none') for i in range(len(p2_a_C2))]
            
            subplot(425)
            [plot(chi,p1_b_C1[i],myb,marker='o') for i in range(len(p1_b_C1))]
            [plot(chi,p1_b_C2[i],myo,marker='o') for i in range(len(p1_b_C2))]
            [plot(chi,p1_a_C1[i],myb,marker='o',fillstyle='none') for i in range(len(p1_a_C1))]
            [plot(chi,p1_a_C2[i],myo,marker='o',fillstyle='none') for i in range(len(p1_a_C2))]
            
            subplot(427)
            [plot(chi,p2_b_C1[i],myb,marker='P') for i in range(len(p2_b_C1))]
            [plot(chi,p2_b_C2[i],myo,marker='P') for i in range(len(p2_b_C2))]
            [plot(chi,p2_a_C1[i],myb,marker='P',fillstyle='none') for i in range(len(p2_a_C1))]
            [plot(chi,p2_a_C2[i],myo,marker='P',fillstyle='none') for i in range(len(p2_a_C2))]
            
            subplot(122)
            [plot(chi,p1_b_C1[i],myb,marker='o') for i in range(len(p1_b_C1))]
            [plot(chi,p1_b_C2[i],myo,marker='o') for i in range(len(p1_b_C2))]
            [plot(chi,p1_a_C1[i],myb,marker='o',fillstyle='none') for i in range(len(p1_a_C1))]
            [plot(chi,p1_a_C2[i],myo,marker='o',fillstyle='none') for i in range(len(p1_a_C2))]
            [plot(chi,p2_b_C1[i],myb,marker='P') for i in range(len(p2_b_C1))]
            [plot(chi,p2_b_C2[i],myo,marker='P') for i in range(len(p2_b_C2))]
            [plot(chi,p2_a_C1[i],myb,marker='P',fillstyle='none') for i in range(len(p2_a_C1))]
            [plot(chi,p2_a_C2[i],myo,marker='P',fillstyle='none') for i in range(len(p2_a_C2))]
            
            fig.canvas.draw()
                
            idx = idx +1
        except:
            time.sleep(0.2)
    

def double_S():
    NB = len(C.getoutput('ls *DSO54853ACHAN1').splitlines())
    
    zero_H,zero_V = prerequisite()
    
    l_chi=[];l_p1_b_C1=[];l_p1_a_C1=[];l_p2_b_C1=[];l_p2_a_C1=[];l_p1_b_C2=[];l_p1_a_C2=[];l_p2_b_C2=[];l_p2_a_C2=[]
    for idx in range(1,NB+1):
        print 'Measurement index:',idx
        chi,p1_b_C1,p1_a_C1,p2_b_C1,p2_a_C1,p1_b_C2,p1_a_C2,p2_b_C2,p2_a_C2 = process_one_set(idx,zero_H,zero_V)
        l_chi.append(chi);l_p1_b_C1.append(p1_b_C1);l_p1_a_C1.append(p1_a_C1);l_p2_b_C1.append(p2_b_C1);l_p2_a_C1.append(p2_a_C1);l_p1_b_C2.append(p1_b_C2);l_p1_a_C2.append(p1_a_C2);l_p2_b_C2.append(p2_b_C2);l_p2_a_C2.append(p2_a_C2)       
    
    l_chi=array(l_chi);l_p1_b_C1=array(l_p1_b_C1);l_p1_a_C1=array(l_p1_a_C1);l_p2_b_C1=array(l_p2_b_C1);l_p2_a_C1=array(l_p2_a_C1);l_p1_b_C2=array(l_p1_b_C2);l_p1_a_C2=array(l_p1_a_C2);l_p2_b_C2=array(l_p2_b_C2);l_p2_a_C2=array(l_p2_a_C2)
    
    ### TO FINISH ###
    
    
def process_one_set(idx,zero_H,zero_V,PLOT_TEMP=False,PLOT_HIST=False,indices_1=None,indices_2=None,RECUT=None,VAL=0.01,SMOOTH_HIST=False):

    chi = evaluate_chi(idx,zero_H,zero_V)
    
    p1_b_C1,p1_a_C1,p2_b_C1,p2_a_C1 = evaluate_states_amplitude_by_channel(idx,channel='1',PLOT_TEMP=PLOT_TEMP,PLOT_HIST=PLOT_HIST,indices_1=indices_1,indices_2=indices_2,RECUT=RECUT,VAL=VAL,SMOOTH_HIST=SMOOTH_HIST)
    p1_b_C2,p1_a_C2,p2_b_C2,p2_a_C2 = evaluate_states_amplitude_by_channel(idx,channel='2',PLOT_TEMP=PLOT_TEMP,PLOT_HIST=PLOT_HIST,indices_1=indices_1,indices_2=indices_2,RECUT=RECUT,VAL=VAL,SMOOTH_HIST=SMOOTH_HIST)
    
    return chi,p1_b_C1,p1_a_C1,p2_b_C1,p2_a_C1,p1_b_C2,p1_a_C2,p2_b_C2,p2_a_C2


def evaluate_states_amplitude_by_channel(idx,channel='1',smooth_trace=0,nb_rt_choosen=4000,PLOT_TEMP=False,PLOT_HIST=False,indices_1=None,indices_2=None,RECUT=None,VAL=0.01,SMOOTH_HIST=False):
    trace_f = C.getoutput('ls %d_*_DSACHAN%s' %(idx,channel))
    trace   = fromfile(trace_f,int8)
    
    if indices_1 is None:
        indices_1,indices_2 = extract_temporalindices_from_trigger(idx)
    
    # Remove offset trace
    off = trace[indices_1[2]-500:indices_1[2]].mean()
    trace = trace + abs(off)
    
    trigger_duration = 200
    pulse_1 = array([trace[indices_1[i]:indices_1[i]+trigger_duration] for i in range(len(indices_1))]) 
    pulse_2 = array([trace[indices_2[i]:indices_2[i]+trigger_duration] for i in range(len(indices_2))])
    
    if RECUT:
        trigger_duration = RECUT[2]
        pulse_1 = array([pulse_1[i][RECUT[0]-trigger_duration:RECUT[0]] for i in range(len(pulse_1))])
        pulse_2 = array([pulse_2[i][RECUT[1]-trigger_duration:RECUT[1]] for i in range(len(pulse_2))])
    
    pulse_1 = pulse_1.ravel()
    pulse_2 = pulse_2.ravel()
    if smooth_trace!=0:
        pulse_1 = savgol_filter(pulse_1,smooth_trace,4)
        pulse_2 = savgol_filter(pulse_2,smooth_trace,4)

    # before perturbation
    pert_beg = len(pulse_1)/2
    pulse_1_b = pulse_1[:pert_beg-50*trigger_duration]   # stops 50 rt before by security
    pulse_2_b = pulse_2[:pert_beg-50*trigger_duration]
    
    # after perturbation
    NB_RT_MAX     = pert_beg - 150*trigger_duration   # not to hit the perturbation part 100rt pert duration 50 security
    if nb_rt_choosen>=NB_RT_MAX:
        print 'Fixing nb rt to maximal available not to hit the perturbation'
        nb_rt_choosen = NB_RT_MAX
    pulse_1_a = pulse_1[(-1)*trigger_duration*nb_rt_choosen:]
    pulse_2_a = pulse_2[(-1)*trigger_duration*nb_rt_choosen:]
    
    if PLOT_TEMP:
        fig2 = figure(102)
        fig2.clf()
        if channel=='1':
            color = myb
        elif channel=='2':
            color = myo
        zero_H,zero_V = prerequisite()
        print 'chi: ',evaluate_chi(idx,zero_H,zero_V)
        subplot(211)
        plot(pulse_1_b[:5*trigger_duration],color)
        plot(pulse_2_b[:5*trigger_duration],color)
        subplot(212)
        plot(pulse_1_a[(-1)*5*trigger_duration:],color)
        plot(pulse_2_a[(-1)*5*trigger_duration:],color)
        fig2.canvas.draw()
        #raw_input()
        
    p1_b,a1,b1,c1 = evaluate_histomaxs_from_trace(pulse_1_b,VAL=VAL,SMOOTH_HIST=SMOOTH_HIST)
    p1_a,a2,b2,c2 = evaluate_histomaxs_from_trace(pulse_1_a,VAL=VAL,SMOOTH_HIST=SMOOTH_HIST)
    p2_b,a3,b3,c3 = evaluate_histomaxs_from_trace(pulse_2_b,VAL=VAL,SMOOTH_HIST=SMOOTH_HIST)
    p2_a,a4,b4,c4 = evaluate_histomaxs_from_trace(pulse_2_a,VAL=VAL,SMOOTH_HIST=SMOOTH_HIST)
    
    if PLOT_HIST:
        fig3=figure(103)
        if channel=='1':
            fig3.clf()
            zero_H,zero_V = prerequisite()
            chi = evaluate_chi(idx,zero_H,zero_V)
            title('chi:   '+str(chi))
            plot(c1,b1,color=myb)
            plot(c2,b2,color=myb)
            plot(c3,b3,color=myb)
            plot(c4,b4,color=myb)
            [plot(p1_b[i],a1[i],color=myb,marker='o') for i in range(len(a1))]
            [plot(p1_a[i],a2[i],color=myb,marker='o',fillstyle='none') for i in range(len(a2))]
            [plot(p2_b[i],a3[i],color=myb,marker='P') for i in range(len(a3))]
            [plot(p2_a[i],a4[i],color=myb,marker='P',fillstyle='none') for i in range(len(a4))]
            #fig.canvas.draw()
        if channel=='2':
            #figure(101)
            plot(c1,b1,color=myo)
            plot(c2,b2,color=myo)
            plot(c3,b3,color=myo)
            plot(c4,b4,color=myo)
            [plot(p1_b[i],a1[i],color=myo,marker='o') for i in range(len(a1))]
            [plot(p1_a[i],a2[i],color=myo,marker='o',fillstyle='none') for i in range(len(a2))]
            [plot(p2_b[i],a3[i],color=myo,marker='P') for i in range(len(a3))]
            [plot(p2_a[i],a4[i],color=myo,marker='P',fillstyle='none') for i in range(len(a4))]
            fig3.canvas.draw()
            #raw_input('Press enter')
    
    # remove the zeros of the traces
    if RECUT is None:
        p1_b = p1_b + abs(p1_b[0])
        p1_a = p1_a + abs(p1_a[0])
        p2_b = p2_b + abs(p2_b[0])
        p2_a = p2_a + abs(p2_a[0])
    
    if RECUT is None:
        # return without the zeros
        return p1_b[1:],p1_a[1:],p2_b[1:],p2_a[1:]
    else:
        return p1_b,p1_a,p2_b,p2_a
    
def evaluate_histomaxs_from_trace(trace,VAL=0.01,SMOOTH_HIST=False):
    h,bi  = histogram(trace,bins=250,range=(-25,225))
    h     = h.astype(float64)/h.max()
    bi    = bi[:-1]
    if SMOOTH_HIST:
        h = savgol_filter(h,SMOOTH_HIST,4)
    
    ma,po = j.maxi(h)
    maxs  = [bi[po[i]] for i in range(len(ma)) if ma[i]> VAL]
    amaxs = [h[po[i]] for i in range(len(ma)) if ma[i]> VAL]
    
    return maxs,amaxs,h,bi
    
def extract_temporalindices_from_trigger(idx,smooth=5):
    trigger_f = C.getoutput('ls %d_*_DSACHAN4' %idx)
    trigger   = fromfile(trigger_f,int8)
    trigger   = j.f_smooth_data(trigger,smooth)
    
    # Compute histograms of the trigger states
    h,bi  = histogram(trigger,bins=250,range=(-125,125))
    h     = h.astype(float64)/h.max()
    bi    = bi[:-1]
    ma,po = j.maxi(h)
    VAL   = 0.03      # min val for max to be considered
    try:
        MIN,MEAN,MAX = [bi[po[i]] for i in range(len(ma)) if ma[i]> VAL]
    except:
        print 'Problem in file:', trigger_f
        print 'Too many maxima:', len([bi[po[i]] for i in range(len(ma)) if ma[i]> VAL])
        print [bi[po[i]] for i in range(len(ma)) if ma[i]> VAL]
    
    thr_min = (MIN + MEAN)/2. # Compute actual thresholds
    thr_max = (MAX + MEAN)/2.
    trigger[:smooth]  = MEAN  # remove potential glitch at beg and end due to smoothing
    trigger[-smooth:] = MEAN
    
    # From thr value return temporal indices
    indices_1 = j.find_down(trigger,thr_min)
    indices_2 = j.find_up(trigger,thr_max)
    
    return indices_1,indices_2
    
def prerequisite():
    zero_H = fromfile('../CALIB_ZERO_CHI_YELLOW_DSO54853ACHAN1',int8).mean()
    zero_V = fromfile('../CALIB_ZERO_CHI_GREEN_DSO54853ACHAN2',int8).mean()
    return zero_H,zero_V

def evaluate_chi(idx,zero_H,zero_V):
    H_f = C.getoutput('ls %d_*_DSO54853ACHAN1' %idx)
    V_f = C.getoutput('ls %d_*_DSO54853ACHAN2' %idx)
    H = fromfile(H_f,int8).mean()
    V = fromfile(V_f,int8).mean()
    H = H + abs(zero_H)
    V = V + abs(zero_V)
    chi = chi_from_HV(H,V)
    return chi

def chi_from_HV(H,V,cal=0.937):
    V = V*cal
    return 2* arctan(sqrt(V/H))*180/pi










