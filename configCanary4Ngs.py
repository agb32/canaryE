#darc, the Durham Adaptive optics Real-time Controller.
#Copyright (C) 2010 Alastair Basden.

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as
#published by the Free Software Foundation, either version 3 of the
#License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Affero General Public License for more details.

#You should have received a copy of the GNU Affero General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
#This is a configuration file for CANARY.
#Aim to fill up the control dictionary with values to be used in the RTCS.

#Using ocam camera as lgs wfs (242,264).  From aosim/canary/rtsim/phaseC2/configCanaryJune2015Sim.py
#Using the Andor Dongle.  So no interleaved pixels.

import FITS
import tel
import numpy
import string
import os
import time
NNGSCAM=4#1, 2, 3, 4.  This is the number of physical cameras
NLGSOCAM=0
NBOBCAT=0
NSLCAMERAS=NNGSCAM
nacts=2+241#97#54#+256
ncamSL=NNGSCAM#(int(NNGSCAM)+1)//2
ncam=ncamSL+NBOBCAT+NLGSOCAM
#camPerGrab=numpy.ones((ncam,),"i")
#camPerGrab[:NNGSCAM//2]=2
ncamThreads=numpy.ones((ncam,),numpy.int32)*1
npxly=numpy.zeros((ncam,),numpy.int32)
npxly[:]=128
npxly[ncamSL:ncamSL+NLGSOCAM]=242
npxly[ncamSL+NLGSOCAM:ncamSL+NBOBCAT+NLGSOCAM]=140
npxlx=npxly.copy()#*camPerGrab
npxlx[ncamSL:ncamSL+NLGSOCAM]=264
nsuby=npxlx.copy()
nsuby[:]=7#for config purposes only... not sent to rtc
if ncamSL!=0:
    nsuby[ncamSL-1]=14#truth
nsuby[ncamSL:ncamSL+NLGSOCAM]=7#The LGS 
nsuby[ncamSL+NLGSOCAM:ncamSL+NLGSOCAM+NBOBCAT]=[7,14][:NBOBCAT]
nsubx=nsuby.copy()#*camPerGrab#for config purposes - not sent to rtc
#nsubx[1]=35#ngs3 + truth (14x14)
#nsubx[ncamSL:ncamSL+NLGSOCAM]=14*4#The LGS (4 WFS on 1 detector - in a row.)
nsub=nsubx*nsuby#This is used by rtc.
nsubaps=nsub.sum()#(nsuby*nsubx).sum()
individualSubapFlag=tel.Pupil(7,3.5,1,7).subflag.astype("i")
sf14=tel.Pupil(14,7.,2,14).subflag.astype("i")
sfNoObs=tel.Pupil(7,3.5,0,7).subflag.astype("i")
sf14NoObs=tel.Pupil(14,7.,0,14).subflag.astype("i")
#lgsSubapFlag=numpy.zeros((14,56),"i")

#For the ocam, I think we can simply interleave the top and bottom subap by subap.
#To be sure of ordering, have pxlCnt set to the end of the row, rather than subap.

nsublist=[]
print "nsub:",nsub
#for i in range(4):
#    lgsSubapFlag[:,i::4]=sf14
subapFlag=numpy.zeros((nsubaps,),"i")

for i in range(NNGSCAM+NLGSOCAM+NBOBCAT):#ngs 1-3, truth, lgs, lofs, hofs
    tmp=subapFlag[nsub[:i].sum():nsub[:i+1].sum()]
    tmp.shape=nsuby[i],nsubx[i]
    if i==NNGSCAM+NLGSOCAM:#lofs
        tmp[:]=sfNoObs
    elif i==1+NNGSCAM+NLGSOCAM:#hofs
        tmp[:]=sf14NoObs
    elif i==NNGSCAM:#lgs
        for j in range(4):
            jj=6-j
            tmp[j*2]=individualSubapFlag[jj]
            if j!=3:
                tmp[j*2+1]=individualSubapFlag[j]
            #jj=7-j
            #if jj<7:
            #    tmp[j*2-1]=individualSubapFlag[jj]
            #tmp[j*2]=individualSubapFlag[j]
    else:
        if tmp.shape[0]==7:
            tmp[:]=individualSubapFlag
        else:
            tmp[:]=sf14
    nsublist.append(tmp.sum())

