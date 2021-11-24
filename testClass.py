import numpy as np

from PyScope import *


import time 

myScope = Control('mySetup',750,LOG=1)


"""

myScope.preP()

myScope.setVscale(1,40e-3,0,0)
myScope.setVscale(2,300e-3,0,0)
myScope.setHscale(100e-9,0,0)

for i in range(3):
    myScope.waitForCommand()
    myScope.acqSetting()
    myScope.runSingle()
    myScope.exportSetting(i)
    myScope.playHistory(750-(50*i))
    myScope.waitForCommand()
    #myScope.copyFile(i)
    #myScope.waitForCommand()


[myScope.copyFile(i) for i in range(3)]

myScope.close()
"""

