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
        client_first = socket.create_connection("127.0.0.1", 843)
        client_second = socket.create_connection("127.0.0.1", 843)
        client_first.send("broker send second")
        status, junk = client_first.recv(1024)
        self.assertEqual(status, "SUCCESS")

    def tearDown(self):
        self.process.terminate()
if __name__ == "__main__":
    unittest.main()
