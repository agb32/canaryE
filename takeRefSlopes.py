import sys
import numpy
import darc
import FITS
nfr=10
if len(sys.argv)>1:
    nfr=int(sys.argv[1])
print "Have you set into calibration mode?"
d=darc.Control("main")
d.Set("refCentroids",None)
refslopes=d.SumData("rtcCentBuf",nfr)[0]/nfr
d.Set("refCentroids",refslopes)
FITS.Write(refslopes,"refslopes.fits")
print "Saved refslopes.fits and set in darc"
