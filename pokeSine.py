#copyright Durham University, Alastair Basden, GPL v3.
#see darc/lib/python/calibrate.py
import sys
import time
import numpy
import FITS
import calibrate



# def loadSineData(fname,stdThresh=0.25):
#     """
#     fname is the name of a file that has been created by e.g. doSinePokeGTC()
#     stdThresh is the threshold above which slopes are ignored if their std is higher than the max std * thresh.  This allows us to automatically cut out slopes the don't have light."""
#     sList=[]
#     vList=[]
#     data=FITS.Read(fname)
#     for i in range(len(data)//12):
#         s=data[1+i*12]#the slopes
#         vmes=data[7+i*12]#the actuators (sinusoidal)
#         if stdThresh>0:
#             #define a mask of valid subaps based on those with low rms.
#             sstd=s.std(0)#get standard deviation of each subap
#             maxstd=sstd.max()#find the max...
#             valid=numpy.where(sstd<maxstd*stdThresh,1,0)
#             s*=valid
#         sList.append(s)
#         vList.append(vmes)
#     return vList,sList

# def rollSineData(vList,sList):
#     """Roll the data so that the phase becomes zero
#     vList is the list of actuator arrays (i.e. as output from loadSineData).
#     sList is the list of slope arrays."""
#     v2=[]
#     s2=[]
#     for i in range(len(vList)):
#         v=vList[i]
#         s=sList[i]
#         vgrad=(v[1:]-v[:-1]).sum(1)
#         maxpos=vgrad.argmax()
#         v=numpy.roll(v,-maxpos-1,0)
#         s=numpy.roll(s,-maxpos-3,0)
#         s2.append(s-s.mean(0))
#         v2.append(v-v.mean(0))
#     return v2,s2

# def makeSinePmx(vList,sList,pokeVal):
#     """compute an interaction matrix.  pokeVal is the amplitude of the sine waves used for poking.  Returns a list of matrics, one for each sine-sequence."""
#     pmxList=[]
#     for i in range(len(vList)):
#         pmx=numpy.dot(sList[i].T.astype("d"),vList[i].astype("d")).T/float(vList[i].shape[0])*2/(pokeVal**2)
#         pmxList.append(pmx)
#     return pmxList

# def makeSineRmx(pmxList,rcond,thresh=0.25):
#     """rcond is the conditioning value.
#     thresh is a threshold as a fraction of the std, below which the pmx is set to zero.
#     """
#     rmxList=[]
#     for pmx in pmxList:
#         if thresh!=0:
#             pmx=numpy.where(numpy.abs(pmx)<pmx.std()*thresh,0,pmx)
#         rmxList.append(-numpy.linalg.pinv(pmx,rcond).T.copy())
#     return rmxList

# def computeSineDelay(vList,sList,vindx,sindx=None):
#     """Computes frame delay between vList and sList.  """
#     vt=vList[0][:,vindx]
#     fv=numpy.fft.fft(vt)[:2000]
#     vpeak=numpy.absolute(fv).argmax()
#     if sindx is None:
#         fs=numpy.fft.fft(sList[0],axis=0)
#         sindx=numpy.argmax(numpy.absolute(fs[vpeak]))
#         print "Got slope index at %d"%sindx
#         fs=fs[:,sindx]
#     else:
#         st=sList[0][:,sindx]
#         fs=numpy.fft.fft(st)[:2000]
#     speak=numpy.absolute(fs).argmax()
#     if(vpeak!=speak):
#         print "WARNING: FFT peaks not at same position %d %d"%(vpeak,speak)
#         return None
#     vphase=numpy.arctan2(fv.imag[vpeak],fv.real[vpeak])
#     sphase=numpy.arctan2(fs.imag[speak],fs.real[speak])
#     phaseDiff=vphase-sphase
#     print "%f radians, %f cycles"%(phaseDiff,phaseDiff/2./numpy.pi)
#     nsamp=vList[0].shape[0]
#     ncycles=vpeak
#     framesPerCycle=nsamp/ncycles
#     framesDelay=framesPerCycle*phaseDiff/2./numpy.pi
#     print "Delay: %f frames"%framesDelay
#     return framesDelay#if +ve, need to roll slopes -ve or acts +ve.

