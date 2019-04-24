import numpy
import base.aobase
import util.tel
class Postdarc(base.aobase.aobase):
    def __init__(self,parent,config,args={},forGUISetup=0,debug=None,idstr=None):
        base.aobase.aobase.__init__(self,parent,config,args,forGUISetup=forGUISetup,debug=debug,idstr=idstr)
        """Expect 245 actuators from darc, which we have to convert to 15x15 and 3."""
        # indx=numpy.nonzero(util.tel.Pupil(8,4,0).fn.ravel())[0]
        # arr=numpy.zeros((8,8),numpy.int32)
        # print indx.shape
        # arr.ravel()[indx]=numpy.arange(241).astype("i")
        # arr2=arr[::-1]
        # arr3=arr2[:,::-1]
        # self.indx=arr3.ravel()[indx]
        self.firsttime=1


        alpaoPup=util.tel.Pupil(17,8.9,0).fn.astype("i")
        if alpaoPup.sum()!=241:
            raise Exception("Alpao pupil: str(alpaoPup)")
        
        self.alpaoPupil=numpy.zeros((17*17),numpy.float32)
        self.alpaoPupIndx=numpy.flatnonzero(alpaoPup)
        
        dmInfo=self.config.getVal("dmInfoList")[0]
        dmflag=dmInfo.getDMFlag(self.config.getVal("atmosGeom"))
        print("dasp using %d actuators of the 241 available"%(dmflag.sum()))
        self.dmflagindx=numpy.flatnonzero(dmflag)
        darcflag=numpy.zeros((17,17),numpy.int32)
        darcflag[1:-1,1:-1]=dmflag
        self.darcflagindx=numpy.flatnonzero(darcflag)
        self.nactsForDasp=dmflag.sum()

        self.outputData=numpy.zeros((self.nactsForDasp+3,),numpy.float32)
        
        #total stroke of adonis is 8 microns, over 65536.
        #So, 1 unit is 0.000122 microns (8/65536.)
        #But dasp units, 1== 1 radian.
        #So at 532nm, 1==0.532/2./numpy.pi=0.8467 microns.
        #So, need to divide by 693.62.
        self.dmscale=-1/693.62
        #tip-tilt - full throw (65536) is about 2 arcsec on-sky.
        #The DM zernike modes is normalised to 1, and for this simulation has ptv of about 0.0355.
        #This is 0.005 PTV across each sub-aperture.  Pixel scale gives 3.85" per subap.
        #arcseconds of motion per 1 unit of zenike gies:  0.017735931274050629*2/7./2./numpy.pi*700e-9/.6*180/numpy.pi*3600=0.00019
        #So, ratio of these 2 scales:
        #s2=0.00019
        #s1=2/65536.
        #s1/s2=0.157
        #So, multiply acts by this value.
        self.ttscale=0.157
        self.fsmscale=0.157
        if forGUISetup:
            self.outputData=self.outputData.shape,self.outputData.dtype

    def generateNext(self,ms=None):
        self.dataValid=1
        if self.generate==1:
            if self.newDataWaiting:
                self.dataValid=1
                if self.parent.dataValid==0:
                    self.dataValid=self.firsttime
                    self.firsttime=0
            if self.dataValid:
                self.getInputData()
        else:
            self.dataValid=0

    def getInputData(self):
        p=self.parent
        data=p.outputData
        #put the darc actuators into a full 2d pupil (and scale)
        #print data.shape,self.alpaoPupIndx.shape
        self.alpaoPupil[self.alpaoPupIndx]=data[4:241+4]*self.dmscale
        #select the correct actuators for use with dasp
        self.outputData[:self.nactsForDasp]=(self.alpaoPupil[self.darcflagindx])
        #skip piston (hence +1 and +3, not 0->2)
        self.outputData[self.nactsForDasp+1:self.nactsForDasp+3]=(((data[0:3:2]-(32768-21300))*32768/21300.)-32768)*self.ttscale

        


    def plottable(self,objname="$OBJ"):
        """Return a XML string which contains the commands to be sent
        over a socket to obtain certain data for plotting.  The $OBJ symbol
        will be replaced by the instance name of the object - e.g.
        if scrn=mkscrns.Mkscrns(...) then $OBJ would be replaced by scrn."""
        if self.idstr==None:
            id=""
        else:
            id=" (%s)"%self.idstr
        txt=""
        txt+="""<plot title="predarc output%s" cmd="data=%s.outputData" ret="data" type="pylab" when="rpt" palette="gray"/>\n"""%(id,objname)
        return txt

    def getParams(self):
        """parameters required for this module, in the form of {"paramName":defaultValue,...}
        These params can then be placed in the config file... if not set by the
        user, the param should still be in config file as default value for
        future reference purposes.
        """
        #This is a working example.  Please feel free to change the parameters
        #required. (if you do, also change the config.getParam() calls too).
        paramList=[]
        return paramList

