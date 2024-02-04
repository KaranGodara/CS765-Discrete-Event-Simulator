import random
import numpy as np
import simpy
import hashlib
import copy
from collections import defaultdict

from transaction import Transaction
from block import Block
from tree import TreeNode

class Peer:
    def __init__(self, ID, slow, CPU_low, T_tx, n, env):
        self.ID = ID
        self.slow = slow
        self.CPU_low = CPU_low
        self.T_tx = T_tx # This is interarrival time between generated transactions
        self.n = n
        self.env = env
        self.block_mine_time = 0 # This is mean block mining time

        # # This is my blockchain tree
        # self.blockchain = None

        # Initialising empty set containing the transaction IDs I have seen
        # self.seen_txn_ID = set()

        # Initialising read queue, this would be used for receiving messages
        # GENESIS BLOCK IS TO BE ADDED TO THIS QUEUE BEFORE START OF SIMULATION
        self.read_queue = simpy.Store(env)

        # this would be used for sending
        # contains peer link objects
        self.send_list = []

        # Creating mapping between blockID and TreeNode
        self.block_to_tree = dict()

        # Initialising empty list of all the txns
        self.txns_seen = dict()

        self.curr_tree_node = None

    # Would be called during peer instantiation to set mean block mining time
    def update_block_mine_time(self, block_mine_time):
        self.block_mine_time = block_mine_time

    # Would be called during peer instantiation to set genesis block and its mapping in block_to_tree
    def add_genesis_block(self, gen_block_tree_node):
        self.block_to_tree[gen_block_tree_node.block.block_ID] = gen_block_tree_node
        self.curr_tree_node = gen_block_tree_node
        # self.blockchain = Tree(gen_block_tree_node)
    
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
        # while True:
            # Finding the peer to which I would send the transaction
            rec = random.randint(1, self.n)
            while rec==self.ID:
                rec = random.randint(1, self.n)

            # Sending the txn 
            print(f"{self.ID} paid {rec} ------- TIME rn {self.env.now}")

            # Creating transaction
            txn = self.create_txn(rec, 5, 1)
            
            # Adding to the list of seen txns
            # self.seen_txn_ID.add(txn.txn_ID)
            self.txns_seen[txn.txn_ID] = txn

            # Sending the currently created transaction
            for link in self.send_list:
                link.send_txn(txn)

            # Waiting for exponential random time(as required by question) before sending next txn
            gap = np.random.exponential(scale=(self.T_tx))
            print(f"SENDER {self.ID} gap {gap} TIME {self.env.now}")

            yield self.env.timeout(gap)
            
    def forward_txn(self, txn):
        # have to forward transaction to links if have not seen it before
        if txn.txn_ID not in self.txns_seen.keys():
            # Marking the current txn as seen by noting its ID
            # self.seen_txn_ID.add(txn.txn_ID)
            self.txns_seen[txn.txn_ID] = txn

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
    
    ##################################################################################
    # FUNCTIONS RELATED TO BLOCKS START HERE

    # Returns 0 if txn already present in blockchain, else 1
    # Here parent is a tree node
    def txn_not_already_present(self, txn, parent):
        while parent != None :
            for tmp in parent.block.txn_list :
                if tmp.txn_ID == txn.txn_ID :
                    return 0
            parent = parent.parent
        return 1


    # checks if block not already added, have correct parent block ID and all its txns
    # never appear before in its chain
    def validate_block(self, blk):
        # checks if block not already added
        if blk.block_ID in self.block_to_tree.keys():
            return 0
        
        # have correct parent block ID
        if blk.parent_ID not in self.block_to_tree.keys():
            return 0

        spending = copy.deepcopy(self.block_to_tree[blk.parent_ID].balance)

        # all its txns never appear before in its chain and sender has enough balance
        for txn in blk.txn_list:
            if isinstance(txn, Transaction):
                if not self.txn_not_already_present(txn, self.block_to_tree[blk.parent_ID]):
                    return 0
                spending[txn.sender_ID] -= txn.coins
                if spending[txn.sender_ID] < 0:
                    return 0    
        return 1
            
    
    def create_and_transmit_new_block(self):
        # New block created
        new_block = Block(self.ID, self.curr_tree_node.block.block_ID, 1000)

        # This stores balance of each peer as of now
        spending = copy.deepcopy(self.curr_tree_node.balance)

        for txn in self.txns_seen.values():
            if not self.txn_not_already_present(txn, self.curr_tree_node):
                continue

            # Can only add this txn if sender's balance is more than what he wants to spend
            if spending[txn.sender_ID] >= txn.coins :
                # O is returned if max limit reached and block not added
                if new_block.add_txn_to_block(txn) == 0: #Added txn to Block
                    break

                # If 1 received that means, txn added successfully to block, update balance
                spending[txn.sender_ID] -= txn.coins
        
        # now valid transactions have been added to the block
        # Simulating PoW
        to_time = np.random.exponential(scale=(self.block_mine_time))
        print(f"BLOCK: {self.ID} creation start at {new_block.block_ID} at {self.env.now} TO for {to_time}")
        yield self.env.timeout(to_time)

        # now PoW has been simulated
        # checking if peer has the same longest chain
        # that is curr_tree_node is the same or not
        # now checking block's parent ID is same as cur_tree_node.block_ID
        if(new_block.parent_ID == self.curr_tree_node.block.block_ID):
            print(f"BLOCK: {self.ID} longest so broadcasting {new_block.block_ID} at {self.env.now}")

            # add this block in my tree
            # self.block_receiver(new_block)
            # Adding this to my own read_queue cause now we need to add it to our block chain
            self.read_queue.put(new_block)
        else: 
            print(f"BLOCK: {self.ID} && {new_block.block_ID} at {self.env.now} Rejeceted ")
            


    # Used to forward the validated block, note blocks are already validated
    # Validated here implies, block is seen for the first time and hence forwarding needs to be done
    def forward_block(self, blk):
        # Need to create tree node and add the mapping to block_to_tree
        self.block_to_tree[blk.block_ID] = TreeNode(blk, self.env.now, self.block_to_tree[blk.parent_ID], self.n)

        # Changing the sender of block
        received_from = blk.curr_sender
        
        # Since we need to forward the block by changing the sender field
        # We need deepcopy as else conflict arises causes same initial block was sent
        # to all the connected nodes and hence change at 1 reflects in all
        new_blk = copy.deepcopy(blk)
        new_blk.curr_sender = self.ID

        # Forwarding the received block
        for link in self.send_list:
            # Making sure that we do loop-less transaction
            if link.receiver.ID == received_from:
                continue
            print(f"BLOCK: {self.ID} FWD TO {link.receiver.ID} rec from {received_from} AT {self.env.now}")
            link.send_txn(new_blk)


    def block_receiver(self, blk):
        if not self.validate_block(blk):
            return
        # Since block is validated, forward it to others
        self.forward_block(blk) 

        # Does it create a new longest chain
        if self.block_to_tree[blk.block_ID].depth > self.curr_tree_node.depth :
            print(f"BLOCK: Curr tree node changed {self.ID}")
            # If yes, select subset of txns received so far not included in any blocks in the longest chain
            # Generate Tk = I/hk
            self.curr_tree_node = self.block_to_tree[blk.block_ID]

            # Launching this as process so that reader doesn't time out during 
            # block PoW mining
            self.env.process(self.create_and_transmit_new_block())

    ##################################################################################
    # FUNCTIONS RELATED TO BLOCKS END HERE

    # This function would continously read queue to process received message
    def reader(self):
        while True:
            # Here we would take messages from the queue as they arrive
            msg = yield self.read_queue.get()

            if isinstance(msg, Transaction):
                # Processing the txn here
                print(msg, f"AT {self.env.now} received at {self.ID}")
                self.forward_txn(msg)
            
            else :
                # Processing block here
                print(msg, f"BLOCK AT {self.env.now} rcvd at {self.ID}")
                self.block_receiver(msg)