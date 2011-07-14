import logging 
import threading
import SocketServer 

class FlashPolicyTCPHandler(SocketServer.BaseRequestHandler):
    """ 
        flash policy TCP socket handler
        returns flash policy XML, which allows to connect to allowed ports
    """
    def setup(self):
        self.log = logging.getLogger("FlashPolicy.Client")
        self.log.debug("setup")
    def handle(self):

        self.log.debug("new client from %s" % self.client_address[0])
        data = self.request.recv(128)
        self.log.debug("received data %s " % data)
        if data.endswith("\x00") and "flash-policy-request" in data.lower():
            self.log.info("sending policy file for port %s" % self.server.port )
            self.request.send('<cross-domain-policy><allow-access-from domain="*", ports="%s" /></cross-domain-policy>' % self.server.port)
        else:
            self.log.warn("invalid request")
            self.request.send("<error>invalid request</error>")
    def finish(self):
        self.log.debug("finished request")

class FlashPolicyTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True

def start(ip, dest_port):
    logger = logging.getLogger("FlashPolicy.Server")
    logger.debug("creating server")
    server = FlashPolicyTCPServer((ip, 843), FlashPolicyTCPHandler)
    server.port = dest_port
    logger.debug("creating server thread")
    return server    
