import unittest
import socket 
from subprocess import Popen 
import subprocess
from time import sleep

class BrokerTest(unittest.TestCase):
    def setUp(self):
        self.process = Popen(["/usr/bin/env", "python", "server.py", "--ip", "127.0.0.1"],
               stdout = subprocess.PIPE)
        sleep(1)
    def test_policy_request_with_broker_port(self):
        """ test valid flash request policy to broker port """
        client = socket.create_connection(('127.0.0.1', 843))
        client.send("<policy-file-request/>\x00")
        data = client.recv(1024)
        policy = '<cross-domain-policy><allow-access-from domain="*", ports="1001" /></cross-domain-policy>' 
        self.assertEqual(data, policy)
        client.close()
    def test_channel_one_on_one_communication(self):
        client_first = socket.create_connection(("127.0.0.1", 1001))
        client_second = socket.create_connection(("127.0.0.1", 1001))
        client_first.send("broker send second\r\n")
        client_second.send("broker receive second\r\n")
        status, junk = client_first.recv(256).split(":")
        status_second, junk = client_second.recv(256).split(":")

        self.assertEqual(status, "SUCCESS")
        self.assertEqual(status_second, "SUCCESS")
        client_first.close()
        client_second.close()
    def test_one_to_many_communication(self):
        broadcaster = socket.create_connection(("127.0.0.1", 1001))
        broadcaster.send("broker send broadcast\r\n")
        data, junk = broadcaster.recv(512).split(":")
        self.assertEqual(data, "SUCCESS")
        clients = []
        for i in range(0, 20):
            client = socket.create_connection(("127.0.0.1", 1001))
            client.send("broker receive broadcast\r\n")
            data, junk = client.recv(512).split(":")
            self.assertEqual(data, "SUCCESS")
            clients.append(client)
        broadcaster.send("broadcast\r\n")
        for client in clients:
            data = client.recv(512)
            self.assertEqual(data, "broadcast\r\n")

    def tearDown(self):
        self.process.terminate()
if __name__ == "__main__":
    unittest.main()
