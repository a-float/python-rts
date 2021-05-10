import socket
import select
import threading
import sys
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ClientData:
    """Class for storing basic client data."""
    id: int
    socket: socket
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
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', 5555))
        self.server_socket.listen(4)
        print("Listening on port 5555")

        self.clients: List[Optional[ClientData]] = [None] * 4
        self.client_count = 0
        self.read_list = [self.server_socket]
        self.running = True

    def close(self):
        self.running = False

    @threaded
    def run(self):
        while self.running:
            sys.stdout.flush()
            readable, writable, errored = select.select(self.read_list, [], [], 1)
            for s in readable:
                if s is self.server_socket:
                    client_socket, address = self.server_socket.accept()
                    new_id = self.client_count + 1
                    client_socket.sendall(str.encode(str(new_id)))
                    self.clients[self.client_count] = ClientData(id=new_id, socket=client_socket, address = address)
                    self.client_count += 1
                    self.receiver.render_players(self.clients)
                    self.read_list.append(client_socket)
                    print("Connection from", address)
                else:
                    data = s.recv(1024)
                    if data:
                        comms = data.decode().split(':')
                        if comms[0] == 'set_name':  # command "set_name:id:name" - sets the player name
                            self.clients[int(comms[1])] = comms[2]
                            self.receiver.render_players(self.clients)
                    else:
                        s.close()
                        self.read_list.remove(s)
        print('The server has stopped')
