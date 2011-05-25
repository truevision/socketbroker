import asyncore
import asynchat
import logging 
import socket 

MAX_DATA_LENGTH = 1024

class RemoteClient(asynchat.async_chat):
    def __init__(self, socket, port = "*"):
        asynchat.async_chat.__init__(self, socket)
        self.port = port
        self.set_terminator("\x00")
        self.data = ""
        self.log = logging.getLogger("FlashPolicy.Client")
        self.log.info("new client")
    def collect_incoming_data(self, data):
        self.log.debug("recieved data %s" % data)
        total_len = len(data) + len(self.data)
        if total_len > MAX_DATA_LENGTH:
            self.push("too much data. closing connection")
            self.log.warn("too much data received (%d bytes)", total_len)
            self.handle_close()
            return 

        self.data = self.data + data 
    def found_terminator(self):
        self.log.debug("found terminator")
        if 'policy-file-request' not in self.data.lower().strip():
            self.push("invalid request")
            self.log.warn("invalid request (%s)" % self.data)
            self.handle_close()
        policy = '<cross-domain-policy><allow-access-from domain="*", ports="%s" /></cross-domain-policy>' % (self.port)
        self.push(policy)
        self.log.info("pushing policy ")
    def handle_close(self):
        asynchat.async_chat.handle_close(self)
        self.log.info("closing connection")

class PolicyDispatcher(asyncore.dispatcher):
    def __init__(self, ip = "0.0.0.0", dest_port = "*"):
        self.dest_port = dest_port
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log = logging.getLogger("FlashPolicy")
        self.set_reuse_addr()
        self.log.info("binding to %s:%s" % (ip, 843))
        self.bind((ip, 843))
        self.listen(5)
    def handle_accept(self):
        socket, address = self.accept()
        RemoteClient(socket, self.dest_port)
    
