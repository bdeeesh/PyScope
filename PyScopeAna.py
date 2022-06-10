import numpy as np
import sys
from time import time
import xml.etree.ElementTree as ET

#from scipy.integrate import simps

def getBinData(FILENAME,dType=np.int8):
    # data can be int.8 or int.16 
    with open(str(FILENAME),'rb') as f: #BIN files with int8 (can be int16)
        BINWFM = np.fromfile(f,dtype=dType)
        #print (int(len(BINWFM)/2))
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


def scopeData(DataName,HeaderName,BaseLineRemove=False,integData=False):
        N,COV,dt,nt,dV_COUNT,CH1_POS,CH2_POS,CH3_POS,CH4_POS,CH1_dVpD,CH2_dVpD,CH3_dVpD,CH4_dVpD,CH1_OFF,CH2_OFF,CH3_OFF,CH4_OFF = readHEADER(HeaderName)
        if COV == 64768:
            dtype = np.int16
            nd = 4
        elif COV == 253:
            dtype = np.int8
            nd = 8
        else:
            print ('data type unknown')
            exit() 
        
        F0Data = getBinData(DataName,dtype)
        
        F0Data = F0Data[nd:]
        
    
        CH1_FAC,CH1_VOL_OFF = CONfactor(CH1_dVpD,dV_COUNT,COV,CH1_OFF,CH1_POS) 
        CH2_FAC,CH2_VOL_OFF = CONfactor(CH2_dVpD,dV_COUNT,COV,CH2_OFF,CH1_POS)
        BCH1,BCH2 = splitCH(F0Data,int(len(F0Data)/2))
        TIME = getTime(dt,nt)
        CH1V,CH2V = getVoltage(BCH1,CH1_FAC,CH1_VOL_OFF),getVoltage(BCH2,CH2_FAC,CH2_VOL_OFF)
    
        CH1V,CH2V = CH1V.reshape(N,nt),CH2V.reshape(N,nt)
        if BaseLineRemove and not integData:
            CH1RB = removeBaseLine(CH1V,N,10,nt)
            return CH1V,CH2V,CH1RB,TIME
        if integData and not BaseLineRemove:
            CH1INTG = IntegratedData(CH1V,N,TIME)
            return CH1V,CH2V,CH1INTG,TIME
        if BaseLineRemove and integData:
            CH1RB = removeBaseLine(CH1V,N,10,nt)
            CH1INTG = IntegratedData(CH1V,N,TIME)
            return CH1V,CH2V,CH1RB,CH1INTG,TIME
        else:
            return CH1V,CH2V,TIME
    
    
    
def getPosition(CH,point,N):
        POS = np.empty(N)
        for j in range(N):
            x = CH[j][point]
            POS[j] = x
        return POS
    
def getTuneSpec(POS,dn=1):
        PowSpec = np.absolute(np.fft.rfft(POS))
        n = POS.size
        tune = np.fft.rfftfreq(n,dn)
        return (tune,PowSpec)
        


def getTunefromScope(rootname,pi=0.41,pf=0.44,BaseLineRemove=True,integData=True,returnPOS=False):
        F0,F0Wfm = rootname+'.bin',rootname+'.Wfm.bin'
        N,COV,dt,nt,dV_COUNT,CH1_POS,CH2_POS,CH3_POS,CH4_POS,CH1_dVpD,CH2_dVpD,CH3_dVpD,CH4_dVpD,CH1_OFF,CH2_OFF,CH3_OFF,CH4_OFF = readHEADER(F0)
        CH1VT,CH2VT,CH1RB,CHINTG,TIME = scopeData(F0Wfm,F0,BaseLineRemove=True,integData=True)
        point = int(nt/2) # center point of the data
        P1,P2,P3 = getPosition(CH1VT,point,N),getPosition(CH1RB,point,N),getPosition(CHINTG,point,N)
        freq1 = np.arange(0,N)/(N)
        freq1 = freq1[:int(N/2+1)]
        x1,y1 = getTuneSpec(P1,dn=1)[0][((freq1 > pi) & (freq1 < pf))],getTuneSpec(P1,dn=1)[1][((freq1 > pi) & (freq1 < pf))]
        x2,y2 = getTuneSpec(P2,dn=1)[0][((freq1 > pi) & (freq1 < pf))],getTuneSpec(P2,dn=1)[1][((freq1 > pi) & (freq1 < pf))]
        x3,y3 = getTuneSpec(P3,dn=1)[0][((freq1 > pi) & (freq1 < pf))],getTuneSpec(P3,dn=1)[1][((freq1 > pi) & (freq1 < pf))]
        print ('expected tune: ', x1[np.argmax(y1)],x1[np.argmax(y2)],x1[np.argmax(y3)])
        if returnPOS:
            return (P1,P2,P3,x1,y1,y2,y3)
        else:
            return (x1,y1,y2,y3)
