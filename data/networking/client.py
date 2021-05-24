import socket
import pickle
from _thread import *


class Client:
    def __init__(self, receiver, name: str, ip: str = '127.0.0.1'):
        self.receiver = receiver
        self.name: str = name
        self.ip = ip if ip != '' else '127.0.0.1'
        self.socket: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr: (str, int) = (self.ip, 5555)
        self.player_id = self.connect()
        self.running = False
        if self.player_id:
            self.running = True
            start_new_thread(threaded_client, (self.socket, lambda: self.running, lambda: self.receiver))

    def close(self):  # TODO implement it. Maybe make it a runnable class?
        self.send(f'quit')
        self.running = False

    def get_player_id(self):
        return self.player_id

    def connect(self):
        try:
            print('Connecting to address ', self.addr)
            self.socket.settimeout(3)
            self.socket.connect(self.addr)
            self.socket.settimeout(None)
            print('Connected to address ', self.addr)
            player_id = self.socket.recv(2048).decode()
            print(f'received id {player_id}')
            self.socket.sendall(str.encode(f'set_name:{self.name}'))
            return player_id
        except Exception as e:
            print('Failed to connect to the server ', e)
            return None

    def send(self, data):
        try:
            if type(data) == str:  # TODO always pickle
                print(f'sending a string: {data}')
                self.socket.send(str.encode(data))
            else:
                print(f'sending an object: {data}')
                self.socket.send(pickle.dumps(data))
        except socket.error as e:
            print(e)


def threaded_client(conn, is_running, receiver):
    while is_running():
        try:
            data = conn.recv(4096*2)
            if not data:
                break
            else:
                data = (pickle.loads(data))
                receiver().handle_message(data)
        except Exception as e:
            print("Something went wrong ", e)
            break

    print("Lost connection to the server")
    conn.close()
