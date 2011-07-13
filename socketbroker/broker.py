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
            data = self.request.recv(16)
            if len(data) == 0:
                continue
            self.log.debug("received %s" % data)
            self.log.debug("buffer length %d" % len(self.data))
            if len(self.data) + len(data) > MAX_MESSAGE_LENGTH:
               self.log.warn("buffer length larger than maximum (%d), purging buffer and closing client" % MAX_MESSAGE_LENGTH)
               self.request.send("ERROR: message larger than %d bytes" % MAX_MESSAGE_LENGTH)
               return
            if "\r\n" in data:
                data = data.split("\r\n")
                self.log.debug("found seperator in data")
                self.data = self.data + data[0]
                self.log.debug("data %s" % self.data)
                self.log.debug("entering handle_data")
                self.handle_data()
                self.log.debug("finished handle_data")
                if len(data) == 1:
                    data[1] = ''
                self.log.debug("data after seperator '%s' " % data[1]) 
                self.data = data[1]
            else:
                self.data += data
    def handle_data(self):
        if self.data.startswith("broker"):
            logging.debug("broker control command")
            self.handle_broker_command()
        else:
            logging.debug("sending data")
            self.server.send(self.data + "\r\n" , self.sends_to)
    def handle_broker_command(self):
        try:
            handle, name, value = self.data.split(" ")
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
                    self.log.debug("sent to %s " % client.client_address[0])
                    client.request.send(data)
                else:
                    self.log.debug("no chanells")

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
