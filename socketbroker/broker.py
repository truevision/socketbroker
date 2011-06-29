from __future__ import print_function

import asyncore
import collections
import logging
import socket
import argparse
import asynchat

from flashpolicy import PolicyDispatcher 

MAX_MESSAGE_LENGTH = 1024


class RemoteClient(asynchat.async_chat):
    def __init__(self, host, socket, address):
        asynchat.async_chat.__init__(self,socket)
        self.log = logging.getLogger("client-%d" % address[1])
        self.log.info("new client from %s" % address[0])
        self.host = host
        self.receives = []
        self.sends_to = []
        self.address = address
        self.set_terminator("\r\n")
        self.data = ""
    def collect_incoming_data(self, data):
        if len(self.data) + len(data) > MAX_MESSAGE_LENGTH:
            self.log.warn("message larger than %d bytes, closing connection" % (MAX_MESSAGE_LENGTH))
            self.push("ERROR: Total message larger than %d bytes" % (MAX_MESSAGE_LENGTH)) 
            self.handle_close()
            self.log.debug("received data %s " % (data))
        self.data = self.data + data
    def handle_close(self):
        asynchat.async_chat.handle_close(self)
        self.log.info("closing connection")
    def found_terminator(self):
        data = self.data
        self.log.debug("found terminator with data %s " % (self.data))
        self.data  = ''
        if data.startswith("broker"):
            data = data.split(" ")
            if len(data) != 3:
                self.log.warn("invalid syntax %s " % (self.data)) 
                self.push("ERROR: syntax broker {command} {value}\r\n")
                return 
            broker, command, value = data 
            if command.lower() == 'receive':
                if value.lower() in self.receives:
                    self.log.warn("try to receive already subscribed chanell %s " % value.lower())
                    self.push("ERROR: you already receive on channell %s\r\n" % value.lower())
                    return
                self.log.info("receiving on chanell %s " % (value.lower()))
                self.receives.append(value.lower())
                self.push("SUCCESS: receive on chanell %s \r\n" % (value))
            elif command.lower() == "send":
                if value.lower() in self.sends_to:
                    self.log.warn("try to send to already sending chanell %s " % (value.lower()))
                    self.push("ERROR: you already send on chanell %s \r\n" % value.lower())
                    return 
                self.log.info("send on chanell %s " % (value.lower()))
                self.sends_to.append(value.lower())
                self.push("SUCCESS: send to chanell %s \r\n" % (value))
            else:
                self.log.warn("invalid command %s " % (command.lower()))
                self.push("ERROR: unknown command %s \r\n" % command)
        else:
            if len(self.sends_to) == 0:
                self.log.warn("try to broadcast without any sender chanells")
                self.push("ERROR: no sender chanells registred \r\n")
                return
            self.log.info("broadcasting to %s" % (",".join(self.sends_to)))
            self.host.broadcast(data, self.sends_to)
    def say(self, data, chanells):
        read = False
        self.log.debug("received data %s " % (data))
        self.log.debug("chanells to send it %s " % chanells)
        for chanell in chanells: 
            if chanell in self.receives:
                self.log.debug("channel %s in receiving " % chanell)
                read = True
                break
        if not read:
            self.log.debug("no valid receive chanells")
            return 
        self.log.debug("sending data %s to client " % data)
        self.push(data + "\r\n")

class Broker(asyncore.dispatcher):

    log = logging.getLogger('Host')

    def __init__(self, ip, port):
        address = (ip, port)
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(address)
        self.listen(5)
        self.remote_clients = []

    def handle_accept(self):
        socket, addr = self.accept() # For the remote client.
        self.log.info('Accepted client at %s', addr)
        self.remote_clients.append(RemoteClient(self, socket, addr))

    def handle_read(self):
        
        self.log.debug('received message: %s', self.read())

    def broadcast(self, message, type):
        self.log.info('broadcasting message: %s (chanells - %s) ', message, type)
        for remote_client in self.remote_clients:
            self.log.debug("%d clients in pool " % (len(self.remote_clients)))
            self.log.debug("sending data %s to client %s " % (message, remote_client.address))
            remote_client.say(message, type)
    
    def handle_close(self):
        self.log.info("closing host")
        self.close()
    def handle_error(self):
        logging.critic("unhandled error: %s ",compat_traceback())

