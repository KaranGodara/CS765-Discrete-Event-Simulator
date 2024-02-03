import random 
import numpy as np
import hashlib

from transaction import Transaction

class Peer_Link :
    def __init__(self, sender, receiver, env):
        self.sender = sender
        self.receiver = receiver
        self.env = env

        # Finding the transmission delay params
        self.p_ij = random.uniform(10, 500) # It's in ms
        self.c_ij = 100 # It's in Mbps
        if (sender.slow or receiver.slow) :
            self.c_ij = 5
        self.d_ij_mean = (96.0/self.c_ij)

    def send_txn(self, m_size = 1, coins = 5): # m_size is in KBps (default is 1KB)
        def per_msg_sender():
            d_ij = np.random.exponential(scale=(self.d_ij_mean))

            # delay in ms
            delay = self.p_ij + ((m_size*8.0)/self.c_ij) + d_ij

            # Generating unique transaction ID here
            txn_data = f"{self.sender.ID} pays {self.receiver.ID} {coins} coins" + str(random.randint(1, 10000000000))
            txn_ID = hashlib.sha256(txn_data.encode()).hexdigest()
            
            # Creating the message that would be sent
            msg = Transaction(self.sender.ID, self.receiver.ID, coins, txn_ID)
            print(f"Delay of {self.sender.ID} to {self.receiver.ID} is {delay} ++++++ TIME {self.env.now}")

            yield self.env.timeout(delay) # time is in milliseconds

            # Sending transaction by adding it to receiver's queue
            print(f"PUT IN Q of {self.receiver.ID} by {self.sender.ID} -$$- TIME {self.env.now}")
            self.receiver.read_queue.put(msg)
            
        self.env.process(per_msg_sender())
        
