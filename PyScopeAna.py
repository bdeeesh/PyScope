import numpy as np
import sys
from time import time
import xml.etree.ElementTree as ET


"""
set of functions to help analyise RTP scope int 8, bin data
can be used to read int 16 data as well
"""
#from scipy.integrate import simps

def getBinData(FILENAME,dType=np.int8):
    # assuming int8 data, load
    with open(str(FILENAME),'rb') as f: #BIN files with int8 (can be int16)
        BINWFM = np.fromfile(f,dtype=dType)
        print (int(len(BINWFM)/2))
        return (BINWFM)



def readHEADER(FILENAME):
    """
    Given a filename of .bin, the measurment information is extracted. The following is assumed:
    MultiChannel is active (2 channels are considered)

    """

    tree = ET.parse(FILENAME)
    root = tree.getroot()
    for child in root:
        for subelem in child:
            for x in subelem.iter('Prop'):
            # NofQuantisationLevels
                if x.get('Name') == 'NumberOfAcquisitions':  print ('NumberOfAcquisitions',x.get('Value')) ; N = int(x.get('Value'))
                if x.get('Name') == 'NofQuantisationLevels': print ('NofQuantisationLevels',x.get('Value')) ; COV = float(x.get('Value'))
            # resulution
                if x.get('Name') == 'Resolution': print ('Resulution',x.get('Value')); dt = float(x.get('Value'))
            # RecordLength 
                if x.get('Name') == 'RecordLength': print ('RecordLength',x.get('Value')); nt =int( x.get('Value'))
            # VerticalDivisionCount
                if x.get('Name') == 'VerticalDivisionCount': print ('VerticalDivisionCount',x.get('Value')); dV_COUNT = int(x.get('Value'))
            #TimeScale
                if x.get('Name') == 'TimeScale': print ('TimeScale',x.get('Value'))
            # I can add a statment for multi ch option
                if x.get('Name') == 'MultiChannelVerticalPosition': \
                print ('MultiChannelVerticalPosition',x.get('I_0'),x.get('I_1'),x.get('I_2'),x.get('I_3')) ;\
                CH1_POS,CH2_POS,CH3_POS,CH4_POS = float(x.get('I_0')),float(x.get('I_1')),float(x.get('I_2')),float(x.get('I_3'))
                if x.get('Name') == 'MultiChannelVerticalScale': \
                print ('MultiChannelVerticalScale',x.get('I_0'),x.get('I_1'),x.get('I_2'),x.get('I_3'));\
                CH1_dVpD,CH2_dVpD,CH3_dVpD,CH4_dVpD = float(x.get('I_0')),float(x.get('I_1')),float(x.get('I_2')),float(x.get('I_3'))
                if x.get('Name') == 'MultiChannelVerticalOffset': \
                print ('MultiChannelVerticalOffset',x.get('I_0'),x.get('I_1'),x.get('I_2'),x.get('I_3')); \
                CH1_OFF,CH2_OFF,CH3_OFF,CH4_OFF = float(x.get('I_0')),float(x.get('I_1')),float(x.get('I_2')),float(x.get('I_3'))

    return (N,COV,dt,nt,dV_COUNT,CH1_POS,CH2_POS,CH3_POS,CH4_POS,CH1_dVpD,CH2_dVpD,CH3_dVpD,CH4_dVpD,CH1_OFF,CH2_OFF,CH3_OFF,CH4_OFF)



def CONfactor(CH_dVpD,dV_COUNT,COV,CH_OFF,CH_POS):
    """
    Example: CH1_FAC,CH1_VOL_OFF = CONfactor(CH1_dVpD,dV_COUNT,COV,CH1_OFF,CH1_POS1) 
    """
    CH_FAC = (CH_dVpD* dV_COUNT/COV)
    CH_VOL_OFF = CH_OFF - (CH_dVpD*CH_POS)

    return (CH_FAC,CH_VOL_OFF)

