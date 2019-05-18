
from numpy import *
from matplotlib.pyplot import *
from scipy import *
import commands as C
import os

L = C.getoutput('ls CALIB_DETEC_CHI/*muW_DSO54853ACHAN1 | sort -n').splitlines()
LL = C.getoutput('ls CALIB_DETEC_CHI/*muW_DSO54853ACHAN2 | sort -n').splitlines()

power  = []
yellow = []
green  = []

for i in range(len(L)):
    a = fromfile(L[i],int8)
    b = fromfile(LL[i],int8)
    idx = L[i].find('muW')
    
    power.append(float(L[i][len('CALIB_DETEC_CHI/'):idx]))
    if power[-1]==0.0:
        a0 = a.mean()
        b0 = b.mean()
        
    yellow.append(a.mean())
    green.append(b.mean())

figure(53)
clf()
subplot(211)
plot(power,yellow-a0,'or')
plot(power,green-b0,'og')

py = polyfit(power,yellow,1)
pg = polyfit(power[:-1],green[:-1],1)

cal = py[0]/pg[0]
print(cal)


a = fromfile('CALIB_DETEC_CHI/modminmax_DSO54853ACHAN1',int8)*1.0-a0
b = fromfile('CALIB_DETEC_CHI/modminmax_DSO54853ACHAN2',int8)*1.0-b0

#a/py[0] + b/pg[0]

subplot(212)
plot(a,'r')
plot(b,'g')
plot(a+b,'k')
plot((a/py[0]+b/pg[0])*py[0],'m')
