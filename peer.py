import socket
import random
import threading
import logging
import time
import json

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

BUFFER_SIZE = 1024
HEARTBEAT = 5
EXPIRIES = HEARTBEAT * 3
RAND_MIN = 45000
RAND_MAX = 49000


def getIp(s):
    return (s.split(":")[0], int(s.split(":")[1]))


def getStr(ip):
    return ip[0]+":"+str(ip[1])


class Peer:
    def __init__(self, mainHost="127.0.0.1", mainPort=55000, host="127.0.0.1", port=None):
        self.isMain = not mainHost
        if self.isMain:
            port = 55000
        elif port is None:
            port = random.randint(RAND_MIN, RAND_MAX)

        self.address = (host, port)
        self.mainAddr = (mainHost or "", mainPort)

        logging.info(f"Main Peer {self.mainAddr}")
        try:
            self.sock = socket.socket(socket.AF_INET,
                                      socket.SOCK_DGRAM)
            self.sock.bind(self.address)
            logging.info(f"Bind to {self.address}")
        except:
            logging.error(f"Failed to Bind to {self.address}")
            quit()

        self.name = input("Enter your name: ")
        if not self.isMain:
            msg = "$HELLO$"+self.name
            self.sock.sendto(msg.encode("utf-8"), self.mainAddr)
        self.peers = {getStr(self.address): {
            "name": self.name, "t": time.time()}}
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

                logging.debug(f"Received {addr} | {data}")

                if data.startswith("$DATA$"):
                    self.peers.update(json.loads(data.split("$DATA$")[1]))
                    msg = ("$HELLO$"+self.name).encode("utf-8")
                    for addr in self.peers:
                        if getIp(addr) != self.address:
                            self.sock.sendto(msg, getIp(addr))
                    continue

                if data.startswith("$HELLO$"):
                    if addr not in self.peers:
                        peersJson = "$DATA$"+json.dumps(self.peers)
                        self.sock.sendto(peersJson.encode(
                            "utf-8"), getIp(addr))

                        self.peers[addr] = {"name": data.split(
                            "$HELLO$")[1]}
                        logging.info(f"New Peer {self.peers[addr]}")

                    # Update last `t`
                    self.peers[addr]["t"] = time.time()

                # Not HEARBEAT but from known Peer
                elif addr in self.peers:
                    # Show Msg and update last `t`
                    print(f"{self.peers[addr]['name']} : {data} ")
                    self.peers[addr]["t"] = time.time()

                # From Unknown Peer
                else:
                    logging.info(f"Got msg From Unknown Peer {addr}")
            except Exception as e:
                print(e)

    def heartbeat(self):
        t = threading.Timer(HEARTBEAT, self.heartbeat)
        t.daemon = True
        t.start()

        ct = time.time()
        self.peers[getStr(self.address)]['t'] = ct
        msg = ("$HELLO$"+self.name).encode("utf-8")

        for addr in self.peers.copy():
            if getIp(addr) == self.address:
                continue
            other = self.peers[addr]

            if ct >= (other["t"] + EXPIRIES):
                logging.info(f"Peer Expired {other} at addr {addr}")
                del self.peers[addr]
                continue

            self.sock.sendto(msg, getIp(addr))

    def checkInput(self):
        while True:
            msg = input().encode("utf-8")

            for addr in self.peers:
                if getIp(addr) != self.address:
                    self.sock.sendto(msg, getIp(addr))


if __name__ == "__main__":
    mainHost = input("Enter one peer ip: ")
    if not mainHost:
        mainHost = None
        mainPort = 55000
    else:
        mainPort = int(input("Enter Peer Port: ") or "55000")
    peer = Peer(mainHost, mainPort)