print "Nsublist:",nsublist
print "ncents:",[x*2 for x in nsublist],subapFlag.sum()
#ncents=nsubaps*2
ncents=subapFlag.sum()*2
npxls=(npxly*npxlx).sum()
ttt=subapFlag.copy()

print "ncents: %d"%ncents,nsubx,nsuby

def makeSubapMap():
    """For test purposes - makes a vector of slopes, with the numbers corresponding to which wfs it is for.  1==nsg1, 4==truth, etc"""
    a=numpy.zeros((sum(nsub),),numpy.int32)
    subFlag=subapFlag.copy()
    for i in range(NNGSCAM+NLGSOCAM+NBOBCAT):#ngs 1-3, truth, lgs, lofs, hofs
        tmp=subFlag[nsub[:i].sum():nsub[:i+1].sum()]
        tmp.shape=nsuby[i],nsubx[i]
        if i==NNGSCAM+NLGSOCAM:#lofs
            tmp[:]=sfNoObs*(i+1)
        elif i==1+NNGSCAM+NLGSOCAM:#hofs
            tmp[:]=sf14NoObs*(i+1)
        elif i==NNGSCAM:#lgs
            for j in range(4):
                jj=6-j
                tmp[j*2]=individualSubapFlag[jj]*(i+1)
                if j!=3:
                    tmp[j*2+1]=individualSubapFlag[j]*(i+1)
                #jj=7-j
                #if jj<7:
                #    tmp[j*2-1]=individualSubapFlag[jj]*(i+1)
                #tmp[j*2]=individualSubapFlag[j]*(i+1)
        else:
            tmp[:]=individualSubapFlag*(i+1)
    return subFlag

def makeSlopeMap():
    """For test purposes - makes a vector of slopes, with the numbers corresponding to which wfs it is for.  1==nsg1, 4==truth, etc"""
    a=numpy.zeros((ncents/2,2),numpy.int32)
    subFlag=makeSubapMap()#subapFlag.copy()
    # for i in range(7):#ngs 1-3, truth, lgs, lofs, hofs
    #     tmp=subFlag[nsub[:i].sum():nsub[:i+1].sum()]
    #     tmp.shape=nsuby[i],nsubx[i]
    #     if i==5:#lofs
    #         tmp[:]=sfNoObs*(i+1)
    #     elif i==6:#hofs
    #         tmp[:]=sf14NoObs*(i+1)
    #     else:
    #         tmp[:]=individualSubapFlag*(i+1)
    pos=0
    for i in range(subFlag.size):
        if subFlag[i]!=0:
            a[pos]=subFlag[i]
            pos+=1
    return a




fakeCCDImage=None
bgImage=None
darkNoise=None
flatField=None

subapLocation=numpy.zeros((nsubaps,6),"i")
nsubapsCum=numpy.zeros((ncam+1,),numpy.int32)
ncentsCum=numpy.zeros((ncam+1,),numpy.int32)
for i in range(ncam):
    nsubapsCum[i+1]=nsubapsCum[i]+nsub[i]
    ncentsCum[i+1]=ncentsCum[i]+subapFlag[nsubapsCum[i]:nsubapsCum[i+1]].sum()*2

# now set up a default subap location array...
#this defines the location of the subapertures.
xoff=numpy.array([8]*(ncamSL)+[16]*NLGSOCAM+[7,0][:NBOBCAT])
yoff=numpy.array([8]*(ncamSL)+[30]*NLGSOCAM+[7,0][:NBOBCAT])
#subx=(npxlx-16*camPerGrab)/nsubx
#suby=(npxly-16)/nsuby
subx=(npxlx-xoff*2)/nsubx
suby=(npxly-yoff*2)/nsuby
subx[ncamSL:ncamSL+NLGSOCAM]=30
suby[ncamSL:ncamSL+NLGSOCAM]=30
print subx,suby
lastUsedSubap=numpy.zeros((ncam,),numpy.int32)

# Static offsets of subapertures on a per WFS basis
# +Y moves subaperture locations up
# +X moves subaperture locations right
# Y,X pixels on Darcplot (check)
subapOffsets = [(2,6),   # WFS 1 was (1,5) in C2
                (1,1), # WFS 2 was (-1,-1) in C2
                (-2,1),  # WFS 3 ws (-2,0) in C2
                (0,0),   # Not implemented
                (0,0),   # Not implemented
                (0,0),   # Not implemented
                (0,0),   # Not implemented
                (0,0),   # Not implemented
                (0,0),   # Not implemented
                (0,0)]   # Not implemented

