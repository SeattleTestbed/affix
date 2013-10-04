import sys
import dylink_portability

if len(sys.argv) < 7:
    print "Usage: \n\t$> python run_shim_proxy.py server_address, server_port, listening_addr, listening_port, shim_port, shim_string"
    sys.exit()

server_address = sys.argv[1]
server_port = int(sys.argv[2])
# Specify the TCP port to listen on.
listening_addr = sys.argv[3]
listening_port = int(sys.argv[4])
shim_port = int(sys.argv[5])
shim_string = sys.argv[6]

dylink_portability.run_unrestricted_repy_code("shim_dumb_server_v2.py", [server_address, server_port, listening_addr, listening_port, shim_port, shim_string])
