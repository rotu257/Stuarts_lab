#!/usr/bin/python
import serial
import time


tmptime = time.strftime('%X %x %Z')  # get time stamp
fpath = "temperature_scan.txt"  # txt file path

with open(fpath, "a") as file:  # open file with append

    # open serial port
    port = '/dev/ttyUSB0'
    baud = 9600

    # 9600 8N1 DEFAULT
    with serial.Serial(port, baud, timeout=1) as ser:

        print('recording temperature')
        ser.flush()

        # get BK precision 710 display using ttyUSB0
        ser.write(b'D')
        line = ser.readline()  # read a '\n' terminated line
        ser.write(b'B')
        line2 = ser.readline()
        l1 = line.split()[1:]
        L1 = concatenate_list_data(l1)
        l2 = line2.split()[1:]
        L2 = concatenate_list_data(l2)
        fh.write(tmptime + ',' + L1 + ',' + L2 + '\n')
        # print line.split()
        print 'T1:', L1, ' ', 'T2:', L2
