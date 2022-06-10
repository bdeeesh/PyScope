import numpy as np

from PyScope import *

import time 


FILENAME = '11292021_Calibration_52MHz'
FRAMES = 2000

myScope = Control(FILENAME,FRAMES,LOG=1)

myScope.copyFileName('D02KC')

myScope.close()


