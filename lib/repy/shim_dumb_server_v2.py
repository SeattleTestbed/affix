"""
<Program>
    shim_dumb_server_V2.repy

<Author>
    Monzur Muhammad
    monzum@cs.washington.edu

<Purpose>
    This will retrieve file from the apache http
    server, and return it to the requesting machine.
"""

import os
import sys
import time
import random

dy_import_module_symbols("shimstackinterface")


# The address and port of the outgoing connection.
localhost_name = "proxy_shim.zenodotus.cs.washington.edu"
server_address = "localhost"
server_port = 80

shim_port = -1
shim_string = "(NoopShim)"

# The max buffersize. The amount of data to send at a time.
buffer_size = 2**15 # 32KB


# Time to sleep if we block
SLEEP_TIME = 0.001




def start_server(myip, myport):
    """
    <Purpose>
        Launches a server that continuously waits for incoming connection.
        Once a connection is made, it launches a thread that handles the
        connection.

    <Arguments>
        myip - the ip address that the server should listen on.

        myport - the port the server should listen on.

    <Side Effects>
        None

    <Exception>
        None

    <Return>
        None
    """

    if myport == shim_port:
        print "Listening for connection on %s:%d" % (localhost_name, myport)
        print "Listening with shim_stack: " + shim_string
        shim_obj = ShimStackInterface(shim_string)
        tcp_server_socket = shim_obj.listenforconnection(myip, myport)
    else:
        print "Listening for connection on %s:%d" % (myip, myport)
        tcp_server_socket = listenforconnection(myip, myport)

    while True:
        try:
            (remoteip, remoteport, sockobj) = tcp_server_socket.getconnection()
            server_func = tcp_file_server_incoming(remoteip, remoteport, sockobj)
        
            # Launch a new thread to handle incoming connection.
            createthread(server_func)
        except (SocketWouldBlockError, SocketClosedLocal, ResourceExhaustedError):
            # Any exception we just continue on.
            time.sleep(SLEEP_TIME)





def tcp_file_server_incoming(remoteip, remoteport, sockobj):
    """
    <Purpose>
        This function is launched when there is any incoming messages
        from a client.

    <Arguments>
        remoteip - the ip address of the remote client.
        remoteport - the port of the remote client.
        sockobj - the socket object that will be used for communication.

    <Exceptions>
        None.

    <Return>
        None.
    """

    def _handle_incoming_connection():
        print "Incoming connection from: %s:%s" % (remoteip, remoteport)


        # Open a connection to the local server (apache, wget, firefox etc.)
        # to send the message.
        # Note that the localip and localport we provide won't be used, so I
        # chose a random port.
        print "Making connection to %s:%d" % (server_address, server_port)
        
        while True:
            try:
                if server_port == shim_port:
                    print "Creating outgoing connection with shim_stack: " + shim_string
                    shim_obj = ShimStackInterface(shim_string)
                    server_sockobj = shim_obj.openconnection(server_address, server_port, localhost_name, random.randint(4000,60000), 10)
                else:
                    server_sockobj = openconnection(server_address, server_port, localhost_name, random.randint(4000,60000), 10)
            except CleanupInProgressError:
                # We sleep if we get cleanup in progress.
                time.sleep(SLEEP_TIME)
            except TimeoutError:
                sockobj.close()
                return
            else:
                # Otherwise we continue.
                break

        outgoing_handle_func = tcp_file_server_outgoing(sockobj, server_sockobj)

        # Launch a listener thread that will handle all the messages that are incoming
        # from the local application server (apache, wget, firefox etc.)
        createthread(outgoing_handle_func)

        # We will send all incoming messages off to the server.
        # Note the reason we don't do server_sockobj.send(sockobj.recv())
        # is because we don't know which will raise the SocketWouldBlockError.
        while True:
            try:
                data_recv = sockobj.recv(buffer_size)
                while data_recv:
                    try:
                        data_sent = server_sockobj.send(data_recv)
                        data_recv = data_recv[data_sent:]
                    except SocketWouldBlockError:
                        time.sleep(SLEEP_TIME)

            except SocketWouldBlockError:
                time.sleep(SLEEP_TIME)
            except (SocketClosedLocal, SocketClosedRemote):
                # This will occur if either the server side or the 
                # client side closes a connection.
                break


        # Close the socket object now that we are done sending the
        # data back to the client.
        try:
            sockobj.close()
            server_sockobj.close()
        except:
            pass

        print "Transfered data to %s:%s" % (remoteip, remoteport)  

        
    # Return the local function.    
    return _handle_incoming_connection
            





def tcp_file_server_outgoing(sockobj, server_sockobj):
    """
    <Purpose>
        This thread is for forwarding any incoming message
        from the server back to the client.

    <Arguments>
        sockobj - the socket object for the client.
        server_sockobj - the socket object for the server.

    <Side Effects>
        None

    <Exceptions>
        None

    <Return>
        None
    """
        

    def _handle_outgoing_connection():
        # We will now receive the response from the server
        # and forward them back to the client.
        # Note the reason we don't do server.send(server_sockobj.recv())
        # is because we don't know which will raise the SocketWouldBlockError.
        while True:
            try:
                data_recv = server_sockobj.recv(buffer_size)
                while data_recv:
                    try:
                        data_sent = sockobj.send(data_recv)
                        data_recv = data_recv[data_sent:]
                    except SocketWouldBlockError:
                        time.sleep(SLEEP_TIME)

            except SocketWouldBlockError:
                time.sleep(SLEEP_TIME)
            except (SocketClosedLocal, SocketClosedRemote):
                # This will occur if either the server side or the
                # client side closes a connection after they have 
                # sent all the data.
                break
    
    
        # Close the socket object now that we are done sending the
        # data back to the client.
        try:
            sockobj.close()
            server_sockobj.close()
        except:
            pass


    return _handle_outgoing_connection


        



            

def main():
    """
    <Purpose>
        This is the main of the function. It launches a 
        tcp client to connect to local apache server and
        then retrieve a file. It also has a server to 
        listen for incoming connections from the client
        version of this program.

    <Arguments>
        None.

    <Exceptions>
        None.

    <Return>
        None.
    """


    if len(sys.argv) < 6:
        usage()


    global localhost_name
    global server_address
    global server_port
    global shim_port
    global shim_string

    # Specify the server address and port
    server_address = sys.argv[1]
    server_port = int(sys.argv[2])
    # Specify the TCP port to listen on. 
    localhost_name = sys.argv[3]
    incoming_connection_port = int(sys.argv[4])
    shim_port = int(sys.argv[5])

    if shim_port != -1:
        if len(sys.argv) < 7:
            print "If shim_port is provided (not -1), then shim_string must also be provided."
            usage()
        shim_string = sys.argv[6]
                         
    print "Starting shim proxy"
    start_server(localhost_name, incoming_connection_port)





def usage():
    message = "Usage:\n\tpython shim_apache_client.repy server_addr server_port listening_addr listening_port shim_port [shim_string]"
    print message
    sys.exit()


if callfunc == 'initialize':
    main()





