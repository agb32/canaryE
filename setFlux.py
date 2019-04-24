import sys
import util.analyse
val=float(sys.argv[1])

txt="""data=wfscentList[0].thisObjList[0].wfscentObj.centcmod.sig
wfscentList[0].thisObjList[0].wfscentObj.centcmod.update(2,%g)
wfscentList[0].thisObjList[0].wfscentObj.centcmod.sig=%g
wfscentList[0].thisObjList[0].wfscentObj.sig=%g
"""%(val,val,val)

for i in range(4):
    a=util.analyse.analyse()
    a.openConnection("localhost",9000+i,pr=0)

    a.execute(txt,rt="data")
    data=a.getData(block=1)
    data=data[0]
    print "Setting flux from %s to %g"%(str(data),val)
