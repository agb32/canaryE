import sys
import numpy
import darc
import FITS
rcond=float(sys.argv[1])
pmx=FITS.Read("pmx.fits")[1]#This contains high order DM and TT.
rmx=-numpy.linalg.pinv(pmx,rcond).T#separating out the TT from rest would be better - but I'm too lazy...
FITS.Write(rmx,"rmx%g.fits"%rcond)
d=darc.Control("main")
d.Set("rmx",rmx)
print "Saved rmx%g.fits and set in darc"%rcond
