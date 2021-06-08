import socket
import select
import threading
import sys
from dataclasses import dataclass
from typing import List, Optional
import pickle
import time


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
        self.ip = ''
        self.port = 5555
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(4)
        print(f"Listening on {self.ip} : {self.port}")

        self.socket_id_dict = {}  # maps sockets to clients ids
        self.host_socket = None
        self.clients: List[Optional[ClientData]] = [None] * 4
        self.read_list = [self.server_socket]
        self.running = True
        self.last_state_update = 0
        self.state_update_delay = 0.5  # in s
        self.state_source = None  # packable object whose state is going to be shared among the players

    def set_state_source(self, packable, update_delay=0.5):
        self.state_source = packable
        self.state_update_delay = update_delay

    def get_client_count(self):
        return len(self.socket_id_dict)

    def _get_available_id(self):
        for i, v in enumerate(self.clients):
            if not v:
                return i

    def close(self):
        self.running = False

    def send_to_clients(self, data):
        for s in self.read_list:
            if s != self.server_socket:
                s.sendall(data)

    def _remove_client(self, sckt):
        self.clients[self.socket_id_dict[sckt]] = None
        # print(self.clients)
        del self.socket_id_dict[sckt]

    def add_client(self, sckt, addr):
        new_id = self._get_available_id()
        self.clients[new_id] = ClientData(id=new_id+1, address=addr)
        self.socket_id_dict.update({sckt: new_id})
        self.read_list.append(sckt)
        sckt.sendall(str.encode(str(new_id+1)))
        self.send_state()
        if self.host_socket is None:
            self.host_socket = sckt
        print("Connection from", addr)

    def send_state(self):
        # print("SERVER sending state")
        self.last_state_update = time.time()
        self.send_to_clients(pickle.dumps(('state', self.state_source.pack())))

    @threaded
    def run(self):
        while self.running:
            if time.time() > self.last_state_update + self.state_update_delay:
                self.send_state()
            sys.stdout.flush()
            readable, writable, errored = select.select(self.read_list, [], [], 1)
            for s in readable:
                if s is self.server_socket:
                    client_socket, address = self.server_socket.accept()
                    self.add_client(client_socket, address)
                else:
                    data = s.recv(1024)
                    if data:
                        comms = data.decode().split(':')
                        if comms[0] == 'set_name':  # command "set_name:name" - set the player's name
                            self.clients[self.socket_id_dict[s]].name = comms[1]
                        elif comms[0] == 'quit':  # command "quit" - player has quit
                            self._remove_client(s)
                            s.close()
                            self.read_list.remove(s)
                        elif comms[0] == 'action':  # command "action: command_name"-player has performed an action
                            payload = ('action', self.socket_id_dict[s]+1, comms[1])
                            self.state_source.handle_message(payload)
                        self.send_state()  # send state after receiving a message
                    else:
                        s.close()
                        self.read_list.remove(s)

        self.server_socket.close()
        print('The server has stopped')
