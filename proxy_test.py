import socket
import sys
import threading
### 

#
## CONSTANTS
#
HOST_NAME = '127.0.0.1' #str(sys.argv[0]) #hostname eg. 127.0.0.1
LISTEN_PORT = 12345
PROXY_ADDR = (HOST_NAME, LISTEN_PORT)
BUFFER_SIZE = 8192
FORMAT = 'utf-8'
MAX_CONN = 10
TIMEOUT = 10000 #seconds
#SYS_EXIT_CODE = 0


def connect_to_url(client_socket, client_addr, request, dst_addr):
    try:
        #request_byte = request
        #request_str = request.decode(FORMAT) #decode byte obj to str
        
        #create connection to the webserver
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        remote_socket.settimeout(TIMEOUT)
        remote_socket.connect(dst_addr)
        remote_socket.sendall(request)
        
        while True:
            # receive data from web server
            web_data = remote_socket.recv(BUFFER_SIZE)
            
            if len(web_data) > 0:
                #web_data_byte = web_data
                #print("web_data_byte: ", web_data)
                web_data_str = web_data.decode(FORMAT) #decode byte obj to str
                print("web_data_str: ", web_data_str)
                
                client_socket.send(web_data) # send to browser/client
                print("Success! Internet data sent to client")
            else:
                break
        #close server connections
        #error handling
        remote_socket.close()
        client_socket.close()
        
    except socket.error as error:
        remote_socket.close()
        client_socket.close()
        print("NOPE2 remote socket not created...", error, "\n")
        sys.exit(2)
        



#function to handle each request to proxy
def handle_client(client_socket, client_addr, request):
    try:
        request_byte = request
        request_str = request.decode(FORMAT) #decode byte obj to str

        first_line = request_str.split('\n')[0]
        url = first_line.split(' ')[1]
        
        # string manipulation to find destination address = (destination_ip, destination_port)
        http_pos = url.find("://") # find pos of ://
        if (http_pos==-1):
            domain = url # 
        else:
            domain = url[(http_pos+3):] # get the rest of url after http(s)://123
        
        dst_port_pos = domain.find(":") # find the port number pos (if any)   
        dst_ip_pos = domain.find("/") # find end of web server
        
        if dst_ip_pos == -1:
            dst_ip_pos = len(domain)
        
        dst_ip = ""
        dst_port = -1
        #finding port and ip
        if (dst_port_pos == -1 or dst_ip_pos < dst_port_pos): # default port
            dst_port = 80 
            dst_ip = domain[:dst_ip_pos] 
        else: # specific port 
            dst_port = int((domain[(dst_port_pos+1):])[:dst_ip_pos-dst_port_pos-1])
            dst_ip = domain[:dst_port_pos]
        
        dst_addr = (dst_ip, dst_port)
        print("---Handling url: ", url)
        connect_to_url(client_socket, client_addr, request, dst_addr)
    except Exception as error:
        print("NOPE1 handling failed...", error)

    
    

"""
socket.getaddrinfo('localhost', 8080)

if len(sys.argv) <= 1:
    print ('Usage : "python proxy.py <HOST_NAME>"\n\
           [HOST_NAME : It is the IP Address Of Proxy Server')
    
    sys.exit(0)"""

def start_server():
      #create, bind, listen   
    try:
        proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy_socket.bind(PROXY_ADDR) #sockname.bind(addr), where addr = (host ip, port no)
    except Exception as error:
        print("Failed to create or bind socket.", str(error))
        sys.exit(0)
       
    try:
        proxy_socket.listen(MAX_CONN)
        print("Proxy server now online...")
    except KeyboardInterrupt:
        print("User requested an interrupt.")
        sys.exit(0)
    
    #accept client-proxy request
    while True:
        try:
            client_socket, client_addr = proxy_socket.accept() #receives client socket and address
            #dispatch request in a separate thread to improve performance
            request = client_socket.recv(BUFFER_SIZE) #inputs GET request, etc.
            print("\n--Received a connection request from: ", client_addr)
            #print("--request: ", request)
            thread = threading.Thread(target=handle_client, args=(client_socket, client_addr, request))
            thread.setDaemon(True)
            thread.start()
        except KeyboardInterrupt:
            print("Shutting down...")
            proxy_socket.close()
            sys.exit(1)
    proxy_socket.close()
        



#calling main function
if __name__ == "__main__":    
    start_server()