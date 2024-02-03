import random
import queue
from collections import defaultdict

from peer import Peer
from peer_link import Peer_Link

class Simulator:
    def __init__(self, n, z0, z1, T_tx, env):
        # Initial parameters
        self.n = n
        self.z0 = z0
        self.z1 = z1
        self.T_tx = T_tx
        self.env = env

        # Initialising Peer Dict
        self.peer_dict = dict()
        print("Simulator constructed")

    # Generating 1 with probability z and 0 otherwise
    def generate_RV(self, z):
        sample = random.random()
        if sample < z:
            return 1
        else:
            return 0

    # Creating peers and adding them in the peer dict of simulator
    def create_peers(self):
        for id in range(1, self.n + 1):
            self.peer_dict[id] = (Peer(id, self.generate_RV(self.z0 / 100.0), self.generate_RV(self.z1 / 100.0), self.T_tx, self.env))

    # This function checks if given edge list representation forms a connected graph or not
    def check_connectivity(self, edge_list):
        visited = [0] * self.n

        # Initialsing queue to do BFS
        q = queue.Queue(maxsize = 0)

        # Starting arbitrarily with node '0'
        # Note, edge list is 1 indexed whereas here q and visited are 0 indexed
        q.put(0)

        # Main BFS algo 
        while(not q.empty()):
            # Getting the element from queue
            elem = q.get()

            # Continuing if already visited
            if visited[elem]:
                continue

            # Else, marking current elem as visited
            visited[elem] = 1

            # Adding unvisited neighbors of current elem to q
            for nxt in edge_list[elem + 1]:
                if visited[nxt-1] == 0:
                    q.put(nxt-1)
        
        return (sum(visited) == self.n)
        


    # Making connected graph for the nodes
    def create_network_graph(self, min_peers, max_peers):
        # Initialising empty edge list for the network graph
        edge_list = defaultdict(list)

        # Variable that on 1 denotes if connected graph is obtained or not, 0 otherwise
        grph_made = 0

        # Continue attempting to make graph until connectivity is achieved
        while(grph_made == 0):
            # Emptying edge_list of previous failed attempts
            edge_list.clear()

            # This stores initially how many neighbor nodes to connect for each node
            p_cnt = dict()

            # Populating the p_cnt, with values between min_peers and max_peers (both inclusive)
            for idx in range(1, self.n+1):
                # How many nodes is the current node connected to?
                peer_cnt = random.randint(min_peers, max_peers)
                peer_cnt = min(peer_cnt, self.n - 1)
                p_cnt[idx] = peer_cnt
            
            # This loop tries to create graph, crct_ngb variable if 1 says for loop 
            # executed successfully by giving each node required number or neighbors
            # and is 0 otherwise
            crct_ngb = 1
            for idx in range(1,self.n+1):
                # This tm is for a heuristic such that we attempt to allocate a neighbor
                # within only n^2 tries, this helps in us not getting stuck in an infinte 
                # while loop (Eg, all nodes have been connected to required number of neighbors
                # but not say node x, then any candidate neighbor would be rejected and we would be
                # stuck in a while loop)
                tm = 0

                # Note p_cnt[idx], actually store number of neighbors yet needed to be connected
                # for a node idx and hence it dynamically reduces by 1 on each successful connection
                # Until no more neighbors are required (i.e., p_cnt[idx] == 0)
                while(p_cnt[idx] > 0 and tm < self.n*self.n):
                    tm += 1

                    # ngb is candidate neighbor
                    ngb = random.randint(1, self.n)

                    # Only add ngb as peer to current node, if peer not same as current node,
                    # peer still has connecting capacity left (i.e., p_cnt[ngb] > 0) and peer
                    # not already a neighbor of current node
                    if (ngb != idx) and (p_cnt[ngb] > 0) and (ngb not in edge_list[idx]):
                        edge_list[idx].append(ngb)
                        p_cnt[idx] -= 1

                        edge_list[ngb].append(idx)
                        p_cnt[ngb] -= 1

                # On incorrect exit of while loop, attempt again
                if p_cnt[idx] != 0:
                    crct_ngb = 0
                    break
            if not crct_ngb :
                continue
            
            
            # Checking if graph is connected
            grph_made = self.check_connectivity(edge_list)
        print("Graph made successfully")
        return edge_list

    # This function would actually materialise the connections of the p2p network
    def create_p2p_links(self, edge_list):
        for idx in range(1, self.n+1):
            for ngb in edge_list[idx]:
                lnk = Peer_Link(self.peer_dict[idx], self.peer_dict[ngb], self.env)
                self.peer_dict[idx].update_send_list(lnk)

    def start_simulation(self):
        print("Creating p2p network")
        # Initialising nodes of the network
        self.create_peers()

        # Generating network topology
        edge_list = self.create_network_graph(3,6)

        # Create actual peer links based on topology
        self.create_p2p_links(edge_list)

        for idx in range(1, self.n+1):
            self.env.process((self.peer_dict[idx]).txn_sender())
            self.env.process((self.peer_dict[idx]).reader())

