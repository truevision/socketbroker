import SocketServer
import logging
import threading

MAX_MESSAGE_LENGTH = 1024



class BrokerTCPHandler(SocketServer.StreamRequestHandler):
    def setup(self):
        self.log = logging.getLogger("BrokerClient")
        self.data = ''
        self.sends_to = [] 
        self.receives = []
        self.server.clients.append(self)
    def handle(self):
        self.log.debug("new client %s" % self.client_address[0])
        while True:
            data = self.request.recv(1)
            if len(data) == 0:
                continue
            self.log.debug("received %s" % data)
            self.log.debug("buffer length %d" % len(self.data))
            if len(self.data) + len(data) > MAX_MESSAGE_LENGTH:
               self.log.warn("buffer length larger than maximum (%d), purging buffer and closing client" % MAX_MESSAGE_LENGTH)
               self.request.send("ERROR: message larger than %d bytes" % MAX_MESSAGE_LENGTH)
               return
            self.data += data
            if len(self.data) >= 2 and self.data[-2:] == '\r\n':
                self.log.debug("seperator \\r\\n found")
                self.log.debug("entering handle data")
                self.handle_data()
                self.log.debug("finished handle data")
                self.data = ''
    def handle_data(self):
        if self.data.startswith("broker"):
            logging.debug("broker control command")
            self.handle_broker_command()
        else:
            logging.debug("sending data")
            self.server.send(self.data , self.sends_to)
    def handle_broker_command(self):
        try:
            handle, name, value = self.data.strip("\r\n").split(" ")
        except:
            self.request.send("ERROR: invalid syntax (broker command value)\r\n")
            self.log.warn("invalid broker command syntax")
            return
        if name.lower() == "receive":
            self.log.debug("receive %s " % value)
            self.receives.append(value)
            self.request.send("SUCCESS: receive on channell %s \r\n" % value)
        elif name.lower() == "send":
            self.log.debug("send %s " % value)
            self.sends_to.append(value)
            self.request.send("SUCCESS: send on channell %s \r\n" % value)
        elif name.lower() == "info":
            self.log.debug("info")
            if value.lower() == 'clients':
                for client in self.server.clients:
                    self.request.send("%s [send:%s] [receive:%s]" % (client.remote_address[0], ','.join(client.sends_to), ','.join(client.receives)))
        else:
            self.log.warn("invalid command %s " % name)
            self.request.send("ERROR: invalid command\r\n")
    def finish(self):
        self.log.debug("finishing")
        index = self.server.clients.index(self)
        del self.server.clients[index]
        

class BrokerTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    log = logging.getLogger("BrokerTCPServer")
    clients = []
    def send(self, data, chanells):

        self.log.debug("send %s to %s " % (data, ','.join(chanells)))
        for client in self.clients:
            for chanell in chanells:
                if chanell in client.receives:
                    self.log.debug("send success to %s " % client.client_address[0])
                    client.request.send(data)
                else:
                    self.log.debug("send failed: client has no channell %s , has %s " % (chanell, ','.join(client.receives)))

def start(ip, port):
    logger = logging.getLogger("BrokerTCPServer")
    logger.debug("creating server")
    server = BrokerTCPServer((ip, port), BrokerTCPHandler)
    logger.debug("creating server thread")
    server_thread = threading.Thread(target = server.serve_forever)
    server_thread.setDaemon(True)
    server_thread.start()
    logger.debug("server runnning in thread %s ", server_thread.getName())
    return server
