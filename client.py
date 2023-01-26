import socket
import protocol

BUFFER = 1024

class Network:
    def __init__(self) -> None:
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.hostname = socket.gethostname()
        self.server = socket.gethostbyname(self.hostname)
        self.port = 5608
        self.addr = (self.server, self.port)
        self.connect()
        protocol.client_handshake(self.client)
        self.currentId = protocol.recv(self.client)
        self.board = protocol.recv(self.client)


    def connect(self):
        self.client.connect(self.addr)
    
    
    def disconnct(self):
        self.client.close()
    

    
