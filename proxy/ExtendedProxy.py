from socket import *
import re
import threading
import datetime

IP_ADDR = "192.168.188.139"
PORT= 13000

# Define a list of blacklisted domains 
BLACKLIST = [
    "moviedownload.com",
    "piratedmovie.com",
    "freemovie.com"
]

# Define a list of keywords to filter requests
KEYWORD = [
    "free download",
    "Free download",
    "pirated",
    "Pirated",
    "lottery",
    "Lottery",
    "Example"
]


# Create a tuple representing the address of the proxy server
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
            
            # Remove the response encoding from the request
            pattern = r"\bAccept-Encoding:[a-zA-Z0-9 ,]{1,}\r\n\b"

            # Replace the matched pattern with an empty string
            message = re.sub(pattern, "", message.decode("utf-8"))

            message = message.encode("utf-8")
            

            IP_ADDR = "192.168.188.139"
            PORT= 13000

            HostField = None
            # Extract host information from the request
            HostField = re.search('Host: (.)+(:[0-9]{1,5})?', message.decode()).group(0)[6:-1]

            httpsSeverPort = HostField[-3:]

            serverDomain = None

            try:

                IP_ADDR, PORT =  HostField.split(':')
                ADDR = (IP_ADDR,int(PORT))
                serverDomain = IP_ADDR

            except ValueError as e:

                serverDomain = HostField.replace("\r","")
                ADDR = (HostField.replace("\r",""),80)

            # Print client's information about request along with client's IP address and port number
            if(httpsSeverPort!= "443" ):
                print("ADDR ",clientAddr," Client want request of",HostField)

            # Log client's http requests and date to a CSV file
            if(httpsSeverPort!= "443" ):

                file  = open("stats.csv","a")

                today = datetime.date.today()

                data = f"{clientAddr[0]},{serverDomain},{today}\n" 
                file.write(data)
                file.close()


            # Check if the target domain is in the blacklist
            if (serverDomain in BLACKLIST):

                file = open("blacklist.html", "rb")
                payload = file.read()

                payload = payload.decode("utf-8")

                payload_size = len(payload)

                payload = "HTTP/1.1 200 OK\r\n" \
                +"Date: Sun, 22 Oct 2023 19:27:32 GMT\r\n" \
                +"Server:Created by Manan\r\n" \
                +"Last-Modified:Sat, 06 Oct 2018 08:00:43 GMT\r\n" \
                +"ETag: \"140c-5778ac8ef5adc\"\r\n" \
                +"Accept-Ranges: bytes\r\n" \
                +"Content-Length:"+ str(payload_size) +"\r\n" \
                +"Connection: close\r\n" \
                +"Cache-Control: no-store, no-cache, must-revalidate\r\n" \
                +"Content-Type: text/html\r\n\n" \
                +payload

                clientSocket.sendall(payload.encode('utf-8'))

                clientSocket.close()

                print("ADDR ",clientAddr," Client request of ",HostField," is blocked")

                return

            
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

                        # Receive data from the target server
                        payload = serverSocket.recv(104857)
                            

                        if not payload:
                            break

                        try:

                            
                            payload = payload.decode('utf8')

                            # Replace keywords in the response with asterisks
                            for i in KEYWORD:
                                payload = payload.replace(i,"*"*len(i))

                            clientSocket.sendall(payload.encode("utf-8"))

                        except UnicodeDecodeError:
                            # This case is for images, audio file which can't be decoded so no need to filtering
                            clientSocket.sendall(payload)

                    # Close the server connection
                    clientSocket.close()

                    # Close the server connection
                    serverSocket.close()

                    # Print the log which shows the server has successfully serve the client's http requests
                    if(httpsSeverPort!= "443" ):
                        print("ADDR ",clientAddr," Client request of ",HostField," is successfully completed")

                
                # timeout error is for if we don't receive the response from the server within time second
                except timeout:
                    # Close the server connection
                    clientSocket.close()

                    # Close the server connection
                    serverSocket.close()

                    if(httpsSeverPort!= "443" ):
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

        # start the thread using start function   
        thread.start()

# Handle KeyboardInterrupt to gracefully shut down the server
except KeyboardInterrupt:
    proxyServerSocket.close()
    print("KeyboardInterrupt occurred socket shutdown")
