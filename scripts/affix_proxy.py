"""
<Program>
  proxy.repy

<Author>
  Monzur Muhammad, monzum@cs.washington.edu
  Danny Y. Huang, yh1@cs.williams.edu

<Purpose>
  Proxy server for non-affix-compatible applications. We can use it, for
  instance, to wget files from an apache server, such that both applications
  appear to use affixs. Here is the set-up:

  Host A runs Apache. This proxy listens for incoming connections from other
  proxies using affixs. When a new client is connected, the proxy makes a
  non-affix connection to the Apache server on port 80.

  Host B runs wget. This proxy listens for incoming connections from wget
  without using affixs. When wget connects to the proxy, we make a affix'ed
  connection to the destination proxy server.

"""

USAGE = """
  The command-line arguments are:
  outgoing_IP outgoing_port incoming_IP incoming_port affix'ed_port [affix_stack]

  The affix'ed port must be either the outgoing openconnection port, or the
  incoming listen port; it designates the usage of affixs on either ports. 

  In the example above, we run:
  - on host A: proxy.repy '127.0.0.1' 80            host_A_ip   listen_port_A listen_port_A '(CoordinationAffix)(StatAffix)(CompressionAffix)'
  - on host B: proxy.repy host_A_ip   listen_port_A '127.0.0.1' listen_port_B listen_port_A '(CoordinationAffix)(StatAffix)(CompressionAffix)'

"""

# Enable repyportability and dylink, so we can use repy API.
from repyportability import *
_context = locals()
add_dy_support(_context)

dy_import_module_symbols('affixstackinterface')
dy_import_module_symbols('random')

# The max buffersize. The amount of data to send at a time.
BUFFER_SIZE = 2**18

# Number of seconds to sleep when encountering the SocketWouldBlockError.
SLEEP_TIME = 0.010

# List of affix stacks for incoming connections. See the documentation of
# start_server() for how ports are assigned to each of the affix stacks.
INCOMING_AFFIX_STACK_LIST = ['(CoordinationAffix)']

# How we are going to open a new outgoing connection.
outgoing_ip = None
outgoing_port = None

# How we listen for incoming connections.
incoming_ip = None
incoming_port = None

# Which of the port above should use affixs.
affix_port = None





def start_server():
  """
  <Purpose>
    Launches a server that continuously waits for incoming connection.
    Once a connection is made, it launches a thread that handles the
    connection.

  <Arguments>
    None

  <Side Effects>
    None

  <Exception>
    None

  <Return>
    None

  """
  tcp_server_socket_list = []

  # Listen for connections from other proxies. We listen using several affix
  # stacks in parallel to facilitate the bulk testing of several affixs. For affix
  # stack with index i, we listen on port p + i, where p is the main listen port
  # specified in the command line.
  if incoming_port == affix_port:

    for index in range(len(INCOMING_AFFIX_STACK_LIST)):
      affix_stack_str = INCOMING_AFFIX_STACK_LIST[index]
      affix = AffixStackInterface(affix_stack_str, incoming_ip)
      port = incoming_port + index
      log('Affix stack', affix_stack_str, 'is about to listen on port', port,'\n')
      tcp_server_socket_list.append(affix.listenforconnection(affix.getmyip(), port))
      log('Affix stack', affix_stack_str, 'is listening on port', port,'\n')

  # Listen for connections from local applicaitons, such as wget.
  else:
    tcp_server_socket_list.append(listenforconnection(incoming_ip, incoming_port))

  # Waits for incoming connections.
  while True:

    log('Ready to accept new connections.\n')
    
    # Gets connection from whichever affix stack that does not block.
    index = 0
    while True:
      tcp_server_socket = tcp_server_socket_list[index]
      try:
        (remoteip, remoteport, in_socket) = tcp_server_socket.getconnection()
      except SocketWouldBlockError:
        sleep(SLEEP_TIME)
        index = (index + 1) % len(tcp_server_socket_list)
      else:
        break
    
    # Launch a new thread to handle incoming connection.
    server_func = handle_incoming_connection(remoteip, remoteport, in_socket)
    createthread(server_func)







