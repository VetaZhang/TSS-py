import time
import json
from threading import Thread
from socket import *

class TcpServer():
    def __init__(self, store = {}, action = {}):
        self.__server = None
        self.__clients = {}
        self.__store = store
        self.__action = action
        self.__threads = {}
        Thread(target=self.run, args=(8080,)).start()

    def run(self, port):
        self.__server = socket(AF_INET, SOCK_STREAM)
        self.__server.bind(('localhost', port))
        self.__server.listen(5)
        print('server start')
        while True:
            client, addr = self.__server.accept()
            id = str(int(time.time()))
            print('client connected, id: ', id)
            self.__clients[id] = client
            self.__threads[id] = Thread(target=self.handleClient, args=(id,))
            self.__threads[id].start()

    def handleClient(self, id):
        while True:
            rowData = self.__clients[id].recv(1024)
            if not rowData:
                break
            data = json.loads(str.decode(rowData))
            data['clientId'] = id
            print(data)
            #handle action
            if data['command'] in self.__action:
                self.__action[data['command']](data)
        self.__clients[id].close()
        print('client closed, id: ', id)

    def set(self, key, value, method = "default"):
        if key in self.__store.keys():
            self.__store[key] = {
                'default': lambda x: x
            }[method](value)
            data = str.encode(json.dumps({
                'key': key,
                'value': value,
                'method': method
            }))
            print(data)
            for id in self.__clients.keys():
                self.__clients[id].send(data)
