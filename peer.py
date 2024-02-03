import random
import numpy as np
import simpy

class Peer:
    def __init__(self, ID, slow, CPU_low, T_tx, env):
        self.ID = ID
        self.slow = slow
        self.CPU_low = CPU_low
        self.T_tx = T_tx
        self.env = env
        self.read_queue = simpy.Store(env)

        # this would be used for sending
        self.send_list = []

        # This would be used for receiving messages
        # REsource
    
    def update_send_list(self, lnk):
        self.send_list.append(lnk)

    # This function would send txns from the current peer
    def txn_sender(self):
        while True:
            # Finding the peer to which I would send the transaction
            idx = random.randint(0, len(self.send_list) - 1)

            # Sending the txn 
            print(f"{self.ID} paid {self.send_list[idx].receiver.ID} ------- TIME rn {self.env.now}")
            self.send_list[idx].send_txn()

            # Waiting for exponential random time(as required by question) before sending next txn
            gap = np.random.exponential(scale=(self.T_tx))
            print(f"SENDER {self.ID} gap {gap} TIME {self.env.now}")

            yield self.env.timeout(gap)
            

    # This function would continously read queue to process received message
    def reader(self):
        while True:
            # Here we would take messages from the queue as they arrive
            msg = yield self.read_queue.get()

            # Processing the txn here
            print(msg, f"AT {self.env.now}")
