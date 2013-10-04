import sys
import dylink_portability

if len(sys.argv) < 6:
    print "Usage: \n\t$> run_rate_limit_proxy.py server_address, server_port, listening_port, shim_port, shim_string"
    sys.exit()

server_address = sys.argv[1]
server_port = int(sys.argv[2])
# Specify the TCP port to listen on.
listening_port = int(sys.argv[3])
shim_port = int(sys.argv[4])
shim_string = sys.argv[5]

dylink_portability.run_unrestricted_repy_code("shim_rate_limit_server_proxy.py", [server_address, server_port, listening_port, shim_port, shim_string])
