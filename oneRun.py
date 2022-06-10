import numpy as np

from scopeFull import *

import time 
import sys

print (len(sys.argv))

if len(sys.argv)>1:
   m = sys.argv[1]
else:
   m = 0


FILENAME = 'tuneVsGain'
FRAMES = 20000
#m = 0
myScope = Control(FILENAME,FRAMES,LOG=1)


myScope.preP(dtype='INT,8') # if the resolution is high, this will be ignored 

myScope.setVscale(1,10e-3,0,0)
myScope.setVscale(2,100e-3,0,0)
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


