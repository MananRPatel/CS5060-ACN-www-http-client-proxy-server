from socket import *
import re
from enum import Enum
import threading

IP_ADDR = "192.168.188.139"
PORT = 12000
ADDR = (IP_ADDR,PORT)

# Define an enumeration for file types
class TYPE(Enum):
    FILE = 1
    IMG = 2


serverSocket = None

try:

    # Create a TCP socket
    # Notice the use of SOCK_STREAM for TCP packets
    serverSocket = socket(AF_INET, SOCK_STREAM)

    # Create Port reusable socket
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    # Assign IP address and port number to socket
    serverSocket.bind(ADDR)
    

    serverSocket.listen()

    # Function to handle file requests based on file type and return the payload with http header
    def fileHandler_local(fileName):

        fT = fileName[-1]

        if fT == "l" or fT == "/"  : fileType = "text/html"
        elif fT == "s" : fileType = "text/css"
        elif fT == "g" : fileType = "image/jpg"
        elif fT == "f" : fileType = "image/gif"
        elif fT == "o" : fileType = "image/x-icon"

        foundOrNot = None

        responseCode = None
        try:

            if(fileName == "/"): file = open("index.html","rb")
            else :file = open(fileName[1:], "rb")
            foundOrNot = True
            responseCode = "HTTP/1.0 200 OK"

        except FileNotFoundError as e:
            file = open("404.html", "rb")
            foundOrNot = False
            responseCode = "HTTP/1.0 404 Not Found"

        # Read the html file
        payload = file.read() 

        # close the file manager
        file.close()

        payload_size = len(payload)


        if fT == "l" or fT == "s":
            payload = payload.decode("utf-8")
            payload = responseCode+"\r\n" \
            +"Date: Sun, 22 Oct 2023 19:27:32 GMT\r\n" \
            +"Accept-Ranges: bytes\r\n" \
            +"Content-Length:"+ str(payload_size) +"\r\n" \
            +"Connection: close\r\n" \
            +"Cache-Control: no-store, no-cache, must-revalidate\r\n" \
            +"Content-Type: "+fileType+"\r\n\n" \
            +payload
            return (TYPE.FILE,payload,foundOrNot)
        
        else: 
            # For image files, prepare the response headers and payload separately
            payload_header = responseCode+"\r\n" \
            +"Date: Sun, 22 Oct 2023 19:27:32 GMT\r\n" \
            +"Accept-Ranges: bytes\r\n" \
            +"Cache-Control: no-store, no-cache, must-revalidate\r\n" \
            +"Content-Length:"+ str(payload_size) +"\r\n" \
            +"Connection: close\r\n" \
            +"Content-Type: "+fileType+"\r\n\n"

            return (TYPE.IMG,(payload_header,payload),foundOrNot)




    def HandleRequest(clientSocket,clientAddr):
                
        # get GET request from clients
        message = clientSocket.recv(104857)

        print(message.decode('utf-8'))

        # Use regular expressions to extract the requested file name
        m = re.search('^GET \/[a-zA-Z0-9\.%\/]{1,}', message.decode("utf-8"))
        if m:
            found = m.group(0)
 
        # Extract the file name from the GET request
        try:
            fileName = found[4:]
        except Exception:
        
            try:
            
            	print("test code")
            	m = re.search('GET http:\/\/[a-zA-Z0-9\.:%\/]{1,}', message.decode("utf-8")).group(0)
            	fileName=m[32:]

            
            except:
                fileName= '/'

        print("ADDR ",clientAddr," Client want request of ",fileName)

        # info_payload is used for get payload along with information
        info_Payload = fileHandler_local(fileName)

        # check file type to send payload according to client
        if info_Payload[0] == TYPE.FILE:
            #send the payload to the client
            clientSocket.sendall(info_Payload[1].encode("utf-8"))
        
        else:
            clientSocket.sendall(info_Payload[1][0].encode("utf-8")+info_Payload[1][1])

        # Close the client connection
        clientSocket.close()

        
        if(info_Payload[2]):
            print("ADDR ",clientAddr,f" Client request {fileName} is served")
        else:
            print("ADDR ",clientAddr,f" Client request {fileName} is not found")


    print("PORT: ",ADDR)


    while True:

            # Accept a connection from a client
            clientSocket,clientAddr = serverSocket.accept()
            # Create a thread to handle the multiple connection
            print("ADDR ",clientAddr," Client want request of ")
            thread = threading.Thread(target=HandleRequest,args=(clientSocket,clientAddr))

            # start the tread using start function   
            thread.start()


# Handle KeyboardInterrupt to gracefully shut down the server  
except Exception as e:
    print(e)
    serverSocket.close()
    print("KeyboardInterrupt occurred socket shutdown")

