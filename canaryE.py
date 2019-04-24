#mpirun -np 5 -hostlist n1-c437 n2-c437 n3-c437 n4-c437 n5-c437  /usr/local/bin/mpipython $PWD/thisfile.py
#Python code created using the simulation setup GUI...
#Order of execution may not be quite optimal - you can always change by hand
#for large simulations - typically, the order of sends and gets may not be
#quite right.  Anyway, enjoy...
import numpy
import util.Ctrl
import science.iscrn
import predarc
import postdarc
import science.darcsim
import science.zdm
import science.xinterp_dm
import science.wfscent
import science.iatmos
import science.science
import base.mpiGet
import base.mpiSend
import base.shmGet
import base.shmSend
ctrl=util.Ctrl.Ctrl(globals=globals())
print "Rank %d imported modules"%ctrl.rank
#Set up the science modules...
newMPIGetList=[]
newMPISendList=[]
newSHMGetList=[]
newSHMSendList=[]
iscrnList=[]
PredarcList=[]
PostdarcList=[]
DarcList=[]
dmList=[]
wfscentList=[]
iatmosList=[]
scienceList=[]
ttval=ctrl.config.getVal("tipTiltVal",default=1.)
#Add any personal code after this line and before the next, and it won't get overwritten
if ctrl.rank==4:
    dims,dtype=science.iscrn.iscrn(None,ctrl.config,args={},forGUISetup=1,idstr="allLayers").outputData
    newMPIGetList.append(base.mpiGet.newMPIGet(dims,dtype,0,3,ctrl.mpiComm))
    iatmosList.append(science.iatmos.iatmos({"allLayers":newMPIGetList[0],},ctrl.config,args={},idstr="sci1"))
    scienceList.append(science.science.science(iatmosList[0],ctrl.config,args={},idstr="sci1uncorr"))
    dims,dtype=postdarc.Postdarc(None,ctrl.config,args={},forGUISetup=1,idstr=None).outputData
    newMPIGetList.append(base.mpiGet.newMPIGet(dims,dtype,0,7,ctrl.mpiComm))
    dmList.append(science.zdm.dm({"1":newMPIGetList[1],"2":iatmosList[0],},ctrl.config,args={},idstr="ttpathsci1"))
    dmList.append(science.xinterp_dm.dm({"1":newMPIGetList[1],"2":dmList[0],},ctrl.config,args={},idstr="dm0pathsci1"))
    scienceList.append(science.science.science(dmList[1],ctrl.config,args={},idstr="sci1"))
    execOrder=[newMPIGetList[0],iatmosList[0],scienceList[0],newMPIGetList[1],dmList[0],dmList[1],scienceList[1],]
    ctrl.mainloop(execOrder)
if ctrl.rank==2:
    dims,dtype=science.iscrn.iscrn(None,ctrl.config,args={},forGUISetup=1,idstr="allLayers").outputData
    newMPIGetList.append(base.mpiGet.newMPIGet(dims,dtype,0,4,ctrl.mpiComm))
    iatmosList.append(science.iatmos.iatmos({"allLayers":newMPIGetList[0],},ctrl.config,args={},idstr="2"))
    dims,dtype=postdarc.Postdarc(None,ctrl.config,args={},forGUISetup=1,idstr=None).outputData
    newMPIGetList.append(base.mpiGet.newMPIGet(dims,dtype,0,8,ctrl.mpiComm))
    dmList.append(science.zdm.dm({"1":newMPIGetList[1],"2":iatmosList[0],},ctrl.config,args={},idstr="ttpath2"))
    wfscentList.append(science.wfscent.wfscent(dmList[0],ctrl.config,args={},idstr="2"))
    newMPISendList.append(base.mpiSend.newMPISend(wfscentList[0],0,1,ctrl.mpiComm))
    execOrder=[newMPIGetList[0],iatmosList[0],newMPIGetList[1],dmList[0],wfscentList[0],newMPISendList[0],]
    ctrl.mainloop(execOrder)
if ctrl.rank==3:
    dims,dtype=science.iscrn.iscrn(None,ctrl.config,args={},forGUISetup=1,idstr="allLayers").outputData
    newMPIGetList.append(base.mpiGet.newMPIGet(dims,dtype,0,5,ctrl.mpiComm))
    iatmosList.append(science.iatmos.iatmos({"allLayers":newMPIGetList[0],},ctrl.config,args={},idstr="3"))
    dims,dtype=postdarc.Postdarc(None,ctrl.config,args={},forGUISetup=1,idstr=None).outputData
    newMPIGetList.append(base.mpiGet.newMPIGet(dims,dtype,0,9,ctrl.mpiComm))
    dmList.append(science.zdm.dm({"1":newMPIGetList[1],"2":iatmosList[0],},ctrl.config,args={},idstr="ttpath3"))
    wfscentList.append(science.wfscent.wfscent(dmList[0],ctrl.config,args={},idstr="3"))
    newMPISendList.append(base.mpiSend.newMPISend(wfscentList[0],0,2,ctrl.mpiComm))
    execOrder=[newMPIGetList[0],iatmosList[0],newMPIGetList[1],dmList[0],wfscentList[0],newMPISendList[0],]
    ctrl.mainloop(execOrder)
