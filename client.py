import socket

def client_program():
    '''TEST CODE 2
    servername = socket.gethostname()
    clientsocket = socket.socket()
    serverport = 5000
    clientsocket.connect((servername, serverport))
    ---insert URL FILTER HERE---
    sentence = input("Enter lowercase sentence:")
    clientsocket.send(sentence.encode())
    changed = clientsocket.recv(1024).decode()
    print("From server: ", changed)
    clientsocket.close()'''


if __name__ == '__main__':
    client_program()

    '''TEST CODE 1
    host = socket.gethostname()  # as both code is running on same pc
    port = 5000  # socket server port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server

    message = input(" -> ")  # take input

    while message.lower().strip() != 'bye':
        client_socket.send(message.encode())  # send message
        data = client_socket.recv(1024).decode()  # receive response

        print('Received from server: ' + data)  # show in terminal

        message = input(" -> ")  # again take input

    client_socket.close()  # close the connection'''