# def computeSineDelays(vList,sList):
#     """Compute mean frame delay between slopes and actuators."""
#     delayList=[]
#     for indx in range(vList[0].shape[1]):
#         delay=computeSineDelay(vList,sList,indx)
#         if delay!=None:
#             delayList.append(delay)
#     delays=numpy.array(delayList)
#     indx=numpy.where(numpy.abs(delays-numpy.median(delays))<0.5)
#     meandelay=delays[indx].mean()
#     stddelay=delays[indx].std(ddof=1)
#     print "Mean delay (ignoring outliers) %g +- %g frames"%(meandelay,stddelay)
#     return delays,meandelay,stddelay#if +ve, need to roll slopes -ve or acts +ve.

# def shiftSineActuators(vList,delay):
#     """shift actuators by non-integer delay - given by the return from computeSineDelays()"""
#     delay1=int(numpy.floor(delay))
#     delay2=int(numpy.ceil(delay))
#     frac=delay%1

#     outList=[]
#     for s in vList:
#         s1=numpy.roll(s,delay1,0)
#         s2=numpy.roll(s,delay2,0)
#         snew=s1*(1-frac)+s2*(frac)
#         outList.append(snew)
#     return outList

# def shiftSineSlopes(sList,delay):
#     """shift slopes by non-integer delay as given by computeSineDelays().  Either use this or shiftSineActuators, but not both...  and looking at created interaction matres, there appears to be very little difference between which one to choose."""
#     return shiftSineActuators(sList,-delay)


# def processSine(fname,rcond=0.1,stdThresh=0.25,pokeVal=1000,pmxThresh=0.5):
#     """Uses the file created by doSinePoke() to compute the rmx.
#     fname - the file containing the slopes and actuator values.
#     rcond - conditioning value for pseudo-inverse of interaction matrix.
#     stdThresh - used to define which are active sub-apertures (the larger this value, the more sub-apertures will be used).
#     pokeVal - the amplitude used during poking.
#     pmxThresh - a threshold used for cleaning the interaction matrix (larger values will result in more of the pmx being set to zero)."""
#     vList,sList=loadSineData(fname,stdThresh)
#     vList,sList=rollSineData(vList,sList)
#     delays,meandelay,stddelay=computeSineDelays(vList,sList)
#     vList=shiftSineActuators(vList,meandelay)
#     pmxList=makeSinePmx(vList,sList,pokeVal)
#     rmxList=makeSineRmx(pmxList,rcond,pmxThresh)
#     rmx=numpy.array(rmxList).mean(0)
#     return rmx,pmxList,rmxList

def doSinePokeGTC(pokeVal=1000.):
    """Set the poking going and save data"""
    fname="pokeSineBench%s.fits"%time.strftime("%y%m%d_%H%M%S")
    dm=calibrate.DMInteraction([2,241],"")
    repeatIfErr=10
    if pokeVal==1:#simulation
        repeatIfErr=0
    dm.pokeSine(2000,pokeVal=pokeVal,nrec=2,dmNo=1,fname=fname,fno=-300,nRepeats=2,repeatIfErr=repeatIfErr)
    return fname,dm

if __name__=="__main__":
    rcond=0.1
    thresh=0.25
    if len(sys.argv)>1:
        rcond=float(sys.argv[1])
    if len(sys.argv)>2:#1 for simulation, 1000 for bench.
        amp=float(sys.argv[2])
    if len(sys.argv)>3:#0 for simulation, 0.25 for bench
        thresh=float(sys.argv[3])
    fname,dm=doSinePokeGTC(pokeVal=amp)
    #dm=calibrate.DMInteraction([373,2],"")
#    fname="pokeSineBench180705_121816.fits"
#    fname="pokeSineBench180705_160328.fits"
    rmx,pmxList,rmxList=dm.processSine(fname,rcond=rcond,stdThresh=thresh)
    rname="rmx_%f_%s"%(rcond,fname)
    FITS.Write(rmx,rname)
    print "Written %s"%rname


