#pragma out Server timed out properly

import sys

from repyportability import *
add_dy_support(locals())

#dy_import_module_symbols("timeoutaffix.repy")
dy_import_module_symbols("affixstackinterface.repy")

# Used for importing the SocketTimeoutError class.
#dy_import_module_symbols("sockettimeout.repy")

myip = getmyip()
server_port = 12345
source_port = 12346

# Use the TimeoutAffix for this test with the
# timeout set to 10 seconds.
timeout = 10
affix_string = "(TimeoutAffix,%d)" % timeout
time_to_wait = 15


def error_and_exit(wait_time):

  # Launch a thread that waits for a time period (15 seconds)
  # that is longer then the timeout set (10 seconds). If the
  # test has not exited by the time we finish our sleep, then
  # the test fails.
  def _error_exit_helper():
    sleep(wait_time)
    print "Error: Managed to wait more than '%d' seconds" % wait_time
    exitall()

  return _error_exit_helper



def server():

  # We setup and launch a listening socket to wait for incoming
  # connection. 
  affix_object = AffixStackInterface(affix_string)
  server_sock = affix_object.listenforconnection(myip, server_port)

  # We accept an incoming connection but then do nothing else after
  # we have accepted the connection.
  while True:
    try:
      rip, rport, sockobj = server_sock.getconnection()
      break
    except SocketWouldBlockError:
      sleep(0.1)
  
  try:
    # We will try to receive data but the client won't be
    # sending any data. We should receive a timeout error
    # after the appropriate time.
    sockobj.recv(1)
  except SocketWouldBlockError, err:
    # Once we receive the SocketTimeoutError, we close the
    # connection, which will let the client know that the
    # server has closed due timeout.
    if str(err) != "recv() timed out!!":
      print "Server did not receive timeout error! Error raised: " + str(err)
    sockobj.close()
  except Exception, err:
    print "Server received error message that wasn't SocketTimeoutError! '%s'" % str(err)
    sockobj.close()

  # We will sleep for a period of time that is greater then the
  # timeout that has been set. This should cause the client to
  # timeout when doing send() and recv() without getting socket
  # closed error.
  sleep(time_to_wait + 5)



if __name__ == '__main__':

  # Launch the server then wait a few second for the server to 
  # start up before connecting to it.
  createthread(server)
  sleep(2)

  client_sock = openconnection(myip, server_port, myip, source_port, timeout)

  # Try to receive data that isn't being sent by the server. If all
  # goes well then the server will close the connection after the 
  # timeout has expired.
  start_time = getruntime()
  while True:
    try:
      client_sock.recv(1)
    except SocketWouldBlockError:
      sleep(0.1)
    except SocketClosedRemote:
      # Great! The server timed out and closed the connection remotely.
      # Now we check if the timeout is in the time range that we expect.
      time_spent = getruntime() - start_time

      # Ensure that the timeout is in acceptible range.
      if time_spent < 10 or time_spent > 11:
        print "Server did not close socket in timely manner. Should have closed around 10 seconds, instead closed around '%s' seconds." % str(time_spent)
      else:
        print "Server timed out properly at %s seconds. Test passed." % str(time_spent)

        # For some reason if I don't manually flush the output, utf.py does not 
        # catch the output from this test, causing it to fail. I am forcibly flushing
        # so the output is passed back to utf.
        sys.stdout.flush()
      exitall()
  
