
import base.readConfig
this=base.readConfig.init(globals())
tstep=1/250.#Simulation timestep in seconds (250Hz).
AOExpTime=0.#40 seconds exposure (use --iterations=xxx to modify)
npup=112#Number of phase points across the pupil
telDiam=4.2 #telescope diameter
telSec=4.2/3.5#Central obscuration
ntel=npup#Telescope diameter in pixels
ngsLam=640.#NGS wavelength
lgsLam=589.#LGS wavelength
sciLam=1650.#Science wavelength
ngsAsterismRadius=90.#arcseconds
nsci=1
nngs=4
ndm=1
import util.tel
#Create a pupil function
pupil=util.tel.Pupil(npup,ntel/2,ntel/2*telSec/telDiam)

#Create the WFS overview
import util.guideStar
#import util.elong
#Create the LGS PSFs (elongated).  There are many ways to do this - this is a simple one.
#lgssig=1e6
#psf=util.elong.make(spotsize=phasesize*4,nsubx=wfs_nsubx,wfs_n=phasesize,lam=lgsLam,telDiam=telDiam,telSec=telSec,beacon_alt=lgsalt,beacon_depth=10000.,launchDist=0.,launchTheta=0.,pup=pupil,photons=lgssig)[0]

sourceList=[]
wfsDict={}
for i in range(nngs-1):#7x7 off-axis NGS
    id="%d"%(i+1)
    wfsDict[id]=util.guideStar.NGS(id,7,ngsAsterismRadius,i*360./(nngs-1),phasesize=16,minarea=0.5,sig=1e6,sourcelam=ngsLam,reconList=["recon"],pupil=pupil)
    sourceList.append(wfsDict[id])
#and now the truth (14x14)
i=nngs-1
id="%d"%(i+1)
wfsDict[id]=util.guideStar.NGS(id,14,0.,0.,phasesize=8,minarea=0.5,sig=1e6,sourcelam=ngsLam,reconList=["recon"],pupil=pupil)
sourceList.append(wfsDict[id])

#wfsDict["img"]=util.guideStar.NGS("img",0.,0.,-1,7,700,reconList=["darc"])#dummy
#sourceList.append(wfsDict["img"])

wfsOverview=util.guideStar.wfsOverview(wfsDict)

#Create a Science overview.
import util.sci
sciDict={}
for i in range(nsci):
    id="sci%d"%(i+1)
    sciDict[id]=util.sci.sciInfo(id,i*10.,0.,pupil,sciLam,phslam=sciLam,calcRMS=1)
    sourceList.append(sciDict[id])
    id="sci%duncorr"%(i+1)
    sciDict[id]=util.sci.sciInfo(id,i*10.,0.,pupil,sciLam,phslam=sciLam,calcRMS=1)
    sourceList.append(sciDict[id])

sciOverview=util.sci.sciOverview(sciDict)
#Create the atmosphere object and source directions.
from util.atmos import geom,layer,source
atmosDict={}
nlayer=10 #10 atmospheric layer
layerList={"allLayers":["L%d"%x for x in range(nlayer)]}
strList=[0.5]+[0.5/(nlayer-1.)]*(nlayer-1)#relative strength of the layers
hList=range(0,nlayer*1000,1000)#height of the layers
vList=[10.]*nlayer#velocity of the layers
dirList=range(0,nlayer*10,10)#direction (degrees) of the layers
for i in range(nlayer):
 atmosDict["L%d"%i]=layer(hList[i],dirList[i],vList[i],strList[i],10+i)

l0=10. #outer scale
r0=0.137 #fried's parameter
atmosGeom=geom(atmosDict,sourceList,ntel,npup,telDiam,r0,l0)

print atmosGeom.getWFSOrder("darc")
#Create the DM object.
from util.dm import dmOverview,dmInfo
import numpy
dmHeight=0
dmInfoList=[]
dmInfoList.append(dmInfo('dm0path',[x.idstr for x in sourceList],dmHeight,15,minarea=0.5,closedLoop=0,reconLam=ngsLam,actuatorsFrom="darc",maxActDist=0.6,interpType="pspline"))
dmInfoList.append(dmInfo('ttpath',[x.idstr for x in sourceList],dmHeight,3,minarea=0.1,actuatorsFrom="darc",closedLoop=1,zonalDM=0,reconLam=ngsLam))

dmOverview=dmOverview(dmInfoList,atmosGeom)

# #reconstructor
# this.tomoRecon=new()
# r=this.tomoRecon
# r.rcond=0.05#condtioning value for SVD
# r.recontype="pinv"#reconstruction type
# r.pokeval=1.#strength of poke
# r.gainFactor=0.5#Loop gain
# r.computeControl=1#To compute the control matrix after poking
# r.reconmxFilename="rmx.fits"#control matrix name (will be created)
# r.pmxFilename="pmx.fits"#interation matrix name (will be created)

imageOnly=2

this.predarc=new()
r=this.predarc
r.readnoise=[0.1]*4
r.background=[0.]*4
r.fliprotateWFS=[7,9,4,3]
npxlxDarc=[128,128,128,128]

this.darcsim=new()
r=this.darcsim
r.useExistingDarc=1
r.npxlx=128**2*4
r.npxly=1
r.npxlsDarc=128**2*4
r.nactsDarc=245 #241 for alpao, 4 for tt.


