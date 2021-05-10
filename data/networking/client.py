import socket
import pickle
from _thread import *
from data.states.online_game import OnlineGame


class Client:
    def __init__(self, name):
        # self.game: OnlineGame = game
        self.name: str = name
        self.socket: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr: (str, int) = ("192.168.56.1", 5555)
        self.player_id = self.connect()
        if self.player_id:
            start_new_thread(threaded_client, (self.socket, print))

    def close(self):  # TODO implement it. Maybe make it a runnable class?
        pass

    def get_player_id(self):
        return self.player_id

    def connect(self):
        try:
            self.socket.connect(self.addr)
            print('Connected to addr ', self.addr)
            res = self.socket.recv(2048).decode()
            self.socket.sendall(str.encode(f'set_name:{self.player_id}:{self.name}'))
            return res
        except:
            pass

    def send(self, data):
        try:
            if type(data) == str:
                print(f'sending a string: {data}')
                self.socket.send(str.encode(data))
            else:
                print(f'sending an object: {data}')
                self.socket.send(pickle.dumps(data))
        except socket.error as e:
            print(e)


def threaded_client(conn, send_event):
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            else:
                send_event(pickle.loads(data))
        except:
            break

    print("Lost connection to the server")
    conn.close()