#Do ngs1-3, truth, lofs, hofs
for k in range(ncamSL)+[NNGSCAM+NLGSOCAM,NNGSCAM+NLGSOCAM+1][:NBOBCAT]:
    for i in range(nsuby[k]):
        for j in range(nsubx[k]):
            indx=nsubapsCum[k]+i*nsubx[k]+j
            if subapFlag[indx]:
                offs=subapOffsets[k]
                lastUsedSubap[k]=i*nsubx[k]+j
                subapLocation[indx]=(yoff[k]+i*suby[k]+offs[0],
                                     yoff[k]+(i+1)*suby[k]+offs[0],1,
                                     xoff[k]+j*subx[k]+offs[1],
                                     xoff[k]+(j+1)*subx[k]+offs[1],1)

#Do the LGS (different because of 4 readout ports mean we order subaps slightly differently).
#CCD has 8 readout ports.  Sub-apertures should try to avoid spanning ports - certainly avoid the top and bottom lines.  Therefore, will have 4x7 subaps above, and 3x7 below.
adapWinShiftCnt=numpy.ones((nsubaps,2),"i")
adapWinShiftCnt[:,1]=0#no need to change rows as we're reading whole rows at a time.
if NLGSOCAM!=0:
    k=ncamSL
    offs=subapOffsets[k]
    for i in range(4):
        ii=6-i
        #Top half (4 rows)
        indx=nsubapsCum[k]+(2*i)*nsubx[k]
        for j in range(nsubx[k]):
            if subapFlag[indx+j]:
                lastUsedSubap[k]=indx+j-nsubapsCum[k]
                subapLocation[indx+j]=(yoff[k]+ii*suby[k]+offs[0],
                                     yoff[k]+(ii+1)*suby[k]+offs[0],1,
                                     xoff[k]+j*subx[k]+offs[1],
                                    xoff[k]+(j+1)*subx[k]+offs[1],1)
                adapWinShiftCnt[indx+j,0]=-1
        #Bottom half (3 rows)
        if i!=3:
            indx=nsubapsCum[k]+(2*i+1)*nsubx[k]
            for j in range(nsubx[k]):
                if subapFlag[indx+j]:
                    lastUsedSubap[k]=indx+j-nsubapsCum[k]
                    subapLocation[indx+j]=(yoff[k]+i*suby[k]+offs[0],
                                         yoff[k]+(i+1)*suby[k]+offs[0],1,
                                         xoff[k]+j*subx[k]+offs[1],
                                         xoff[k]+(j+1)*subx[k]+offs[1],1)

"""        if ii<7:#Top half (3 rows)
            indx=nsubapsCum[k]+(2*i-1)*nsubx[k]
            for j in range(nsubx[k]):
                if subapFlag[indx+j]:
                    lastUsedSubap[k]=indx+j-nsubapsCum[k]
                    subapLocation[indx+j]=(yoff[k]+ii*suby[k]+offs[0],
                                         yoff[k]+(ii+1)*suby[k]+offs[0],1,
                                         xoff[k]+j*subx[k]+offs[1],
                                        xoff[k]+(j+1)*subx[k]+offs[1],1)
                    adapWinShiftCnt[indx+j,0]=-1
        #Bottom half (4 rows)
        indx=nsubapsCum[k]+2*i*nsubx[k]
        for j in range(nsubx[k]):
            if subapFlag[indx+j]:
                lastUsedSubap[k]=indx+j-nsubapsCum[k]
                subapLocation[indx+j]=(yoff[k]+i*suby[k]+offs[0],
                                     yoff[k]+(i+1)*suby[k]+offs[0],1,
                                     xoff[k]+j*subx[k]+offs[1],
                                     xoff[k]+(j+1)*subx[k]+offs[1],1)
"""


pxlCnt=numpy.zeros((nsubaps,),"i")
# set up the pxlCnt array - number of pixels to wait until each subap is ready.
#ngs1-3,truth,lofs,hofs
for k in range(ncamSL)+[NNGSCAM+NLGSOCAM,NNGSCAM+NLGSOCAM+1][:NBOBCAT]:
    for i in range(nsub[k]):
        indx=nsubapsCum[k]+i
        n=(subapLocation[indx,1]-1)*npxlx[k]+subapLocation[indx,4]
        pxlCnt[indx]=n
    pxlCnt[nsubapsCum[k]+lastUsedSubap[k]]=npxlx[k]*npxly[k]

