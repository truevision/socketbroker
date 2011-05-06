from __future__ import print_function

import asyncore
import collections
import logging
import socket
import argparse

MAX_MESSAGE_LENGTH = 1024


class RemoteClient(asyncore.dispatcher):

    """Wraps a remote client socket."""

    def __init__(self, host, socket, address):
        asyncore.dispatcher.__init__(self, socket)
        self.host = host
        self.outbox = collections.deque()
        self.type = None 
        self.address = address
    def say(self, message, type):
        if type != self.type:
            self.outbox.append(message)

    def handle_read(self):
        client_message = self.recv(MAX_MESSAGE_LENGTH)

        if not self.type and client_message.startswith("1"):
            self.type = 'controller'
            self.host.log.info("registered %s as controller", self.address)
            client_message = client_message[1:]
        elif not self.type:
            self.type = 'view'
            self.host.log.info("registered %s as view", self.address)
            client_message = client_message[1:]
       
        if len(client_message.strip()):
            self.host.log.debug("broadcasting %s from %s (%s)", client_message, self.address, self.type)
            self.host.broadcast(client_message, self.type)


    def handle_write(self):

        if not self.outbox:
            return
        message = self.outbox.popleft()
        if len(message) > MAX_MESSAGE_LENGTH:
            message = message[0:MAX_MESSAGE_LENGTH]
        self.send(message)
    def handle_close(self):
        self.host.log.warning("closing connection from %s", self.address)
        self.close()

class Host(asyncore.dispatcher):

    log = logging.getLogger('Host')

    def __init__(self, ip, port):
        address = (ip, port)
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(address)
        self.listen(4)
        self.remote_clients = []

    def handle_accept(self):
        socket, addr = self.accept() # For the remote client.
        self.log.info('Accepted client at %s', addr)
        self.remote_clients.append(RemoteClient(self, socket, addr))

    def handle_read(self):
        
        self.log.info('Received message: %s', self.read())

    def broadcast(self, message, type):
        self.log.info('Broadcasting message: %s (type - %s) ', message, type)
        for remote_client in self.remote_clients:
            remote_client.say(message, type)
    def handle_close(self):
        self.log.info("closing host")
        self.close()
    def handle_error(self):
        logging.info("error: %s ", self.compat_traceback())



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "socket message broker")
    parser.add_argument('--port', type = int, help="port to listen", default = 1001)
    parser.add_argument('--ip', type = str, help = "ip address to listen", default = "0.0.0.0")
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    logging.info('Creating host')
    logging.info("command line arguments: %s", args)
    try:
        host = Host(args.ip, args.port)
        asyncore.loop()
    except KeyboardInterrupt as error:
        logging.info("Got CTRL+C, shutting down gracefully")
        asyncore.close_all()
