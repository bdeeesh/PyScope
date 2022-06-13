set of functions to control scope RTP

python3 oneRun.py -h

set the options for a single run on the scope


positional arguments:


  rootname    root file name

  frames      number of frames

  run         run number

  CH1_dV      Voltag per Division for CH1

  CH2_dV      Voltag per Division for CH2

  dt          Time per divison (H-SCALE)

  RES         Resolution H-SCALE

Example:

python3 oneRun.py rootname 20000 0 1e-3 100e-3 10e-9 50e-12

#copying files

Example: Change the file name inside copyOneFile.py

python3 copyOneFile.py

 
PyScopeAna.py contains functions to read and analyze data from the scope: 

Example

PyScopeAna.getTunefromScope(rootname,pi=0.41,pf=0.44,BaseLineRemove=True,integData=True,returnPOS=False)

will look for the tune in the rootname file (Wfm data) with bin data between 0.41 and 0.44. The arguemtns will remove the BaseLine by averaging the data and/or return the integrated signal by using np.cumsum. 

The output will be 4 arrays each with shape (N) (Number of frames x number of points):
freq


tune from CH1 without anything

tune from CH1 with BaseLineRemoved

tune from CH1 after integrating the data