#for the LGS - whole rows - in pairs (with top ones upside down)
if NLGSOCAM!=0:
    maxn=0
    maxindx=0
    for k in range(ncamSL,ncamSL+NLGSOCAM):
        for i in range(nsub[k]):
            indx=nsubapsCum[k]+i
            if subapFlag[indx]:
                if subapLocation[indx,1]<=120:#bottom half
                    n=(subapLocation[indx,1]+1)*npxlx[k]*2#The +1 comes from the reorder.  The pixels are reordered into the first 240x240 area.  But actually, there is a blank row read out before this!
                    if n>maxn:
                        maxn=n
                        maxindx=indx
                else:#top half (it reads out towards the middle)
                    n=(241-subapLocation[indx,0])*npxlx[k]*2
                    if n>maxn:
                        maxn=n
                        maxindx=indx
                pxlCnt[indx]=n
        pxlCnt[maxindx]=npxlx[k]*npxly[k]


#The params are dependent on the interface library used.

camList=["Pleora Technologies Inc.-"]*NLGSOCAM+["Imperx, inc.-110525","Imperx, inc.-110526","Imperx, inc.-110528"][:NBOBCAT]
camNames=string.join(camList,";")#"Imperx, inc.-110323;Imperx, inc.-110324"
print camNames
while len(camNames)%4!=0:
    camNames+="\0"
namelen=len(camNames)

# The bobcat window offsets
bobOffset_X = [254, 254]
bobOffset_Y = [174+10, 174+10]

