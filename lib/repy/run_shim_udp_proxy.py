import sys
import dylink_portability

dylink_portability.run_unrestricted_repy_code("udp_proxy.repy", sys.argv[1:])
