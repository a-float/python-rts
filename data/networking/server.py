import socket
import select
import threading
import sys
from dataclasses import dataclass
from typing import List, Optional, Dict
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

        self.socket_id_dict = {}
        self.host_socket = None
        self.clients: List[Optional[ClientData]] = [None] * 4
        self.read_list = [self.server_socket]
        self.running = True

    def get_client_count(self):
        return len(self.socket_id_dict)

    def _get_id(self):
        for i, v in enumerate(self.clients):
            if not v:
                return i

    def close(self):
        self.running = False
        print('SERVER IS BEING CLOSED')

    def send_to_all(self, data):
        for s in self.read_list:
            if s != self.server_socket:
                s.sendall(data)

    def _remove_client(self, sckt):
        self.clients[self.socket_id_dict[sckt]] = None
        del self.socket_id_dict[sckt]
        self.update_clients()

    def update_clients(self):
        print(self.clients)
        self.send_to_all(pickle.dumps({'players': self.clients}))

    def add_client(self, sckt, addr):
        new_id = self._get_id()
        self.clients[new_id] = ClientData(id=new_id+1, address=addr)
        self.socket_id_dict.update({sckt: new_id})
        print('socket_id_dict is now', self.socket_id_dict)
        self.read_list.append(sckt)
        sckt.sendall(str.encode(str(new_id+1)))
        self.update_clients()
        if self.host_socket is None:
            self.host_socket = sckt
        print("Connection from", addr)

    def change_map(self, diff):
        self.send_to_all(pickle.dumps({'map_change': diff}))

    @threaded
    def run(self):
        while self.running:
            print(self.running)
            sys.stdout.flush()
            readable, writable, errored = select.select(self.read_list, [], [], 1)
            for s in readable:
                if s is self.server_socket:
                    client_socket, address = self.server_socket.accept()
                    self.add_client(client_socket, address)
                else:
                    data = s.recv(1024)
                    print('SERVER RECEIVED ',data)
                    if data:
                        comms = data.decode().split(':')
                        if comms[0] == 'set_name':  # command "set_name:name" - sets the player name
                            self.clients[self.socket_id_dict[s]].name = comms[1]
                            self.update_clients()
                        if comms[0] == 'quit':  # command "quit" - player has quit
                            self.read_list.remove(s)
                            s.close()
                            self.remove_client(s)

                    else:
                        s.close()
                        self.read_list.remove(s)
        self.send_to_all(pickle.dumps('end'))
        print('The server has stopped')
