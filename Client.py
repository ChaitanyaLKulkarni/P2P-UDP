import socket
import random
import threading
import logging
import time
import json

from config import (BUFFER_SIZE, HEARTBEAT, EXPIRIES,
                    RAND_MIN, RAND_MAX, getStr, getIp)

logging.basicConfig(level=logging.INFO)


class Client:
    def __init__(self, serverHost="127.0.0.1", serverPort=55000, host="127.0.0.1", port=None):
        if port is None:
            port = random.randint(RAND_MIN, RAND_MAX)

        self.address = (host, port)
        self.serverAddr = (serverHost, serverPort)

        try:
            self.sock = socket.socket(socket.AF_INET,
                                      socket.SOCK_DGRAM)
            self.sock.bind(self.address)
            logging.info(f"Bind to {self.address}")
        except:
            logging.error(f"Failed to Bind to {self.address}")
            quit()

        self.name = input("Enter your name: ")
        msg = "$HELLO$"+self.name
        self.sock.sendto(msg.encode("utf-8"), self.serverAddr)

        self.others = {}

        self.recThread = threading.Thread(target=self.receive)
        self.recThread.setDaemon(True)
        self.recThread.start()

        self.heartbeat()
        self.checkInput()

    def receive(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(BUFFER_SIZE)
                data = data.decode('utf-8')
                addr = getStr(addr)
                # Check if send by server
                if addr == getStr(self.serverAddr):
                    # Got other clients from server
                    self.others = json.loads(data)
                    msg = ("$HELLO$"+self.name).encode("utf-8")
                    # Send Hi to All of Them
                    for addr in self.others:
                        self.sock.sendto(msg, getIp(addr))
                    continue

                # Check if HEARTBEAT
                if data.startswith("$HELLO$"):
                    if addr not in self.others:
                        # Add New client to Others list
                        self.others[addr] = {"name": data.split(
                            "$HELLO$")[1]}
                        logging.info(f"New Client {self.others[addr]}")
                    # Update last `t`
                    self.others[addr]["t"] = time.time()

                # Not HEARBEAT but from known client
                elif addr in self.others:
                    # Show Msg and update last `t`
                    print(f"{self.others[addr]['name']} : {data} ")
                    self.others[addr]["t"] = time.time()

                # From Unknown Client
                else:
                    logging.info(f"Got msg From Unknown Client {addr}")
            except:
                pass

    def heartbeat(self):
        t = threading.Timer(HEARTBEAT, self.heartbeat)
        t.daemon = True
        t.start()

        ct = time.time()
        msg = ("$HELLO$"+self.name).encode("utf-8")
        self.sock.sendto(msg, self.serverAddr)
        for addr in self.others.copy():
            other = self.others[addr]

            if ct >= (other["t"] + EXPIRIES):
                logging.info(f"Client Expired {other} at addr {addr}")
                del self.others[addr]
                continue

            self.sock.sendto(msg, getIp(addr))

    def checkInput(self):
        while True:
            msg = input().encode("utf-8")

            for addr in self.others:
                self.sock.sendto(msg, getIp(addr))


if __name__ == "__main__":
    client = Client()
