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
server_address = "localhost"
server_port = 80

shim_port = -1
shim_string = "(NoopShim)"

# The max buffersize. The amount of data to send at a time.
buffer_size = 2**15 # 32KB


# Time to sleep if we block
SLEEP_TIME = 0.001

in_file_name = "incoming_time_data.txt"
out_file_name = "outgoing_time_data.txt"

in_file_object = None
out_file_object = None
in_offset = 0
out_offset = 0

# How often to sample data
SAMPLE_INTERVAL = 0.1



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

    global in_file_object
    global out_file_object
    global in_offset
    global out_offset

    in_file_object = openfile(in_file_name, True)
    out_file_object = openfile(out_file_name, True)

    in_offset = _find_file_location(in_file_object)
    out_offset = _find_file_location(out_file_object)

    print "Listening for connection on %s:%d" % (myip, myport)
    if myport == shim_port:
        print "Listening with shim_stack: " + shim_string
        shim_obj = ShimStackInterface(shim_string)
        tcp_server_socket = shim_obj.listenforconnection(myip, myport)
    else:
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


    in_file_object.close()
    out_file_object.close()




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

        global in_offset
        start_msg = "\n===Start===\n"
        in_file_object.writeat(start_msg, in_offset)
        in_offset += len(start_msg)


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
                    server_sockobj = shim_obj.openconnection(server_address, server_port, getmyip(), int(random.random() * 30000 + 10000), 10)
                else:
                    server_sockobj = openconnection(server_address, server_port, getmyip(), int(random.random() * 30000 + 10000), 10)
            except CleanupInProgressError:
                # We sleep if we get cleanup in progress.
                time.sleep(SLEEP_TIME)
            else:
                # Otherwise we continue.
                break

        outgoing_handle_func = tcp_file_server_outgoing(sockobj, server_sockobj)

        # Launch a listener thread that will handle all the messages that are incoming
        # from the local application server (apache, wget, firefox etc.)
        createthread(outgoing_handle_func)

        start_time = getruntime()
        cur_time = start_time
        lastsample = cur_time + SAMPLE_INTERVAL
        total_data = 0
        # We will send all incoming messages off to the server.
        # Note the reason we don't do server_sockobj.send(sockobj.recv())
        # is because we don't know which will raise the SocketWouldBlockError.
        while True:
            try:
                data_recv = sockobj.recv(buffer_size)
                
                # This is the case where we are listening with a shim port.
                if server_port != shim_port:
                    total_data += len(data_recv)
                    curtime = getruntime()
                    # We want to check if enough time has passed for us to 
                    # sample data again.
                    if (curtime - lastsample) > SAMPLE_INTERVAL:
                        msg = "%.4f\t%d\tR\n" % ((curtime-start_time), total_data)
                        lastsample = curtime
                        in_file_object.writeat(msg, in_offset)
                        in_offset += len(msg)


                while data_recv:
                    try:
                        data_sent = server_sockobj.send(data_recv)
                        data_recv = data_recv[data_sent:]
                        
                        # This is the case where we are sending with a shim port.
                        if server_port == shim_port:
                            print "got here"
                            total_data += data_sent
                            curtime = getruntime()
                            # We want to check if enough time has passed for us to
                            # sample data again.
                            if (curtime - lastsample) > SAMPLE_INTERVAL:
                                msg = "%.4f\t%d\tS\n" % ((curtime-start_time), total_data)
                                lastsample = curtime
                                in_file_object.writeat(msg, in_offset)
                                in_offset += len(msg)


                    except SocketWouldBlockError:
                        time.sleep(SLEEP_TIME)

                        if server_port == shim_port:
                            curtime = getruntime()
                            # We want to check if enough time has passed for us to
                            # sample data again.
                            if (curtime - lastsample) > SAMPLE_INTERVAL:
                                msg = "%.4f\t%d\tS\n" % ((curtime-start_time), total_data)
                                lastsample = curtime
                                in_file_object.writeat(msg, in_offset)
                                in_offset += len(msg)

            except SocketWouldBlockError:
                time.sleep(SLEEP_TIME)
                
                if server_port != shim_port:
                    curtime = getruntime()
                    # We want to check if enough time has passed for us to
                    # sample data again.
                    if (curtime - lastsample) > SAMPLE_INTERVAL:
                        msg = "%.4f\t%d\tR\n" % ((curtime-start_time), total_data)
                        lastsample = curtime
                        in_file_object.writeat(msg, in_offset)
                        in_offset += len(msg)
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
        global out_offset

        start_msg = "\n===Start===\n"
        out_file_object.writeat(start_msg, out_offset)
        out_offset += len(start_msg)

        start_time = getruntime()
        cur_time = start_time
        lastsample = cur_time + SAMPLE_INTERVAL
        total_data = 0


        # We will now receive the response from the server
        # and forward them back to the client.
        # Note the reason we don't do server.send(server_sockobj.recv())
        # is because we don't know which will raise the SocketWouldBlockError.
        while True:
            try:
                data_recv = server_sockobj.recv(buffer_size)
                # This is the case where we are listening with a shim port.
                if server_port == shim_port:
                    total_data += len(data_recv)
                    curtime = getruntime()
                    # We want to check if enough time has passed for us to
                    # sample data again.
                    if (curtime - lastsample) > SAMPLE_INTERVAL:
                        msg = "%.4f\t%d\tR\n" % ((curtime-start_time), total_data)
                        lastsample = curtime
                        out_file_object.writeat(msg, out_offset)
                        out_offset += len(msg)

                while data_recv:
                    try:
                        data_sent = sockobj.send(data_recv)
                        data_recv = data_recv[data_sent:]

                        # This is the case where we are sending with a shim port.
                        if server_port != shim_port:
                            total_data += data_sent
                            curtime = getruntime()
                            # We want to check if enough time has passed for us to
                            # sample data again.
                            if (curtime - lastsample) > SAMPLE_INTERVAL:
                                msg = "%.4f\t%d\tS\n" % ((curtime-start_time), total_data)
                                lastsample = curtime
                                out_file_object.writeat(msg, out_offset)
                                out_offset += len(msg)

                    except SocketWouldBlockError:
                        time.sleep(SLEEP_TIME)
                        if server_port != shim_port:
                            curtime = getruntime()
                            # We want to check if enough time has passed for us to
                            # sample data again.
                            if (curtime - lastsample) > SAMPLE_INTERVAL:
                                msg = "%.4f\t%d\tS\n" % ((curtime-start_time), total_data)
                                lastsample = curtime
                                out_file_object.writeat(msg, out_offset)
                                out_offset += len(msg)


            except SocketWouldBlockError:
                time.sleep(SLEEP_TIME)
                if server_port == shim_port:
                    curtime = getruntime()
                    # We want to check if enough time has passed for us to
                    # sample data again.
                    if (curtime - lastsample) > SAMPLE_INTERVAL:
                        msg = "%.4f\t%d\tR\n" % ((curtime-start_time), total_data)
                        lastsample = curtime
                        out_file_object.writeat(msg, out_offset)
                        out_offset += len(msg)

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





