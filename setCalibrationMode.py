import sys
import util.analyse
val=int(sys.argv[1])
txt="""for obj in ctrl.compList:
 if obj.control.has_key("cal_source"):
  obj.control["cal_source"]=%d
"""%val

a=util.analyse.analyse()
for i in range(5):
    a.openConnection("localhost",i+9000)

a.execute(txt)

