import random
import numpy as np
import simpy
import hashlib
import copy

from transaction import Transaction

class Peer:
    def __init__(self, ID, slow, CPU_low, T_tx, n, env):
        self.ID = ID
        self.slow = slow
        self.CPU_low = CPU_low
        self.T_tx = T_tx
        self.n = n
        self.env = env

        # Initialising empty set containing the transaction IDs I have seen
        self.seen_txn_ID = set()

        # Initialising read queue, this would be used for receiving messages
        self.read_queue = simpy.Store(env)

        # this would be used for sending
        # contains peer link objects
        self.send_list = []
    
    def update_send_list(self, lnk):
        self.send_list.append(lnk)

    # This function creates transaction
    def create_txn(self, receiver, coins = 5, txn_size = 1):
        # Generating unique transaction ID here
        txn_data = f"{self.ID} pays {receiver} {coins} coins" + str(random.randint(1, 10000000000)) + "___" + str(random.randint(1, 10000000000))
        txn_ID = hashlib.sha256(txn_data.encode()).hexdigest()
        
        # Creating the message that would be sent
        txn = Transaction(self.ID, receiver, coins, txn_ID, txn_size)
        return txn

    # This function would send txns from the current peer
    def txn_sender(self):
        while True:
            # Finding the peer to which I would send the transaction
            rec = random.randint(1, self.n)
            while rec==self.ID:
                rec = random.randint(1, self.n)

            # Sending the txn 
            print(f"{self.ID} paid {rec} ------- TIME rn {self.env.now}")

            # Creating transaction
            txn = self.create_txn(rec, 5, 1)
            
            # Adding to the list of seen txns
            self.seen_txn_ID.add(txn.txn_ID)

            # Sending the currently created transaction
            for link in self.send_list:
                link.send_txn(txn)

            # Waiting for exponential random time(as required by question) before sending next txn
            gap = np.random.exponential(scale=(self.T_tx))
            print(f"SENDER {self.ID} gap {gap} TIME {self.env.now}")

            yield self.env.timeout(gap)
            
    def forward_txn(self, txn):
        # have to forward transaction to links if have not seen it before
        if txn.txn_ID not in self.seen_txn_ID:
            # Marking the current txn as seen by noting its ID
            self.seen_txn_ID.add(txn.txn_ID)

            # Changing the sender of transaction

            received_from = txn.curr_sender
            
            # Since we need to forward the transaction by changing the sender field
            # We need deepcopy as else conflict arises causes same initial txn was sent
            # to all the connected nodes and hence change at 1 reflects in all
            new_txn = copy.deepcopy(txn)
            new_txn.curr_sender = self.ID

            # Forwarding the received block
            for link in self.send_list:
                # Making sure that we do loop-less transaction
                if link.receiver.ID == received_from:
                    continue
                print(f"{self.ID} FWD TO {link.receiver.ID} rec from {received_from} AT {self.env.now}")
                link.send_txn(new_txn)
    

    # This function would continously read queue to process received message
    def reader(self):
        while True:
            # Here we would take messages from the queue as they arrive
            txn = yield self.read_queue.get()

            # Processing the txn here
            print(txn, f"AT {self.env.now}")
            self.forward_txn(txn)