if ctrl.rank==0:
    iscrnList.append(science.iscrn.iscrn(None,ctrl.config,args={},idstr="allLayers"))
    newMPISendList.append(base.mpiSend.newMPISend(iscrnList[0],1,6,ctrl.mpiComm))
    newMPISendList.append(base.mpiSend.newMPISend(iscrnList[0],2,4,ctrl.mpiComm))
    newMPISendList.append(base.mpiSend.newMPISend(iscrnList[0],3,5,ctrl.mpiComm))
    newMPISendList.append(base.mpiSend.newMPISend(iscrnList[0],4,3,ctrl.mpiComm))
    iatmosList.append(science.iatmos.iatmos({"allLayers":iscrnList[0],},ctrl.config,args={},idstr=None))
    PostdarcList.append(postdarc.Postdarc(None,ctrl.config,args={},idstr=None))
    newMPISendList.append(base.mpiSend.newMPISend(PostdarcList[0],1,10,ctrl.mpiComm))
    newMPISendList.append(base.mpiSend.newMPISend(PostdarcList[0],2,8,ctrl.mpiComm))
    newMPISendList.append(base.mpiSend.newMPISend(PostdarcList[0],3,9,ctrl.mpiComm))
    newMPISendList.append(base.mpiSend.newMPISend(PostdarcList[0],4,7,ctrl.mpiComm))
    dmList.append(science.zdm.dm({"1":PostdarcList[0],"2":iatmosList[0],},ctrl.config,args={},idstr="ttpath4"))
    dmList.append(science.xinterp_dm.dm({"1":dmList[0],"2":PostdarcList[0],},ctrl.config,args={},idstr="dm0path4"))
    wfscentList.append(science.wfscent.wfscent(dmList[1],ctrl.config,args={},idstr="4"))
    dims,dtype=science.wfscent.wfscent(None,ctrl.config,args={},forGUISetup=1,idstr="2").outputData
    newMPIGetList.append(base.mpiGet.newMPIGet(dims,dtype,2,1,ctrl.mpiComm))
    dims,dtype=science.wfscent.wfscent(None,ctrl.config,args={},forGUISetup=1,idstr="3").outputData
    newMPIGetList.append(base.mpiGet.newMPIGet(dims,dtype,3,2,ctrl.mpiComm))
    dims,dtype=science.wfscent.wfscent(None,ctrl.config,args={},forGUISetup=1,idstr="1").outputData
    newMPIGetList.append(base.mpiGet.newMPIGet(dims,dtype,1,11,ctrl.mpiComm))
    PredarcList.append(predarc.Predarc({"4":wfscentList[0],"1":newMPIGetList[2],"2":newMPIGetList[0],"3":newMPIGetList[1],},ctrl.config,args={},idstr=None))
    DarcList.append(science.darcsim.Darc({"img":PredarcList[0],},ctrl.config,args={},idstr="darc"))
    PostdarcList[0].newParent(DarcList[0],None)
    execOrder=[iscrnList[0],newMPISendList[0],newMPISendList[1],newMPISendList[2],newMPISendList[3],iatmosList[0],PostdarcList[0],newMPISendList[4],newMPISendList[5],newMPISendList[6],newMPISendList[7],dmList[0],dmList[1],wfscentList[0],newMPIGetList[0],newMPIGetList[1],newMPIGetList[2],PredarcList[0],DarcList[0],]
    ctrl.mainloop(execOrder)
if ctrl.rank==1:
    dims,dtype=science.iscrn.iscrn(None,ctrl.config,args={},forGUISetup=1,idstr="allLayers").outputData
    newMPIGetList.append(base.mpiGet.newMPIGet(dims,dtype,0,6,ctrl.mpiComm))
    iatmosList.append(science.iatmos.iatmos({"allLayers":newMPIGetList[0],},ctrl.config,args={},idstr="1"))
    dims,dtype=postdarc.Postdarc(None,ctrl.config,args={},forGUISetup=1,idstr=None).outputData
    newMPIGetList.append(base.mpiGet.newMPIGet(dims,dtype,0,10,ctrl.mpiComm))
    dmList.append(science.zdm.dm({"1":newMPIGetList[1],"2":iatmosList[0],},ctrl.config,args={},idstr="ttpath1"))
    wfscentList.append(science.wfscent.wfscent(dmList[0],ctrl.config,args={},idstr="1"))
    newMPISendList.append(base.mpiSend.newMPISend(wfscentList[0],0,11,ctrl.mpiComm))
    execOrder=[newMPIGetList[0],iatmosList[0],newMPIGetList[1],dmList[0],wfscentList[0],newMPISendList[0],]
    ctrl.mainloop(execOrder)
print "Simulation finished..."
#Add any personal code after this, and it will not get overwritten
ctrl.config.abort(0)