def _find_file_location(file_obj):
    """
    Find out where to write in a file. Returns the offset of the file.
    """

    min = 0
    max = 10 * 1024 * 1024 * 1024 # Assume that the max file size is 1 GB

    while min <= max :
      mid = (min + max) / 2
      try:
        file_obj.readat(1, mid)
      except SeekPastEndOfFileError:
        # If we got an error that means we are seeking past file size,
        # so the file size is smaller then mid.
        max = mid - 1
      else:
        # If we did not get an error, then the file is bigger then size mid.
        min = mid + 1

    # We may get out of the loop in two different cases, and we have to check
    # if we found the right mid, or just one over.
    try:
      file_obj.readat(1, mid)
    except SeekPastEndOfFileError:
      return mid - 1
    else:
      return mid
        



            

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


    if len(sys.argv) < 5:
        usage()


    global server_address
    global server_port
    global shim_port
    global shim_string

    # Specify the server address and port
    server_address = sys.argv[1]
    server_port = int(sys.argv[2])
    # Specify the TCP port to listen on.
    incoming_connection_port = int(sys.argv[3])
    shim_port = int(sys.argv[4])

    if shim_port != -1:
        if len(sys.argv) < 6:
            print "If shim_port is provided (not -1), then shim_string must also be provided."
            usage()
        shim_string = sys.argv[5]
                         
    print "Starting shim proxy"
    start_server(getmyip(), incoming_connection_port)





def usage():
    message = "Usage:\n\tpython shim_apache_client.repy server_addr server_port listening_port shim_port [shim_string]"
    print message
    sys.exit()


if callfunc == 'initialize':
    main()