#The params are dependent on the interface library used.
cameraParams=numpy.zeros((7*ncamSL+10*(NLGSOCAM+NBOBCAT)+7+(namelen+3)//4,),numpy.int32)
cameraParams[0]=1#affin el size
cameraParams[1]=ncamSL
cameraParams[2:2+7*ncamSL:7]=[1024]*ncamSL#128*8#blocksize in pixels
cameraParams[3:2+7*ncamSL:7]=1000#timeout/ms
cameraParams[4:2+7*ncamSL:7]=[2,1,0,3]#range(ncamSL)#port
cameraParams[5:2+7*ncamSL:7]=19#thread priority
cameraParams[6:2+7*ncamSL:7]=0#reorder
#cameraParams[6+7*(ncamSL-NLGSCAM):2+7*ncamSL:7]=1#reorder the LGS
cameraParams[7:2+7*(ncamSL):7]=0#testLastPixel for ngs  - 0 for dongle, 2 for pre-dongle
#cameraParams[7+7*(ncamSL-NLGSCAM):2+7*ncamSL:7]=0#testLastPixel for lgs
cameraParams[8:2+7*ncamSL:7]=-1#thread affinity
cameraParams[2+7*ncamSL:2+7*ncamSL+10*NLGSOCAM:10]=16#bpp for lgs - though aravis should be told it is 8 bpp.
cameraParams[2+7*ncamSL+10*NLGSOCAM:2+7*ncamSL+10*NLGSOCAM+10*NBOBCAT:10]=8#bpp for fs
cameraParams[3+7*ncamSL:2+7*ncamSL+10*(NLGSOCAM+NBOBCAT):10]=npxlx[ncamSL:ncamSL+NLGSOCAM+NBOBCAT]*8*numpy.array([8]*NLGSOCAM+[1,1][:NBOBCAT])#blocksize in bytes
cameraParams[4+7*ncamSL:2+7*ncamSL+10*(NLGSOCAM+NBOBCAT):10]=[0]*NLGSOCAM+bobOffset_X[:NBOBCAT]#,(648-npxlx[ncamSL+NLGSOCAM])//2,(648-npxlx[ncamSL+NLGSOCAM+1])//2)#0,254#offsetx
cameraParams[5+7*ncamSL:2+7*ncamSL+10*(NLGSOCAM+NBOBCAT):10]=[0]*NLGSOCAM+bobOffset_Y[:NBOBCAT]#(488-npxly[ncamSL+NLGSOCAM])//2,(488-npxly[ncamSL+NLGSOCAM+1])//2)#174#offsety
cameraParams[6+7*ncamSL:2+7*ncamSL+10*(NLGSOCAM+NBOBCAT):10]=[1056]*NLGSOCAM+list(npxlx[ncamSL+NLGSOCAM:ncamSL+NLGSOCAM+NBOBCAT])#camnpxlx
cameraParams[7+7*ncamSL:2+7*ncamSL+10*(NLGSOCAM+NBOBCAT):10]=[121]*NLGSOCAM+list(npxly[ncamSL+NLGSOCAM:ncamSL+NLGSOCAM+NBOBCAT])#camnpxly
cameraParams[8+7*ncamSL:2+7*ncamSL+10*(NLGSOCAM+NBOBCAT):10]=[1]*NLGSOCAM+[0]*NBOBCAT#byteswapInt (1 for ocam)
cameraParams[9+7*ncamSL:2+7*ncamSL+10*(NLGSOCAM+NBOBCAT):10]=[4]*NLGSOCAM+[0]*NBOBCAT#reorder (4 for ocam)

cameraParams[10+7*ncamSL:2+7*ncamSL+10*(NLGSOCAM+NBOBCAT):10]=20#threadprio
cameraParams[11+7*ncamSL:2+7*ncamSL+10*(NLGSOCAM+NBOBCAT):10]=[0xff00ff00]*NLGSOCAM+[0xff00ff00]*NBOBCAT#threadaffin
cameraParams[2+7*ncamSL+10*(NLGSOCAM+NBOBCAT)]=2#skipFrameAfterBad
cameraParams[3+7*ncamSL+10*(NLGSOCAM+NBOBCAT)]=0#pxlRowStartSkipThreshold
cameraParams[4+7*ncamSL+10*(NLGSOCAM+NBOBCAT)]=0#pxlRowEndInsertThreshold
cameraParams[5+7*ncamSL+10*(NLGSOCAM+NBOBCAT)]=0#recordTimestamp
cameraParams[6+7*ncamSL+10*(NLGSOCAM+NBOBCAT)]=namelen#length of names...
cameraParams[7+7*ncamSL+10*(NLGSOCAM+NBOBCAT):].view("c")[:]=camNames

#print cameraParams,cameraParams[7+7*ncamSL+6*NBOBCAT:].view("c")

#This one works well - gets a ~500Hz rate with a 10kHz rate if numPulses==10, and 133Hz if numPulses=66.  And 151Hz if numPulses=58.
#If lgs rate is 1e8/7714, then 57 gives 168Hz, while 67  gives 149Hz. (1e8/671118
#If lgs rate is 1e8/10000, then 51 gives 151.51Hz.  (use 1e8/660000 for frame rate)
#aravisCmd0="TriggerMode=Off;PixelFormat=Mono12;PixelSize=Bpp12;BinningHorizontal=x2;BinningVertical=x2;ProgFrameTimeEnable=false;GevSCPSPacketSize=9000;ProgFrameTimeAbs=10000;TriggerType=FrameAccumulation;ExposureTimeRaw=4;ExposureMode=Timed;TriggerNumPulses=67;CenterScanMode=false;TriggerMode=On;"

ab=numpy.array([1056,121]).astype("i").byteswap()
aravisCmd0="DigitizedImageWidth=%d;DigitizedImageHeight=%d;TestPattern=Off;GevStreamThroughputLimit=1075773440;R[0x0d04]=8164;R[0x12650]=7;Bulk0Mode=UART;R[0x20017814]=6;BulkNumOfStopBits=One;BulkParity=None;BulkLoopback=false;EventNotification=Off;"%(ab[0],ab[1])
#GevStreamThroughputLimit=1075773440 #8000 Mbps byteswapped.
#GevSCPSPacketSize=9000 doesn't seem settable - so set via reg instead:
#R[0x0d04]=9000  #Note, this-36 bytes of data sent per packet.  Default on switchon is 576 (540 bytes).  Seems to be set to 8164 by the eBUSPlayer - so probably use this!
#SensorDigitizationTaps=Eight  - doesn't work - need to set the register:
#[0x12650]=7  #Sets SensorDigitizationTaps to Eight

#Bulk0Mode=UART (which is enum 0 so don't need reg)
#Bulk0SystemClockDivider=By128 - need to set via reg:
#R[0x20017814]=6
#BulkNumOfStopBits=One  (which is enum 0 so don't need reg)
#BulkParity=None


aravisCmd1="TriggerMode=Off;PixelFormat=Mono8;PixelSize=Bpp8;BinningHorizontal=x1;BinningVertical=x1;ProgFrameTimeEnable=false;GevSCPSPacketSize=9000;TriggerType=Fast;ExposureTimeRaw=100;CenterScanMode=false;ExposureMode=Off;TriggerMode=On;"#ProgFrameTimeAbs=20000;

#To get running in a timed exposure mode (eg for LQG), set ExposureMode=Timed;
#Then, ExposureTimeRaw=3000; can be used to set in microseconds.
#TriggerDelayRaw=1000; delays the trigger for this many microseconds.
#To unset exposure mode (to 1/trigger period), use ExposureMode=Off;

host="127.0.0.1"
while len(host)%4!=0:
    host+='\0'
cameraParams=numpy.zeros((2+len(host)//4,),numpy.int32)
cameraParams[0]=1#asfloat
cameraParams[1]=8500#port
cameraParams[2:]=numpy.fromstring(host,dtype=numpy.int32)

rmx=numpy.zeros((nacts,ncents)).astype("f")
print rmx.shape


if NLGSOCAM>0:
    reorder=numpy.zeros((264*242,),numpy.int32)
    for i in range(npxlx[ncamSL]*npxly[ncamSL]):
        pxl=i//8#the pixel within a given quadrant
        if((pxl%66>5) and (pxl<66*120)):#not an overscan pixel
            amp=i%8#the amplifier (quadrant) in question    
            rl=1-i%2#right to left
            tb=1-amp//4#top to bottom amp (0,1,2,3)?
            x=(tb*2-1)*(((1-2*rl)*(pxl%66-6)+rl*59)+60*amp)+(1-tb)*(60*8-1)
            y=(1-tb)*239+(2*tb-1)*(pxl//66)
            j=y*264+x;
            reorder[i]=j
else:
    reorder=None



useSL240=0
nodmc=0
if useSL240:
    mirrorName="libmirrorSL240.so"
    mirrorParams=numpy.zeros((5,),"i")
    mirrorParams[0]=1000#timeout/ms
    mirrorParams[1]=3#port
    mirrorParams[2]=1#thread affinity el size
    mirrorParams[3]=3#thread prioirty
    mirrorParams[4]=-1#thread affinity
elif nodmc:
    mirrorName="libmirrorPdAO32AlpaoThreaded.so"
    mirrorParams=numpy.zeros((12,),"i")
    mirrorParams[0]=1#elsize
    mirrorParams[1]=3#prio
    mirrorParams[2]=-1#affin
    mirrorParams[3]=1#number of Pd32AO boards
    mirrorParams[4]=1#number of ALPAO DMs
    mirrorParams[5]=0#board number - first board.
    mirrorParams[6:8]=numpy.fromstring("BEL111\0\0",dtype=numpy.int32)#alpao serial number
    mirrorParams[8]=59#nacts for the PdAO32
    mirrorParams[9]=241#nacts for the alpao
    mirrorParams[10]=96#nactInit for PdAO32
    mirrorParams[11]=241#Ignored, but nactInit for alpao

else:#use a socket
    host="127.0.0.1"
    while len(host)%4!=0:
        host+='\0'
    mirrorName="libmirrorSocket.so"
    mirrorParams=numpy.zeros((7+len(host)//4,),"i")
    mirrorParams[0]=1#timeout, not used
    mirrorParams[1]=8500#port on receiver
    mirrorParams[2]=1#affin el size
    mirrorParams[3]=1#priority
    mirrorParams[4]=-1#affinity
    mirrorParams[5]=0#send prefix
    mirrorParams[6]=1#as float
    mirrorParams[7:]=numpy.fromstring(host,dtype=numpy.int32)


v0=numpy.zeros((nacts,),"f")#v0 from the tomograhpcic algorithm in openloop (see spec)
#v0[-2:]=32768+16384#mid range for tt mirror 5v.
actuators=numpy.ones((nacts,),"f")*32768
actuators[-241:]=0.#midrange for alpao. (-1 to 1)

ub=numpy.zeros((sum(nsub),),numpy.int32)
ub[:]=-12
ub[sum(nsub[:ncamSL]):sum(nsub[:ncamSL+NLGSOCAM])]=-25#the lgs
ub[sum(nsub[:ncamSL+NLGSOCAM]):]=-20#and the figure sensors
maxAdapOffset=numpy.zeros((subapFlag.sum(),),numpy.int32)
maxAdapOffset[:]=4
maxAdapOffset[subapFlag[:sum(nsub[:ncamSL])].sum():subapFlag[:sum(nsub[:ncamSL+NLGSOCAM])].sum()]=2
#maxAdapOffset[subapFlag[:sum(nsub[:(NNGSCAM+1)//2])].sum():]=2

adapBoundary=numpy.zeros((ncam,4),numpy.int32)
for i in range(ncam):
    adapBoundary[i]=(0,npxly[i],0,npxlx[i])
#and stop the lgs getting to the top/bottom edge:
if NLGSOCAM!=0:
    adapBoundary[ncamSL]=(1,239,0,240)

actInit=numpy.ones((96,),numpy.uint16)*32768
actInit[64:67]+=16384 #lgs tt mirror

#Tip/Tilt drive is differential. Max differential voltage is 13V.
#DAC outputs range from -10V (for 0x0) to +10V (for 0x10000); 
#however outputs must be limited to +/- 6.5V for the TT outputs
#because of above max differential limit.
#+6.5V ~ 0x8000 + (0x8000 * 6.5/10) = 0x8000 + 0x5334
#-6.5V ~ 0x8000 - (0x8000 * 6.5/10) = 0x8000 - 0x5334

#Now we need a matrix to map the tip tilt signals to the 4 or 3 actuators that create them.
actControlMx=numpy.zeros((nacts+2,nacts),numpy.float32)
#actControlMx[:52,:52]=numpy.identity(52)
actControlMx[-241:,-241:]=numpy.identity(241)  #  same as: actControlMx[59:,56:]=numpy.identity(241)
#tt - differential
actControlMx[0,0]=21300./32768
actControlMx[1,0]=-21300./32768
actControlMx[2,1]=21300./32768
actControlMx[3,1]=-21300./32768
#lgs tt - a 3 actuator dm, with acts spaced at 120 degrees around the dm.
#This can take from 0 to 10V.  But, want darc to have full range (0-65535), so need to scale the darc inputs here... ie half them.  And actually, due to the way it is driven, need to do a bit more than half - ie 1/(0.5+sqrt(3)/2).
#sf=0.5/(0.5+numpy.sqrt(3)/2)
#actControlMx[56,54]=1*sf
#actControlMx[57,54]=-0.5*sf#sin(30)
#actControlMx[57,55]=-numpy.sqrt(3)/2.*sf#cos(30)
#actControlMx[58,54]=-0.5*sf#sin(30)
#actControlMx[58,55]=numpy.sqrt(3)/2.*sf#cos(30)
import scipy.sparse
#convert to sparse
csr=scipy.sparse.csr_matrix(actControlMx)
#and put into darc format.
actControlMx=numpy.concatenate([csr.indptr.astype(numpy.int32),csr.indices.astype(numpy.int32),csr.data.astype(numpy.float32).view(numpy.int32)])

actNewSize=nacts+2

#Mapping to the DAC card (not used in simulation)
actMapping=numpy.arange((nacts+3)).astype("i")
actMapping[52]=80#tip+
actMapping[53]=81#tip-
actMapping[54]=82#tilt+
actMapping[55]=83#tilt-
actMapping[56]=70#64
actMapping[57]=71#65
actMapping[58]=72#66

print "TODO: Check actMapping for alpao"
#actMapping[59:]=numpy.arange(241)#CHECK THIS IS CORRECT!

actScale=None#numpy.ones((nacts+2,),numpy.float32)
actSource=None#numpy.arange((nacts+2)).astype("i")
actOffset=numpy.zeros((nacts+2,),numpy.float32)
actOffset[0]=32768-21300
actOffset[1]=32768+21300
actOffset[2]=32768-21300
actOffset[3]=32768+21300
#actOffset[56]=32768+16384-32768*sf
#actOffset[57]=32768*sf*(0.5+numpy.sqrt(3)/2.)+32768+16384
#actOffset[58]=32768*sf*(0.5-numpy.sqrt(3)/2.)+32768+16384
#The equation to set DAC value actMapping[i] is
# act[actSource[i]] * actScale[i] + actOffset[i]
#or
#(actControlMx dot acts) + actOffset

actMin=numpy.ones((actNewSize,),numpy.float32)*-1e9
actMax=numpy.ones((actNewSize,),numpy.float32)*1e9
actMin[-241:]=-1#alpao
actMax[-241:]=1#alpao

creepAbstats=numpy.random.random(241).astype("f")
creepMean=numpy.random.random(241).astype("f")
creepTime=time.time()
creepMode=0

control={
    "switchRequested":0,#this is the only item in a currently active buffer that can be changed...
    "pause":0,
    "go":1,
    "maxClipped":15,
    "openLoopIfClip":1,
    "refCentroids":None,
    "centroidMode":"CoG",#whether data is from cameras or from WPU.
    "windowMode":"basic",
    "thresholdAlgo":1,
    "reconstructMode":"simple",#simple (matrix vector only), truth or open
    "centroidWeight":None,
    "v0":v0,
    "bleedGain":0.0,#0.05,#a gain for the piston bleed...
    "actMax":actMax,
    "actMin":actMin,
    "nacts":nacts,
    "ncam":ncam,
    "nsub":nsub,
    #"nsubx":nsubx,
    "npxly":npxly,
    "npxlx":npxlx,
    "ncamThreads":ncamThreads,
    "pxlCnt":pxlCnt,
    "subapLocation":subapLocation,
    "bgImage":bgImage,
    "darkNoise":darkNoise,
    "closeLoop":1,
    "flatField":flatField,#numpy.random.random((npxls,)).astype("f"),
    "thresholdValue":0.,#could also be an array.
    "powerFactor":1.,#raise pixel values to this power.
    "subapFlag":subapFlag,
    "fakeCCDImage":fakeCCDImage,
    "printTime":0,#whether to print time/Hz
    "rmx":rmx,#numpy.random.random((nacts,ncents)).astype("f"),
    "gain":numpy.ones((nacts,),"f"),
    "E":numpy.zeros((nacts,nacts),"f"),#E from the tomoalgo in openloop.
    "threadAffinity":None,
    "threadPriority":numpy.ones((ncamThreads.sum()+1,),numpy.int32)*10,
    "delay":1000,
    "clearErrors":0,
    "camerasOpen":1,
    "cameraName":"libcamsocket.so",#"libcamSL240AravisNOCRC.so",#"camfile",
    "cameraParams":cameraParams,
    "mirrorName":mirrorName,
    "mirrorParams":mirrorParams,
    "mirrorOpen":1,
    "frameno":0,
    "switchTime":numpy.zeros((1,),"d")[0],
    "adaptiveWinGain":0.5,
    "corrThreshType":0,
    "corrThresh":0.,
    "corrFFTPattern":None,#correlation.transformPSF(correlationPSF,ncam,npxlx,npxly,nsubx,nsuby,subapLocation),
#    "correlationPSF":correlationPSF,
    "nsubapsTogether":1,
    "nsteps":0,
    "addActuators":1,
    "actuators":actuators,#(numpy.random.random((3,52))*1000).astype("H"),#None,#an array of actuator values.
    "actSequence":None,#numpy.ones((3,),"i")*1000,
    "recordCents":0,
    "pxlWeight":None,
    "averageImg":0,
    "slopeOpen":1,
    "slopeParams":None,
    "slopeName":"librtcslope.so",
    "actuatorMask":None,
    "averageCent":0,
    "calibrateOpen":1,
    "calibrateName":"librtccalibrate.so",
    "calibrateParams":None,
    "corrPSF":None,
    "centCalData":None,
    "centCalBounds":None,
    "centCalSteps":None,
    "figureOpen":0,
    "figureName":"figureSL240",
    "figureParams":None,
    "reconName":"libreconmvm.so",
    "fluxThreshold":0,
    "printUnused":1,
    "useBrightest":ub,
    "figureGain":1,
    "decayFactor":None,#used in libreconmvm.so
    "reconlibOpen":1,
    "maxAdapOffset":maxAdapOffset,
    "version":" "*120,
    "adapWinShiftCnt":adapWinShiftCnt,
    "adapResetCount":100,
    "adapBoundary":adapBoundary,
#    "aravisCmdAll":aravisCmdAll,
    "actInit":actInit,
    "actMapping":actMapping,
    "actSource":actSource,
    "actScale":actScale,
    "actOffset":actOffset,
    "actControlMx":actControlMx,
    "actNew":actNewSize,
#    "aravisCmd%d"%(ncamSL):aravisCmd0,
#    "aravisCmd%d"%(ncamSL+1):aravisCmd1,
#    "aravisCmd%d"%(ncamSL+2):aravisCmd1,
#    "camReorder4":reorder,
#    "creepMean":creepMean,
#    "creepAbstats":creepAbstats,
#    "creepMode":creepMode,
#    "creepTime":numpy.array([creepTime])[0],
    }

