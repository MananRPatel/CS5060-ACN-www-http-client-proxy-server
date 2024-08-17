from socket import *
from enum import Enum
import re
import threading
import sys
      
lock = threading.Lock()

def saveImgs(file_name, data):
    with lock:
        try:
            image = data.split(b"\r\n\n")
            with open(file_name, "wb") as f:
                f.write(image[1])
            print(f"Image successfully written to {file_name}")
        except Exception as e:
            print(f"Error writing image to {file_name}: {e}")


class HTTP():

    ADDR =None
    clientSocket = None

    
    def __init__(self,ADDR):

        self.ADDR = ADDR

        # establish the TCP socket connection
        self.clientSocket = socket(AF_INET,SOCK_STREAM)
        # connect client to the server with the specified IP address and port
        self.clientSocket.connect(self.ADDR)
        



    def GET_request(self,format):
        # send packet to server with sendall function because the sendall function is good for error handling
        print(format)
        self.clientSocket.sendall(format.encode("utf-8"))

        # set timeout to 1 second for request timeout 
        self.clientSocket.settimeout(1)

        return self.GET_response(type)


    def GET_response(self,type):

        # declare the data which captures server response
        data = None

        # this while loop is for getting the response from the server and after sending and retransmitting
        while True:

            # try block for if packet is not received then handle the error
            try:

                data = self.clientSocket.recv(104857600) # 100*2^20Byte = 100MB message size

                # break is for because we know that we don't need for retransmission
                break
            
            # timeout error is for if we don't receive the response from the server within time second
            except timeout:
                pass
      
        return data
	
    def send_request(self,hostname,path):

        http_structure = f"""GET {path} HTTP/1.0\r\nHost: {hostname}\r\n\r\n"""
           
        return self.GET_request(http_structure)
    

# Function to extract referenced objects from HTML file        
def extract_referenced_objects(data):
        
        href_regex = r'<link\s+[^>]*\bhref=["\'](.*?)["\']'
	
        href_references = re.findall(href_regex, data)
	
        print("Link references: ",href_references)
    
        src_regex = r'<img[^>]*\bsrc=["\'](.*?)["\']'
    	
        src_references = re.findall(src_regex, data)
	
        print("Image references: ",src_references)
        
        for obj in href_references:

            httpObj = HTTP(ADDR)
            
            data = httpObj.send_request(server_ip_address+":"+server_port_number,"/"+obj)
            
            print(data.decode('utf-8'))
            
        for obj in src_references:
            httpObj = HTTP(ADDR)
            print(f"\n\n{obj}\n\n")
            data =  httpObj.send_request(server_ip_address+":"+server_port_number,"/"+obj)

            thread = threading.Thread(target=saveImgs,args=(obj[7:],data))
 
            thread.start()
            thread.join()
    
# server ip address
IP_ADDR = "127.0.0.1"
PORT = 12000
PATH = "index.html"

# Check command-line arguments for server information and file path
if len(sys.argv) == 4:
    server_ip_address = sys.argv[1]
    server_port_number = sys.argv[2]
    path_of_file = sys.argv[3]
    IP_ADDR = server_ip_address
    PORT = int(server_port_number)
    PATH = path_of_file

elif len(sys.argv) == 6:
    proxy_ip_address = sys.argv[1]
    proxy_port_number = sys.argv[2]
    server_ip_address = sys.argv[3]
    server_port_number = sys.argv[4]
    path_of_file = sys.argv[5]
    IP_ADDR = proxy_ip_address
    PORT = int(proxy_port_number)
    PATH = path_of_file


else:
    print("Invalid arguments!")
    sys.exit(1)
    
ADDR = (IP_ADDR,PORT)

httpObj = HTTP(ADDR)

data = httpObj.send_request(server_ip_address+":"+server_port_number,PATH)

print(data.decode('utf-8'))

extract_referenced_objects(data.decode('utf-8'))
