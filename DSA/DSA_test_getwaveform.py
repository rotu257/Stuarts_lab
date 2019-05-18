

import vxi11Device as vxi
import time


a = vxi.Vxi11Device("169.254.108.195",'inst0')

#a.write('*RST; :AUTOSCALE')

a.write(':STOP')
a.write(':WAVEFORM:SOURCE CHAN1')
a.write(':TIMEBASE:MODE MAIN')
#a.write(':ACQUIRE:TYPE NORMAL')
#a.write(':ACQUIRE:COUNT 1')

#a.write(':WAV:POINTS:MODE RAW')
#a.write(':WAV:POINTS 5000')
#a.write(':DIGITIZE CHAN1')



a.write(':WAVEFORM:FORMAT ASCII')
#a.write(':WAVEFORM:BYTEORDER LSBFirst')

print 'acquiring'
a.write(':WAV:DATA?')
print 'ici',a.read()

a.write(':RUN')

#preambleBlock = query(visaObj,':WAVEFORM:PREAMBLE?');
#% The preamble block contains all of the current WAVEFORM settings.  
#% It is returned in the form <preamble_block><NL> where <preamble_block> is:
#%    FORMAT        : int16 - 0 = BYTE, 1 = WORD, 2 = ASCII.
#%    TYPE          : int16 - 0 = NORMAL, 1 = PEAK DETECT, 2 = AVERAGE
#%    POINTS        : int32 - number of data points transferred.
#%    COUNT         : int32 - 1 and is always 1.
#%    XINCREMENT    : float64 - time difference between data points.
#%    XORIGIN       : float64 - always the first data point in memory.
#%    XREFERENCE    : int32 - specifies the data point associated with
#%                            x-origin.
#%    YINCREMENT    : float32 - voltage diff between data points.
#%    YORIGIN       : float32 - value is the voltage at center screen.
#%    YREFERENCE    : int32 - specifies the data point where y-origin
#%                            occurs.
#% Now send commmand to read data
