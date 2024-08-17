from socket import *
import re
import threading

IP_ADDR = "192.168.188.139"
PORT = 13000

ADDR = (IP_ADDR,PORT)

print("Proxy server test listening on ", ADDR)

# Create a TCP socket
# Notice the use of SOCK_STREAM for TCP packets
proxyServerSocket = socket(AF_INET, SOCK_STREAM)
proxyServerSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
proxyServerSocket.bind(ADDR)
proxyServerSocket.listen(100)
    
try:  
    # Define a function to handle client connections
    def fnConnectClients(clientSocket,clientAddr):

        try:  

            # Receive the client's request with buffer size of 104857 bytes
            message = clientSocket.recv(104857)

             # If there is no message available then break out of the loop
            if not message : 
                return 
            
            IP_ADDR = "192.168.188.139"
            PORT= 13000
      



            HostField = None
            # Extract host information from the request
            HostField = re.search('Host: (.)+(:[0-9]{1,5})?', message.decode()).group(0)[6:-1]

            httpsSeverPort = HostField[-3:]

             # Print client's information about request along with client's IP address and port number
            if(httpsSeverPort!= "443" ):
                print("ADDR ",clientAddr," Client want request of ",HostField)

            try:
                IP_ADDR, PORT =  HostField.split(':')
                ADDR = (IP_ADDR,int(PORT))
            except ValueError as e:
                ADDR = (HostField.replace("\r",""),80)

            # Establish a connection to the target server
            serverSocket = socket(AF_INET,SOCK_STREAM)

            # connect proxy to the server with the specified IP address and port

            try:
                serverSocket.connect(ADDR)
            # send the client message to the server
            except Exception as e:
                print("ADDR ",clientAddr," error ",e)
            serverSocket.sendall(message)

            serverSocket.settimeout(5)


            payload = None


            # this while loop is for getting the response from the server and after sending request
            while True:

                # try block for if packet is not received then handle the error
                try:

                    while True:

                        payload = serverSocket.recv(104857)

                        if not payload:
                            break

                        clientSocket.sendall(payload)

                    # Print the log which shows the server has successfully serve the client's http requests
                    if(httpsSeverPort!= "443" ):
                        print("ADDR ",clientAddr," Client request of ",HostField," is successfully completed")

                    # Close the client connection
                    clientSocket.close()

                    # Close the server connection
                    serverSocket.close()

                
                # timeout error is for if we don't receive the response from the server within time second
                except timeout:
                    if(HostField[-3:]!= "443" ):
                        clientSocket.close()
                        serverSocket.close()
                        # Print the log which shows the server has successfully serve the client's http requests
                        print("ADDR ",clientAddr," Client request of ",HostField," is successfully completed")
                        break
                    pass

        # This exception majorly occurs for the https request will trying to reset the connection
        except ConnectionResetError as e:
            if(httpsSeverPort!= "443" ):
                print("Connection reset for Host ",HostField)

    while True:

        # Accept a connection from a client
        clientSocket,clientAddr = proxyServerSocket.accept()

        # Create a thread to handle the multiple connection
        thread = threading.Thread(target=fnConnectClients,args=(clientSocket,clientAddr))

        # start the tread using start function   
        thread.start()

# Handle KeyboardInterrupt to gracefully shut down the server
except KeyboardInterrupt:
    proxyServerSocket.close()
    print("KeyboardInterrupt occurred socket shutdown")