# CH0Y0,CH1Y0,CH0Y1,CH1Y1....
splitCH = lambda BINDATA,N: BINDATA.reshape(N,2).T #where N is the number of samples in one channel (rearrange data)
# example BINCH1,BINCH2 = splitCH(BINWFM,int(len(BINWFM)/2))

getTime = lambda dt,nt: np.linspace(-1*dt*nt/2,dt*nt/2,nt)

getVoltage = lambda ADC,CH_N_FAC,CH_N_VOL_OFF: (ADC*CH_N_FAC) + CH_N_VOL_OFF # use convertsion factors for the voltage
# example CH1VOLT,CH2VOLT = getVoltage(BINCH1,CH1_FAC,CH1_VOL_OFF),getVoltage(BINCH2,CH2_FAC,CH2_VOL_OFF)


# usually the first 4 entries are useless:
# remove the first N points (need to be done for each CH, after the split)
fixCHdata = lambda CHVOLT,N : CHVOLT[N:]

# data analysis:

reShapeData = lambda CH,N,bt: CH.reshape(N,bt)


# averaging data

def removeBaseLine(CHVOLT,N,M,nt,log=False,returnBaseLine=False):
    """
    For each array (N x nt): 
    BaseLine = np.empty_like(CHVOLT)
        take the average of N-M, N+ M to get the base line
        remove the base line from the N data
        return the new array
    """
    # create empty arrays for baseline and new data:
    # assuming reShapeData was applied first
    BaseLine = np.empty_like(CHVOLT)
    NEWCH = np.empty_like(CHVOLT)


    for i in range(M,N-M):
        I = np.arange(i-M,i+M) # index to average over

        BaseLine[i] = np.average(np.array([CHVOLT[(v):(v+1)] for v in I]),axis=0) # the average 
        NEWCH[i] = CHVOLT[i]-BaseLine[i]
        if log and i%100 == 0: print("averaging frame number {}, from {} to {} ".format (i, I[0], I[-1]))
    if returnBaseLine:
        return (BaseLine,NEWCH)
    else:
        return NEWCH


def IntegratedData(CHVOLT,N,TIME,Log=False):
    INTEGCH = np.empty_like(CHVOLT)
    for i in range(N):
        t = time()

        #INTEGCH[i] = np.asarray([simps(CHVOLT[i][:m+1],dx=dt) for m in range(CHVOLT[i].size)]) Too slow
        INTEGCH[i] = np.asarray(np.cumsum(CHVOLT[i]))
        #polyfit to extract slope 
        coef = np.polyfit(TIME,INTEGCH[i],1)
        poly1d_fn = np.poly1d(coef)
        INTEGCH[i] = INTEGCH[i] - poly1d_fn(TIME)


        if Log and i % 100 == 0: print("Integrating frame number {} took {}".format (i, t - time()))
    return (INTEGCH)


def scopeData(DataName,HeaderName):
    N,COV,dt,nt,dV_COUNT,CH1_POS,CH2_POS,CH3_POS,CH4_POS,CH1_dVpD,CH2_dVpD,CH3_dVpD,CH4_dVpD,CH1_OFF,CH2_OFF,CH3_OFF,CH4_OFF = readHEADER(HeaderName)
    F0Data = getBinData(DataName)
    CH1_FAC,CH1_VOL_OFF = CONfactor(CH1_dVpD,dV_COUNT,COV,CH1_OFF,CH1_POS) 
    CH2_FAC,CH2_VOL_OFF = CONfactor(CH2_dVpD,dV_COUNT,COV,CH2_OFF,CH1_POS)
    BCH1,BCH2 = splitCH(F0Data,int(len(F0Data)/2))
    TIME = getTime(dt,nt)
    CH1V,CH2V = getVoltage(BCH1,CH1_FAC,CH1_VOL_OFF),getVoltage(BCH2,CH2_FAC,CH2_VOL_OFF)
    CH1V,CH2V = fixCHdata(CH1V,4),fixCHdata(CH2V,4)
    CH1V,CH2V = CH1V.reshape(N,nt),CH2V.reshape(N,nt)
    return CH1V,CH2V,TIME
    
    
    
    
