#!/usr/bin/python3
"""
python class to control Rohde-Schwarz RTP scope based on the RsInstrument package and pyvisa

"""

from RsInstrument import *  # The RsInstrument package is hosted on pypi.org, see Readme.txt for more details

resource_string_1 = 'TCPIP::131.225.137.193::inst0::INSTR'  # Standard LAN connection (also called VXI-11)
resource_string_2 = 'TCPIP::131.225.137.193::hislip0::INSTR'  # Hi-Speed LAN connection - see 1MA208

import sys


#LOG = 0

#name formate FILENAME_RUN.Wfm.bin
#

class Control(object):

    def __init__(self,FileName,N,instrAdd=resource_string_1,Location='"C:\Temp\\',FileFormat = '.bin',LOG=0):
        ''' 
        this function establish connection with the instrument at address resource_string_1
        FileName : rootname for the measurment file
        Location : rootlocation 
        FileFormat : bin with int,8 
        '''
        self.instrAdd = instrAdd
        self.N = N

        self.Location = Location
        self.FileFormat = FileFormat

        self.File = str(FileName)

        self.FileLocation = self.Location+str(self.File)#+'"'
        print (self.FileLocation)


        try:
            self.instr = RsInstrument(self.instrAdd)
            self.instr.VisaTimeout = 10000
            self.instr.instrument_status_checking=True

            if LOG: self.instr.logger.log_to_console = True; self.instr.logger.mode = LoggingMode.On

        except Exception as ex:
            print('Error initializing the instrument session:\n' + ex.args[0])
            exit()


    def close(self):
        self.instr.close()

    def preP(self,dtype='INT,8'):
        COMM = 'SYSTem:DISPlay:UPDate ON'
        self.instr.write_str(COMM)
        # Normal mode Trig
        self.instr.write_str('TRIG1:MODE NORM')
        # Exter mode Trig
        self.instr.write_str('TRIG1:SOUR EXT')
        # INT 8 data (binary)
        COMM = 'FORMat:DATA INT,8'
        self.instr.write(COMM)

    
        self.instr.query_opc()



    def setVscale(self,CHNum,SCALE,POS=0,OFF=0):
        CHAN = 'CHAN'+str(CHNum)
        COMM = CHAN+':POS '+str(POS)
        self.instr.write(COMM)

        COMM = CHAN+':OFFS '+str(OFF)
        self.instr.write(COMM)

        COMM = CHAN+':SCALE '+str(SCALE)
        self.instr.write(COMM)

        COMM = CHAN+':STATe ON' # turn on CH
        self.instr.write_str(COMM)

        self.instr.query_opc()

    def setHscale(self,SCALE,POS=0,OFF=0):
        COMM = 'TIM:SCAL '+str(SCALE)
        self.instr.write_str(COMM)
        
        self.instr.query_opc()


    def acqSetting(self,multiCH=True):
        COMM = 'EXPort:WAVeform:FASTexport ON'
        self.instr.write_str(COMM)
        if multiCH :
            COMM = 'EXPort:WAVeform:MULTichannel ON'
            self.instr.write_str(COMM)
        else:
            COMM = 'CHANnel1:WAVeform1:STATe 1'
            self.instr.write_str(COMM)
            
        COMM = 'ACQuire:COUNt '+str(self.N)

        self.instr.write_str(COMM)
        COMM = 'ACQ:SEGM:STAT ON'
        self.instr.write_str(COMM)
        self.instr.query_opc()


    def runSingle(self):
        COMM = 'RUNSingle'
        self.instr.write_str(COMM)
        self.instr.query_opc()



    def deleteData(self,run):

        CCOMM = 'MMEM:DEL '+self.FileLocation

        self.instr.write_str(COMM)


    def exportSetting(self,run):

        COMM = 'EXPort:WAVeform:SOURce C1W1'
        self.instr.write_str(COMM)
        COMM = 'EXPort:WAVeform:SCOPe WFM'
        self.instr.write_str(COMM)
        RUN = str(run).zfill(3)

        outputFile = self.FileLocation+RUN+self.FileFormat+'"'
        print (outputFile)

        self.instr.query_opc()
        COMM = 'EXPort:WAVeform:NAME '+outputFile
        self.instr.write_str(COMM)
        COMM = 'EXPort:WAVeform:RAW ON'
        self.instr.write_str(COMM)
        COMM = 'EXPort:WAVeform:INCXvalues OFF'
        self.instr.write_str(COMM)
        COMM = 'EXPort:WAVeform:DLOGging ON'
        self.instr.write_str(COMM)
        self.instr.query_opc()



    def playHistory(self,Hi,Hf=0):
        Hi = (-1*Hi) +1
        COMM = 'CHANnel1:WAV1:HISTory:STATe ON'
        self.instr.query_opc()
        self.instr.write_str(COMM)
        COMM = 'CHANnel1:WAV1:HISTory:STARt '+str(Hi)
        self.instr.write_str(COMM)
        COMM = 'CHANnel1:WAV1:HISTory:STOP '+str(Hf)
        self.instr.write_str(COMM)
        COMM = 'CHANnel1:WAV1:HISTory:REPLay OFF'
        self.instr.write_str(COMM)
        COMM = 'CHANnel1:WAV1:HISTory:PLAY'
        self.instr.write_str(COMM)
        self.instr.query_opc()

    def waitForCommand(self):
        self.instr.query_opc()


    def copyFile(self,run):
        self.instr.query_opc()
        RUN = str(run).zfill(3)
        self.FileLocation = self.FileLocation.strip('"')
        

        File0 = self.FileLocation+RUN+'.Wfm'+self.FileFormat
        File1 = self.FileLocation+RUN+self.FileFormat
        Local0 = self.File+RUN+'.Wfm'+self.FileFormat
        Local1 = self.File+RUN+self.FileFormat 
        print ('transfering files {} and {}'.format(File0,File1))
        self.instr.read_file_from_instrument_to_pc(File1,Local1)
        self.instr.query_opc()
        self.instr.read_file_from_instrument_to_pc(File0,Local0)
        self.instr.query_opc()
        print ('done')


if __name__ == '__main__':
    cont = Control('TEST')