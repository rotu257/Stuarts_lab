#!/usr/bin/python

import vxi11 as v
from optparse import OptionParser
import sys
import commands as C
import time
from numpy import fromstring,int8,int16,float64,sign

IP = '169.254.166.206'

class Lecroy():
        def __init__(self,channel=None,encoding='BYTE',spe_mode=None,filename=None, FACT=8.,query=None,command=None,FORCE=False,PRINT=False,chan_spe=None):
            if encoding=='BYTE':dtype=int8;NUM=256;LIM=217.          # 15% less than the maximal number possible
            elif encoding=='WORD':dtype=int16;NUM=65536;LIM=55700.   # 15% less than the maximal number possible
            
            ### Initiate communication ###
            self.command = command
            self.scope = v.Instrument(IP)
            
            ### Format of answers ###
            self.scope.write('CFMT DEF9,'+encoding+',BIN')
            self.scope.write('CHDR SHORT')
            
            if query:
                self.command = query
                print '\nAnswer to query:',self.command
                rep = self.query(self.command)
                print rep,'\n'
                sys.exit()
            elif command:
                self.command = command
                print '\nExecuting command',self.command
                self.scope.write(self.command)
                print '\n'
                sys.exit()
                
            self.prev_trigg_mode = self.query('TRMD?')
            print self.prev_trigg_mode
            
            if filename:
                self.single()
                while self.query('TRMD?') != 'TRMD STOP':
                    time.sleep(0.05)
                    pass
                    
                ### Check if channels are active ###
                for i in range(len(channel)):
                    temp = self.query(channel[i]+':TRA?')
                    if temp.find('ON') == -1:
                        print '\nWARNING:  Channel',channel[i], 'is not active  ===>  exiting....\n'
                        sys.exit()
                ### Acquire and save datas ###
                for i in range(len(channel)):
                    ### Allow auto scaling the channel gain and offset ###
                    k = 1
                    if spe_mode:
                        if channel[i] not in chan_spe:
                            print 'trying to get channel',channel[i]
                            self.get_data(chan=channel[i],filename=filename,SAVE=True,FORCE=FORCE)
                            continue
                        else:
                            while k <= spe_mode:
                                stri = self.query(channel[i]+':PAVA? MIN,MAX')
                                temp2 = 'MIN,'
                                temp3 = stri.find(temp2)
                                temp4 = stri.find(' V')
                                mi    = eval(stri[temp3+len(temp2):temp4])
                                stri = stri[temp4+len(' V'):]
                                temp2 = 'MAX,'
                                temp3 = stri.find(temp2)
                                temp4 = stri.find(' V')
                                ma    = eval(stri[temp3+len(temp2):temp4])
                                diff = abs(mi) + abs(ma)
                                #print 'prev_amp:  ',diff
                                temp5    = channel[i]+':VDIV'
                                temp5_o  = channel[i]+':OFST'
                                #print 'MIN,MAX:   ',mi,ma
                                
                                ########## To modify offset and amplitude ###########
                                val = round((-1)*diff/2. + abs(mi),3)
                                self.scope.write(temp5_o+' '+str(val))                            
                                new_channel_amp  = round(diff/FACT,3)
                                if new_channel_amp<0.005:        # if lower than the lowest possible 5mV/div
                                    new_channel_amp = 0.005
                                self.scope.write(temp5+' '+str(new_channel_amp))
                                #####################################################
                                
                                self.single()
                                while self.query('TRMD?') != 'TRMD STOP':
                                    time.sleep(0.05)
                                    pass
                                print 'Optimisation loop index:', k,spe_mode
                                
                                ############### Checking part #######################
                                if k==spe_mode:
                                    VDIV = eval(self.query(temp5+'?').split(' ')[1])
                                    OFST = eval(self.query(temp5_o+'?').split(' ')[1])
                                    R_MI = -(4.5 * VDIV) - OFST
                                    R_MA =   4.5 * VDIV  - OFST
                                    stri = self.query(channel[i]+':PAVA? MIN,MAX')
                                    temp2 = 'MIN,'
                                    temp3 = stri.find(temp2)
                                    temp4 = stri.find(' V')
                                    mi    = eval(stri[temp3+len(temp2):temp4])
                                    stri = stri[temp4+len(' V'):]
                                    temp2 = 'MAX,'
                                    temp3 = stri.find(temp2)
                                    temp4 = stri.find(' V')
                                    ma    = eval(stri[temp3+len(temp2):temp4])
                                    if mi<R_MI or ma>R_MA:                        #if trace out of the screen optimize again
                                        print '(SCOPE)   Min:',R_MI,' Max:',R_MA
                                        print '(TRACE)   Min:',mi,' Max:',ma
                                        k = k-1
                                        
                                ####################################################
                                
                                k = k+1
                            
                        ### END of spe_mode #################################
                    
                    print 'trying to get channel',channel[i]
                    self.get_data(chan=channel[i],filename=filename,SAVE=True,FORCE=FORCE)
            else:
                print 'If you want to save, provide an output file name'
            
            ### Run the scope BACK in the previous trigger mode###
            self.run()
            
        
        def query(self, cmd, nbytes=1000000):
            """Send command 'cmd' and read 'nbytes' bytes as answer."""
            self.scope.write(cmd)
            r = self.scope.read(nbytes)
            return r
        

        def get_data(self,chan='C1',filename='test_save_file_',PLOT=False,SAVE=False,LOG=True,FORCE=False,RET=False):
            self.data = self.query_data(chan)
            print len(self.data)
            ### TO SAVE ###
            if SAVE:
                temp = C.getoutput('ls').splitlines()                           # if file exist => exit
                for i in range(len(temp)):
                    temp_filename = filename + '_lecroy' + chan
                    if temp[i] == temp_filename and not(FORCE):
                        print '\nFile ', temp_filename, ' already exists, change filename or remove old file\n'
                        sys.exit()
                
                f = open(filename + '_lecroy' + chan,'w')                   # Save data
                f.write(self.data)
                f.close()
                
                if LOG:
                    self.preamb = self.get_log_data(chan)             # Save scope configuration
                    f = open(filename + '_lecroy' + chan + '.log','w')
                    f.write(self.preamb)
                    f.close()
                print  chan + ' saved'
            if RET:
                return self.data
        
        def get_log_data(self,chan):
            rep = self.query(chan+":INSP? 'WAVEDESC'")
            return rep          
        
        def stop(self):
            self.scope.write("TRMD STOP")
        def single(self):
            self.scope.write("TRMD SINGLE")
        def run(self):
            self.scope.write(self.prev_trigg_mode)
        
        def query_data(self, chan, fname=None, force=None,):
            ## trigger SINGLE
            chan = str(chan)
            self.scope.write(chan+':WF? DAT1')
            data = self.scope.read_raw()
            return data[data.find('#')+11:-1]

        
