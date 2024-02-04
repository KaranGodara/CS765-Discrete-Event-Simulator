import sys

from collections import defaultdict
from transaction import Transaction
from block import CoinBaseTransaction

class TreeNode:
    def __init__(self, blk, time_stamp, parent, n):
        self.block = blk
        self.time_stamp = time_stamp
        self.parent = parent

        self.depth = 0 # 0 is genesis
        
        # Would initialise empty child list here
        self.children = []

        # Would store the balance until this block for all peers
        self.balance = defaultdict(int)

        if self.parent != None : # Means genesis Tree Node
            self.depth = self.parent.depth + 1
            for idx in range(1, n + 1):
                self.balance[idx] = self.parent.balance[idx]

            # Updating balance based on txns added in current block (block must be validated)
            for txn in self.block.txn_list:
                if isinstance(txn, Transaction):
                    self.balance[txn.sender_ID] -= txn.coins
                    self.balance[txn.receiver_ID] += txn.coins

                elif isinstance(txn, CoinBaseTransaction):
                    self.balance[txn.miner] += txn.coins

                else:
                    sys.stderr.write("Incorrect transaction type entered in transaction list of block\n")
                    sys.exit(1)

    # appending tree node to child list
    def add_child(self, child):
        self.children.append(child)

class Tree:
    def __init__(self, root):
        self.root = root

    # ADD FUNCTIONS FOR ANIMATION HERE, LIKE TRAVERSAL, PRINTING ETC