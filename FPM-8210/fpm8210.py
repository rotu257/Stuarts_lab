#!/usr/bin/python

from optparse import OptionParser
import sys
import visa as v
import commands as C
import gpib


class fpm8210():
        def __init__(self,query=None,command=None,FORCE=False,filename=None,SAVE=True):
            ### establish GPIB communication ###
            self.scope = gpib.dev(0,05)
           
             #gpib.write(scope,'ZERO')
             #gpib.write(scope,'ZERO?')
             #gpib.read(scope,1000)
     
                                      
           
             ### establish settings ###
          #  gpib.write(self.scope,'ZERO') 
            gpib.write(self.scope,'Filter FAST') 
            gpib.write(self.scope,'RANGE:AUTO 1')
            gpib.write(self.scope,'WAVE 980')






                       

            if query:                                         # to execute command from outside
                print '\nAnswer to query:',query
                self.write(query+'\n')
                rep = self.read()
                print rep,'\n'
                sys.exit()
            elif command:
                self.command = command
                print '\nExecuting command',self.command
                self.scope.write(self.command)
                print '\n'
                sys.exit()
                
            if filename:
                self.amp= self.get_power()

            ### TO SAVE ###
            if SAVE:
                temp = C.getoutput('ls').splitlines()                           # if file exist => exit
                for i in range(len(temp)):
                    temp_filename = filename + 'fpm8210'
                    if temp[i] == temp_filename:
                        print '\nFile ', temp_filename, ' already exists, change filename or remove old file\n'
                        sys.exit()
                
                f = open(filename + '_fpm8210','w')        # Save data
                f.write(self.data)
                f.close()
                
                
        def get_power(self,filename='test_save_file_',PLOT=False,typ='BYTE',SAVE=False):
            print "ACQUIRING..."
            #gpib.write(self.scope,'*IDN?')
            gpib.write(self.scope,'POWER?')            
            self.data = gpib.read(self.scope,1000) 
            print "CHEERS!!!"         
            return self.data

	

 
if __name__ == '__main__':

    usage = """usage: %prog [options] arg
               
               
       EXAMPLES:
                   
           get_fpm8210 -o filename 

               """
    parser = OptionParser(usage)
    parser.add_option("-q", "--query", type="str", dest="com", default=None, help="Set the query to use." )
    parser.add_option("-c", "--command", type="str", dest="com", default=None, help="Set the command to execute." )
    parser.add_option("-i", "--gpib_port", type="str", dest="gpib_port", default='1', help="Set the gpib port to use." )
    parser.add_option("-o", "--filename", type="string", dest="filename", default=None, help="Set the name of the output file" )
    parser.add_option("-F", "--force", type="string", dest="force", default=None, help="Allows overwriting file" )
    (options, args) = parser.parse_args()

    ### Start the talker ###
    fpm8210(query=options.com,filename=options.filename,FORCE=options.force)
