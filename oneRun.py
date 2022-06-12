import numpy as np

from PyScope import *

import time 
import sys


import argparse



parser = argparse.ArgumentParser(description='set the options for a single run on the scope') 


parser.add_argument('rootname', type=str,
                            help='root file name')

parser.add_argument('frames', type=int,nargs='?',default=2000,
                            help='number of frames')

parser.add_argument('run', type=int,nargs='?',default=0,
                            help='run number')
parser.add_argument('CH1_dV', type=float,nargs='?',default=10e-3,
                            help='Voltag per Division for CH1')

parser.add_argument('CH2_dV', type=float,nargs='?',default=100e-3,
                            help='Voltag per Division for CH2')

parser.add_argument('dt', type=float,nargs='?',default=10e-9,
                            help='Time per divison (H-SCALE)')

parser.add_argument('RES', type=float,nargs='?',default=10e-9,
                            help='Resolution H-SCALE')



args = parser.parse_args()

rootname =args.rootname
FRAMES = args.frames
m = args.run
CH1_dV  =args.CH1_dV
CH2_dV  =args.CH2_dV
dt = args.dt
RES = args.RES

print (rootname,FRAMES,m,CH1_dV,CH2_dV)


myScope = Control(rootname,FRAMES,LOG=1)


myScope.preP(dtype='INT,8') # if the resolution is high, this will be ignored 

myScope.setVscale(1,CH1_dV,0,0)
myScope.setVscale(2,Ch2_dV,0,0)
myScope.setHscale(10e-9,0,0)


#myScope.acqSetting(RES=50e-12)

COMM = 'SYSTem:DISPlay:UPDate ON' #keep the display on
myScope.instr.write(COMM)

myScope.runSingle()
myScope.exportSetting(m)
myScope.playHistory(FRAMES)
myScope.waitForCommand()
myScope.copyFile(m)
myScope.waitForCommand()
myScope.close()


