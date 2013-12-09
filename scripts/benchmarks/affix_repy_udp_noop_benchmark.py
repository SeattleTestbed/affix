"""
<Program Name>
  affix_python_udp_benchmark.py

<Author>
  Monzur Muhammad
  monzum@cs.washington.edu

<Date Started>
  4 December 2012

<Purpose>
  This is a test file that will be used for benchmarking
  udp connectivity over the loopback interface using 
  different data blocks.

<Usage>
  $ python affix_repy_udp_benchmark.py packet_block_size(in KB) total_data_to_send(in MB)
"""
import sys
import time
import threading
import random
import socket

from repyportability import *
_context = locals()
add_dy_support(_context)

dy_import_module_symbols("affixstackinterface")


# 1KB string size.
random_string = 'abcdefgh' * 128

block_size = 1024 
start_time = 0
sleep_time = 0.00001

FIN_TAG="@FIN"
total_data_sent = 0

port = 12345
server_address = '127.0.0.1'


affix_string = '(NoopAffix)'


class server(threading.Thread):
  """
  <Purpose>
    The purpose of this thread is to only receive the
    message sent by the client and time it.
  """
  def __init__(self):
    threading.Thread.__init__(self)

  def run(self):
    # Create a new server socket and accept a connection when
    # there is an incoming connection.
    affix_obj = AffixStackInterface(affix_string)
    sock_server = affix_obj.listenformessage(server_address, port)

    # Now that we have accepted the connection, we will 
    recv_msg = ''
    data_recv_len = 0
    last_data_recv_time = time.time()
    while True:
      try:
        rip, rport, cur_msg = sock_server.getmessage()
        #last_data_recv_time = time.time()
        if FIN_TAG in cur_msg:
          print "Received Fin packet."
          break
        data_recv_len += len(cur_msg)
        recv_msg += cur_msg
      except SocketWouldBlockError:
        #cur_time = time.time()
        # If we haven't received data for the last 2 seconds,
        # we will break.
        #if (cur_time - last_data_recv_time) > 3:
        #  break
        time.sleep(sleep_time)
        pass

    sock_server.close()
    total_run_time = time.time() - start_time
    
    print "Time to receive: %s" % str(total_run_time)
    print "Total data received: %d KB. \nThroughput: %s KB/s" % (data_recv_len/1024, str(data_recv_len/total_run_time/1024))

    total_data_loss = total_data_sent - data_recv_len
    print "Data loss: %d KB\nLoss rate: %s%%" % (total_data_loss/1024, str((total_data_loss*1.0/total_data_sent*100)))



def main():
  """
  <Purpose>
    The main thread is the client that sends data across to 
    the server across the loopback address.
  """
  global block_size
  global start_time
  global total_data_sent

  if len(sys.argv) < 3:
    print "  $ python affix_python_tcp_benchmark.py packet_block_size(in KB) total_data_to_send(in MB)"
    sys.exit(1)

  # Extract the user input to figure out what the block size will be 
  # and how much data to send in total.
  block_multiplier = int(sys.argv[1])
  data_length = int(sys.argv[2]) * 1024 * 1024

  repeat_data = random_string * block_multiplier
  block_size = block_size * block_multiplier
  
  total_sent = 0

  
  # Start the server then wait a few seconds before connecting.
  new_server = server()
  new_server.start()
  time.sleep(2)

  # Send data repeatedly until we have sent
  # sufficient ammount through UDP.
  affix_obj = AffixStackInterface(affix_string)

  start_time = time.time()
  myip = server_address
  while total_data_sent < data_length:
    try:
      total_data_sent += affix_obj.sendmessage(server_address, port, repeat_data, myip, port+1)
    except SocketWouldBlockError:
      time.sleep(sleep_time)
      pass
  # Send a signal telling the server we are done sending data.
  affix_obj.sendmessage(server_address, port, FIN_TAG, myip, port+1)
  



if __name__ == '__main__':
  main()