def handle_incoming_connection(remoteip, remoteport, in_socket):
  """
  <Purpose>
    This function is launched when there is any incoming messages
    from a client.

  <Arguments>
    remoteip - the ip address of the remote/local client.
    remoteport - the port of the remote/local client.
    in_socket - the socket object that will be used for communication.

  <Exceptions>
    None.

  <Return>
    None.

  """

  def _threaded_function():

    # Keep trying until we find an allowable random local port
    while True:

      local_port = random_randint(10000, 59999)

      try: 

        # Open a connection to presumably the destination proxy
        if outgoing_port == affix_port:
          affix = AffixStackInterface(INCOMING_AFFIX_STACK_LIST[0])
          out_socket = affix.openconnection(outgoing_ip, outgoing_port, affix.getmyip(), local_port, 30)

        # Open a connection to presumably the local server, e.g. Apache.
        else:
          if outgoing_ip.startswith('127.'):
            local_ip = '127.3.5.7'
          else:
            local_ip = getmyip()
          log('proxy: openconnection with local IP', local_ip, '\n')
          out_socket = openconnection(outgoing_ip, outgoing_port, local_ip, local_port, 15)

      # Looks like the random local port is not allowed. We retry.
      except (DuplicateTupleError, ResourceForbiddenError), err:
        log('Local port', local_port, 'is not allowed; retrying another one:', repr(err), err, '\n')

      # Terminate thread upon any other exception.
      except Exception, err:
        info = 'Unable to make outgoing connection to %s:%s ' % (outgoing_ip, outgoing_port)
        info += 'because: %s\n' % err
        log(info)
        return

      # Successfully opened a new connection.
      else:
        break


    log("Incoming connection from %s:%s using socket %s.\n" % (remoteip, remoteport, out_socket))

    # Exchange data between the two sockets.
    _DataForwarder(in_socket, out_socket)
    _DataForwarder(out_socket, in_socket)

  # end-closure

    
  # Return the local function.  
  return _threaded_function
      






class _DataForwarder:
  """
  A threaded class that forwards data from src_socket to dst_socket until either
  socket is closed.

  """

  def __init__(self, src_socket, dst_socket):

    self._src_socket = src_socket
    self._dst_socket = dst_socket

    createthread(self._threaded_function)

  


  def _threaded_function(self):
    """ A function that will be called in a thread. """

    # Forward until socket closed.
    while True:

      try:
        data_recv = block_call(self._src_socket.recv, BUFFER_SIZE)      
        #log('Forwarding', len(data_recv), 'bytes.\n')
        while data_recv:
          data_sent = block_call(self._dst_socket.send, data_recv)
          data_recv = data_recv[data_sent:]

      except (SocketClosedRemote, SocketClosedLocal):
        break

      # Terminate thread upon unhandled exceptions.
      except Exception, err:
        info = 'Unhandled exception while forwarding data:'
        log(info, str(err), '\n')
        log('src_socket:', self._src_socket, 'dst_socket:', self._dst_socket, '\n')
        break

    # Clean up
    self._src_socket.close()
    self._dst_socket.close()







def block_call(func, *p, **q):
  """
  Blocks the execution of the function until it exits without raising the
  SocketWouldBlockError. Returns the result of the function.

  """
  while True:
    try:
      return func(*p, **q)
    except SocketWouldBlockError:
      sleep(SLEEP_TIME)
    



      

def main():
  """
  <Purpose>

    Parses the command-line arguments. Listens for incoming connection.

  <Arguments>
    None.

  <Exceptions>
    None.

  <Return>
    None.

  """

  global outgoing_ip
  global outgoing_port
  global incoming_ip
  global incoming_port
  global affix_port
  global INCOMING_AFFIX_STACK_LIST

  try:

    outgoing_ip = sys.argv[1]
    outgoing_port = int(sys.argv[2])
    incoming_ip = sys.argv[3]
    incoming_port = int(sys.argv[4])
    affix_port = int(sys.argv[5])

    # The affix port must be either the outgoing or incoming port.
    if affix_port not in (outgoing_port, incoming_port):
      raise ValueError('The affix port must be either the outgoing or incoming port.')
    
  except (ValueError, IndexError), err:
    
    err_info = 'Bad command-line arguments: '
    err_info += USAGE
    log(err_info)

    return

  # The user may have optionally specified the affix stack string.
  try:
    INCOMING_AFFIX_STACK_LIST = [sys.argv[6]]
  except IndexError:
    pass

  start_server()





if __name__ == '__main__':
  main()





