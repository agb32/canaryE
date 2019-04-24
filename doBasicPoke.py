import sys
import numpy
import darc
import FITS
import time
"""Basic poke method - probably not what you want for a real AO system.

For a real system, you would want to both push and pull the actuators at the very least.

You may also want to poke patterns of actuators rather than individually (Hadamard, sinusoids, etc).

Also, the way this is implemented isn't the most efficient.  For a real system, you probably want to set actuators to a 2D array, with dimensions X,nacts.
Darc will then play through this sequence, repeating when it gets to the end.  You can then record a sequence of slopes:
data=GetStreamBlock(["rtcCentBuf","rtcActuatorBuf"],X,asArray=1)
slopes=data["rtcCentBuf"][0]
acts=data["rtcActuatorBuf"][0]  #note, we recorded acts, so that you know where about in the sequence you are...

"""
nfr=1
if len(sys.argv)>1:
    nfr=int(sys.argv[1])
pokeval=10.
if len(sys.argv)>2:
    pokeval=float(sys.argv[2])
print "Have you set into calibration mode and taken reference slopes?"
d=darc.Control("main")
rmx=d.Get("rmx")
nacts,nslopes=rmx.shape
pmx=numpy.zeros(rmx.shape,numpy.float32)
d.Set("addActuators",0)
actuators=numpy.ones((nacts,),numpy.float32)*32768
for i in range(nacts):
    print "Poking %d"%i
    actuators[i]=pokeval
    if i<2:
        actuators[i]+=32768
    d.Set("actuators",actuators)
    time.sleep(1.5)
    sl=d.SumData("rtcCentBuf",nfr)[0]/nfr/pokeval
    pmx[i]=sl
    actuators[i]=0
    if i<2:
        actuators[i]=32768

d.Set("actuators",actuators)
FITS.Write(pmx,"pmx.fits")
rmx=-numpy.linalg.pinv(pmx,0.1).T
FITS.Write(rmx,"rmx.fits")
d.Set("rmx",rmx)
print "Saved pmx.fits, rmx.fits and set rmx into darc"