if __name__ == '__main__':

    usage = """usage: %prog [options] arg

               EXAMPLES:
                   get_lecroy 1 -o filename
               Record the first channel and create two files name filename_lecroy and filename_lecroy.log
               
               get_lecroy -F -m 2,3,4 -o test 2,3,4

               
               IMPORTANT INFORMATIONS:
                    - Datas are obtained in a binary format: int8 
                    - To retrieve datas (in "VERTUNIT"), see corresponding log file:
                    DATA(VERTUNIT) = DATA(ACQUIRED) * VERTICAL_GAIN - VERTICAL_OFFSET
                    
                See for more informations:  Stuarts_lab/Prog_guide/Lecroy.pdf

               """
    parser = OptionParser(usage)
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to use." )
    parser.add_option("-q", "--query", type="str", dest="que", default=None, help="Set the query to use." )
    parser.add_option("-o", "--filename", type="string", dest="filename", default=None, help="Set the name of the output file" )
    parser.add_option("-F", "--force",action = "store_true", dest="force", default=None, help="Allows overwriting file" )
    parser.add_option("-e", "--encoding", type="string", dest="encoding", default='BYTE', help="For mofifying the encoding format of the answer" )
    parser.add_option("-m", "--spe_mode", type="string", dest="spe_mode", default=None, help="For allowing auto modification of the vertical gain. List of: spe_mode iteration number, all the channels to apply spe mode on. Note if no channel precized, all the channel are corrected. WARNING: if you want all the channels to correpond to the same trigger event, you need to spe_mode one channel only and to physically plug the cable in the first channel acquired (first in the list 1->4)")
    parser.add_option("-n", "--spe_fact", type="float", dest="spe_fact", default=8., help="For setting limits of the vertical gain, units are in number of scope division. Do not overpass 9 due to a security in the code!" )
    (options, args) = parser.parse_args()
    
    ### Compute channels to acquire ###
    if (len(args) == 0) and (options.com is None) and (options.que is None):
        print '\nYou must provide at least one channel\n'
        sys.exit()
    elif len(args) == 1:
        chan = []
        temp_chan = args[0].split(',')                  # Is there a coma?
        for i in range(len(temp_chan)):
            chan.append('C' + temp_chan[i])
    else:
        chan = []
        for i in range(len(args)):
            chan.append('C' + str(args[i]))
    print 'Channel(s):   ', chan
    ####################################
    ### Compute channels for spe_mode to acquire ###
    if options.spe_mode:
        if len(options.spe_mode) > 1:
            spe_mode       = eval(options.spe_mode)[0]
            spe_mode_chans = eval(options.spe_mode)[1:]
            chan_spe = []
            for i in range(len(spe_mode_chans)):
                chan_spe.append('C'+str(spe_mode_chans[i]))
            print 'Special mode Channel(s):   ', chan_spe
        else:
            chan_spe = chan
            spe_mode = eval(options.spe_mode)
            print 'Special mode Channel(s):   ', chan_spe
    else:
        chan_spe = None
        spe_mode = options.spe_mode
    ####################################
    
    ### Start the talker ###
    Lecroy(channel=chan,encoding=options.encoding,spe_mode=spe_mode,query=options.que,command=options.com,filename=options.filename,FORCE=options.force,FACT=options.spe_fact,chan_spe=chan_spe)
    
