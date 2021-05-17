import socket
import select
import threading
import sys
from dataclasses import dataclass
from typing import List, Optional
import pickle


@dataclass
class ClientData:
    """Class for storing basic client data."""
    id: int
    name: str = 'Joe'
    address: str = '???'


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


class Server:
    def __init__(self, receiver):
        self.receiver = receiver
        self.ip = '127.0.0.1'
        self.port = 5555
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(4)
        print(f"Listening on {self.ip} : {self.port}")

        self.clients: List[Optional[ClientData]] = [None] * 4
        self.read_list = [self.server_socket]
        self.running = True

    def get_id(self):
        for i, v in enumerate(self.clients):
            if not v:
                return i

    def close(self):
        self.running = False

    def send_to_all(self, data):
        for s in self.read_list:
            if s != self.server_socket:
                s.sendall(data)

    def remove_client(self, client_id):
        self.clients[client_id - 1] = None
        self.update_clients()

    def update_clients(self):
        print(self.clients)
        self.send_to_all(pickle.dumps({'players': self.clients}))

    def change_map(self, diff):
        self.send_to_all(pickle.dumps({'map_change': diff}))

    @threaded
    def run(self):
        while self.running:
            sys.stdout.flush()
            readable, writable, errored = select.select(self.read_list, [], [], 1)
            for s in readable:
                if s is self.server_socket:
                    client_socket, address = self.server_socket.accept()
                    new_id = self.get_id()
                    print('new id is ', new_id)
                    self.clients[new_id] = ClientData(id=new_id+1, address=address)
                    client_socket.sendall(str.encode(str(new_id+1)))
                    self.update_clients()
                    self.read_list.append(client_socket)
                    print("Connection from", address)
                else:
                    data = s.recv(1024)
                    if data:
                        comms = data.decode().split(':')
                        if comms[0] == 'set_name':  # command "set_name:id:name" - sets the player name
                            self.clients[int(comms[1])-1].name = comms[2]
                            self.update_clients()
                        if comms[0] == 'quit':  # command "quit:id" - player has quit
                            self.remove_client(int(comms[1])-1)
                            s.close()
                            self.read_list.remove(s)
                    else:
                        s.close()
                        self.read_list.remove(s)
        print('The server has stopped')