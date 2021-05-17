import socket
import threading
import logging
import time
import json

from config import BUFFER_SIZE, HEARTBEAT, EXPIRIES, getStr, getIp

logging.basicConfig(level=logging.INFO)


class Server:
    def __init__(self, host="127.0.0.1", port=55000):
        self.address = (host, port)
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(self.address)
            logging.info(f"UDP Socket bind to {host}:{port}")
            self.clients = {}
            self.recThread = threading.Thread(target=self.receive)
            self.recThread.setDaemon(True)
            self.recThread.start()
        except:
            logging.error(f"Unable to Bind UDP socket")
            quit()

        self.check()

    def check(self):
        try:
            time.sleep(HEARTBEAT)
        except:
            logging.info("Exiting!")
            quit()

        ct = time.time()
        # Check for Expired Clients
        for clientAddr in self.clients.copy():
            client = self.clients[clientAddr]
            # Checks if current Time is greater than last t + `EXPIRIES`
            if ct >= (client["t"] + EXPIRIES):
                logging.info(f"Client Expired {client} at addr {clientAddr}")
                del self.clients[clientAddr]
        self.check()

    def receive(self):
        while True:
            data, addr = self.sock.recvfrom(BUFFER_SIZE)
            data = data.decode('utf-8')
            addr = getStr(addr)
            logging.debug(
                f"received message: {data} from {addr}")

            if not data.startswith("$HELLO$"):
                logging.warning(f"GOT WRONG MSG...")
                continue

            if addr not in self.clients:
                # Create Json of Current clients
                clientsJson = json.dumps(self.clients)

                # Send current clients to the new one
                self.sock.sendto(clientsJson.encode(
                    "utf-8"), getIp(addr))

                # Add New client to Clients list
                self.clients[addr] = {"name": data.split(
                    "$HELLO$")[1]}

                logging.info(f"New Client {self.clients[addr]}")
            self.clients[addr]["t"] = time.time()


if __name__ == "__main__":
    server = Server()
