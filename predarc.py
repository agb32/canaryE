import numpy
import base.aobase
class Predarc(base.aobase.aobase):
    def __init__(self,parent,config,args={},forGUISetup=0,debug=None,idstr=None):
        if type(parent)!=type({}):
            parent={"1":parent}
        base.aobase.aobase.__init__(self,parent,config,args,forGUISetup=forGUISetup,debug=debug,idstr=idstr)
        """PArents will be a-d for NGS (d being truth).  Need to rotate these, then combine (interleave, add pixels, etc).
        """
        self.readnoise=self.config.getVal("readnoise")#a list, one for each WFS.
        self.bg=self.config.getVal("background")#a list, either of floats, or of images.
        self.fliprot=self.config.getVal("fliprotateWFS")#angle in degrees which to rotate wfs by.  A list. 
        self.npxlxDarc=self.config.getVal("npxlxDarc")#image size in darc.  For each camera.
        self.npxlyDarc=self.config.getVal("npxlyDarc",default=self.npxlxDarc)#image size in darc.  For each camera.
        self.npxlDarc=numpy.array(self.npxlxDarc)*numpy.array(self.npxlyDarc)
        self.keyList=self.config.getVal("predarcKeyList",default=["1","2","3","4"])
        self.imgOffset=self.config.getVal("imgOffset",default=None,raiseerror=0)
        self.outputData=numpy.zeros((numpy.array(self.npxlxDarc)*numpy.array(self.npxlyDarc)).sum(),numpy.float32)

    def newParent(self,parent,idstr=None):
        raise Exception("Please don't call newParent for predarc module")
        
    def generateNext(self,ms=None):
        if self.generate==1:
            if self.newDataWaiting:
                self.dataValid=1
                for key in self.parent.keys():
                    if self.parent[key].dataValid==0:
                        self.dataValid=0
            if self.dataValid:
                self.getInputData()
        else:
            self.dataValid=0
            

    def getInputData(self):
        pos=0
        for i in range(len(self.keyList)):#0-3=ngs
            key=self.keyList[i]
            img=self.parent[key].outputData
            #first, rotate (wrt the truth).
            if self.fliprot[i]!=0:
                if self.fliprot[i]==1:#symmetry about vertical axis
                    img[:]=img.copy()[:,::-1]
                elif self.fliprot[i]==4:#rotation of 180 degrees and vertical flip.  Or, rotation of 90 and horiz flip.
                    img=numpy.rot90(img,1)[:,::-1]
                elif self.fliprot[i]==7:#transpose + rotation of 180.  Or, rotation of 90 and vertical flip (about the hozir axis).
                    img=numpy.rot90(img,1)[::-1]
                elif self.fliprot[i]==9:#symmetry about horiz axis
                    img[:]=img.copy()[::-1]
                elif self.fliprot[i]==3:#rotation of 180 degrees
                    img[:]=numpy.rot90(img,2)
                elif self.fliprot[i]==5:#rotate 270 degrees
                    img[:]=numpy.rot90(img,3)
                else:
                    raise Exception("Symmetry code %d not yet implemented"%self.fliprot[i])
            #then add a background and readnoise in the extra pixels
            img2=numpy.random.normal(scale=self.readnoise[i],size=(self.npxlyDarc[i],self.npxlxDarc[i]))
            #then insert the image into the extra pixels.
            if self.imgOffset==None or self.imgOffset[i]==None:
                fx=(self.npxlxDarc[i]-img.shape[0])/2
                fy=(self.npxlxDarc[i]-img.shape[0])/2
            else:
                fy,fx=self.imgOffset[i]
            #print img.shape
            #print img2.shape
            img2[fy:fy+img.shape[0],fx:fx+img.shape[1]]+=img
            #and add the background (single value or array).
            img2+=self.bg[i]
            #And now paste the image into the pixel array (outputData)
            tmp=self.outputData[self.npxlDarc[:i].sum():self.npxlDarc[:i+1].sum()]
            tmp.shape=self.npxlyDarc[i],self.npxlxDarc[i]
            tmp[:]=img2
            

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

