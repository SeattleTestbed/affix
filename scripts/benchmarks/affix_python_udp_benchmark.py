"""
<Program Name>
  affix_python_tcp_benchmark.py

<Author>
  Monzur Muhammad
  monzum@cs.washington.edu

<Date Started>
  4 December 2012

<Purpose>
  This is a test file that will be used for benchmarking
  tcp connectivity over the loopback interface using 
  different data blocks.

<Usage>
  $ python affix_python_tcp_benchmark.py packet_block_size(in KB) total_data_to_send(in MB)
"""
import sys
import time
import threading
import random
import socket

# 1KB string size.
random_string = 'a'
#random_string = 'abcdefgh' * 128

block_size = 1024 
start_time = 0

FIN_TAG="@FIN"
total_data_sent = 0

port = 12345
server_address = '127.0.0.1'

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
    sock_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_server.bind((server_address, port))


    # Now that we have accepted the connection, we will 
    recv_msg = ''
    data_recv_len = 0
    while True:
      try:
        cur_msg, addr = sock_server.recvfrom(block_size)
        if FIN_TAG in cur_msg:
          break
        data_recv_len += len(cur_msg)
        recv_msg += cur_msg
      except socket.error:
        break

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
  block_size = int(sys.argv[1])
  data_length = int(sys.argv[2]) * 1024 * 1024

  repeat_data = random_string * block_size
  
  total_sent = 0

  
  # Start the server then wait a few seconds before connecting.
  new_server = server()
  new_server.start()
  time.sleep(2)

  # Create a client socket and connect to the server. Following
  # the connection, send data repeatedly until we have sent
  # sufficient ammount.
  sockobj = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  start_time = time.time()
  while total_data_sent < data_length:
    total_data_sent += sockobj.sendto(repeat_data, (server_address, port))

  # Send a signal telling the server we are done sending data.
  for i in range(10):
    sockobj.sendto(FIN_TAG, (server_address, port))

  sockobj.close()
  



if __name__ == '__main__':
  main()
