import sys
import darc


gain=0.5
if len(sys.argv)>1:
    gain=float(sys.argv[1])
d=darc.Control("main")
g=d.Get("gain")
g[:]=gain
d.Set("gain",g)
d.Set("addActuators",1)
