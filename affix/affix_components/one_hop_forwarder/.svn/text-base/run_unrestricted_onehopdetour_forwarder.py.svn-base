import sys
import dylink_portability

if len(sys.argv) < 3:
    print "Usage: \n\t$> python run_onehopdetour_forwarder.py TCP_PORT UDP_PORT"
    sys.exit()

TCP_PORT = sys.argv[1]
UDP_PORT = sys.argv[2]

dylink_portability.run_unrestricted_repy_code("one_hop_forwarder.repy", [TCP_PORT, UDP_PORT])
