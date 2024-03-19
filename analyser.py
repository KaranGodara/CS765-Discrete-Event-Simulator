import networkx as nx
import os
import csv
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import graphviz_layout
import argparse
from collections import Counter
import queue

# Read the graph from the file
# Assumed format: BLOCK ID,TIME STAMP,PARENT ID,MINER,SLOW,LOW_CPU
# If pvt is False, then private blocks are not considered in the graph
def read_graph(pvt=False, file="output/blockchain_1.txt"):
    id_to_virt = {} # Mapping from block ID to virtual node ID that would be used in the graph
    virt_to_miner = {} # Mapping from virtual node ID to miner ID who mined the block and whether it is private i.e virtual node ID to (miner ID, is_private)
    miner = {} # Mapping from miner ID to (slow, low_cpu)
    i = 1
    G = nx.DiGraph()
    with open(file , "r") as f:
        reader = csv.reader(f)
        next(reader)
        rows = list(reader)
        rows.sort(key=lambda x: float(x[1])) # Sorting the rows based on time stamp
        for row in rows:
            if pvt or int(row[6]) == 0:
                id_to_virt[row[0]] = i
                virt_to_miner[i] = (int(row[3]), int(row[6]))
                miner[int(row[3])] = (int(row[4]), int(row[5]))
                i += 1
                G.add_node(id_to_virt[row[0]], label=id_to_virt[row[0]]) # Adding node to the graph
                if row[2] != "NULL": # If this is not the genesis block
                    G.add_edge(id_to_virt[row[2]], id_to_virt[row[0]]) # Adding edge to the graph from parent to current node
    return G, virt_to_miner, miner


# This function would return the longest path in the blockchain and ratio of number of blocks generated by each peer in longest chain to total number of generated block 
def longest_chain_ratios(G, n, v_m):
    # Ratio of number of blocks generated by each peer in longest chain to total number of generated block
    ratio = [0]*n 
    # Total number of blocks generated by each peer
    total = [0]*(n+1) 
    # Number of blocks generated by each peer in longest chain
    longest = [0]*(n+1) 
    for node in G.nodes():
        total[v_m[node][0]]+=1
    for node in nx.dag_longest_path(G):
        longest[v_m[node][0]]+=1
    for i in range(n): # Calculating the ratio if total number of blocks generated by a peer is not 0
        ratio[i] = longest[i+1]/total[i+1] if total[i+1]!=0 else 'ND'
    return nx.dag_longest_path(G), longest[1:], total[1:], ratio


def mark_branch(G, node, ids, new_id):
    # get to the ancestor of the node that is part of the longest branch
    # NOTE: We have a tree so there is only one parent
    parent = list(G.predecessors(node))[0]
    while ids[parent-1] != 1:
        node = parent
        parent = list(G.predecessors(node))[0]

    # Mark the all the descendants of the node
    q = queue.Queue()
    ids[node-1] = new_id
    q.put(node)
    while not q.empty():
        curr = q.get()
        for child in G.successors(curr):
            ids[child-1] = new_id
            q.put(child)
    return

# This function would return the minimum, maximum, average and number of branches in the blockchain
def get_branch_stats(G):
    longest_branch = nx.dag_longest_path(G) # Longest branch in the blockchain
    ids = [0]*(len(G.nodes()))  # List to store the branch id of each node

    for node in longest_branch: # Marking the nodes in the longest branch
        ids[node-1]=1

    for node in G.nodes(): # Marking the nodes in the other branches
        if ids[node-1]==0: # If the node is not marked, this means it is in a different branch
            new_id = max(ids)+1 # Assigning a new branch id
            mark_branch(G, node, ids, new_id) # Marking all the nodes in the branch  

    branches = []
    # Get unique and frequency of ids list using dictionary
    for id, freq in Counter(ids).items():
        if id!=1:
            branches.append(freq)

    if len(branches) == 0:
        return 'ND','ND','ND',0
    return min(branches), max(branches), sum(branches)/len(branches), len(branches)


# This function generates the graph from the blockchain in the file and plots the graph, args is the argument parser object so as to customize the plot as per the arguments
def plot_graph(args, file="output/blockchain_1.txt"):
    if args.show_private:
        G, d, m = read_graph(True, file)
    else:
        G, d, m = read_graph(False, file)
    node_color = []
    legend_handles = []
    if args.color_same:
        node_color = ["grey"] + ["hotpink"]*(len(G.nodes())-1)
        legend_handles = [plt.Line2D([0], [0], marker='o', color='grey', label='Genesis Block', markersize=6), plt.Line2D([0], [0], marker='o', color='hotpink', label='Non-Genesis Block', markersize=6)]
    elif args.color_miner != -1:
        for i in G.nodes():
            if d[i][0] == args.color_miner:
                if d[i][1]==0:
                    node_color.append("blue")
                else:
                    node_color.append("lightblue")
            elif d[i][0] == 0:
                node_color.append("grey")
            else:
                node_color.append("hotpink")
        if args.show_private:
            legend_handles = [plt.Line2D([0], [0], marker='o', color='grey', label='Genesis Block', markersize=6), plt.Line2D([0], [0], marker='o', color='blue', label='Attacker\'s Block', markersize=6), plt.Line2D([0], [0], marker='o', color='lightblue', label='Attacker\'s Private Block', markersize=6), plt.Line2D([0], [0], marker='o', color='hotpink', label='Other Block', markersize=6)]
        else:
            legend_handles = [plt.Line2D([0], [0], marker='o', color='grey', label='Genesis Block', markersize=6), plt.Line2D([0], [0], marker='o', color='blue', label='Attacker\'s Block', markersize=6), plt.Line2D([0], [0], marker='o', color='hotpink', label='Other Block', markersize=6)]
    else:
        for i in G.nodes():
            if d[i][0]==0:
                node_color.append("grey")
            elif d[i][0]==1:
                if d[i][1]==0:
                    node_color.append("blue")
                else:
                    node_color.append("lightblue")
            elif d[i][0]==2:
                if d[i][1]==0:
                    node_color.append("orange")
                else:
                    node_color.append("gold")
            else:
                node_color.append("hotpink")
        if args.show_private:
            legend_handles = [plt.Line2D([0], [0], marker='o', color='grey', label='Genesis Block', markersize=6), plt.Line2D([0], [0], marker='o', color='blue', label='Attacker 1\'s Block', markersize=6), plt.Line2D([0], [0], marker='o', color='lightblue', label='Attacker 1\'s Private Block', markersize=6), plt.Line2D([0], [0], marker='o', color='orange', label='Attacker 2\'s Block', markersize=6), plt.Line2D([0], [0], marker='o', color='gold', label='Attacker 2\'s Private Block', markersize=6), plt.Line2D([0], [0], marker='o', color='hotpink', label='Honest Block', markersize=6)]
        else:
            legend_handles = [plt.Line2D([0], [0], marker='o', color='grey', label='Genesis Block', markersize=6), plt.Line2D([0], [0], marker='o', color='blue', label='Attacker 1\'s Block', markersize=6), plt.Line2D([0], [0], marker='o', color='orange', label='Attacker 2\'s Block', markersize=6), plt.Line2D([0], [0], marker='o', color='hotpink', label='Honest Block', markersize=6)]
    pos = graphviz_layout(G, prog="dot")
    nx.draw(G, pos, with_labels=True, node_size=200, node_color=node_color, node_shape="o", alpha=0.8, linewidths=1, font_size=8, font_color="black", font_family="monospace", edge_color="green", width=1, arrows=True, arrowsize=8, arrowstyle="-|>", connectionstyle="arc3")
    plt.legend(handles=legend_handles)
    plt.savefig('output/blockchain.png')


# This function would return aggregate ratio of number of blocks generated by each peer in longest chain to total number of generated block
def aggregate_ratio(longest, total, miners):
    l = [longest[i-1] for i in miners]
    t = [total[i-1] for i in miners]
    return sum(l)/sum(t) if sum(t)!=0 else 'ND' # Return ND if no block generated


# This function would return the number of peers who did not contribute i.e. no block generated
def no_contribution(miner_total, miners):
    return len([i for i in miners if miner_total[i-1]==0])


if __name__ == "__main__":
    # Creating ArgumentParser object
    argparser = argparse.ArgumentParser(description='Analyser for the blockchain')
    argparser.add_argument('--blkchain', type=str, default="output/blockchain_1.txt", help='File containing the blockchain')
    argparser.add_argument('--info_file', type=str, default="output/info.txt", help='File containing info about miners')
    argparser.add_argument('--only_plot', action="store_true", help="Only plot blockchain tree and exit")
    argparser.add_argument('--output', type=str, default="output/final_stats.txt", help="Output file")
    argparser.add_argument('--show_private', action="store_true", help="Show private chain as well in the plot")
    argparser.add_argument('--color_same', action="store_true", help="Color all nodes same regardless of attacker or honest miner")
    argparser.add_argument('--color_miner', type=int, default=-1, help="Color distinctly the blocks mined by the miner with this ID, works only if --color-same is not given")
    args = argparser.parse_args()

    # Make output directory if it doesn't exist
    if not os.path.exists("output"):
        os.makedirs("output")

    # Plot the blockchain tree
    plot_graph(args, args.blkchain)
    print("Blockchain tree plotted successfully")
    if args.only_plot:
        exit(0)
    
    # Check if the info file exists
    if not os.path.exists(args.info_file):
        print("No info file found")
        exit(1)
    
    # Store info about simulation parameters in sim_params and miners in a dictionary "miners" with miner ID as key and (slow, low_cpu) as value 
    # Also store the miner IDs in lists slow_low, fast_low, slow_high, fast_high
    with open(args.info_file, "r") as f:
        lines = f.readlines()
        sim_params = lines[:8]
        lines = lines[10:]
        miners = [line.strip().split(",") for line in lines]
        miners = {int(line[0]): (line[1], line[2]) for line in miners}
        attacker_1 = [k for k, v in miners.items() if v[0] == "Fast" and v[1] == "Attacker 1"]
        attacker_2 = [k for k, v in miners.items() if v[0] == "Fast" and v[1] == "Attacker 2"]
        slow_low = [k for k, v in miners.items() if v[0] == "Slow" and v[1] == "Low CPU"]
        fast_low = [k for k, v in miners.items() if v[0] == "Fast" and v[1] == "Low CPU"]
        slow_high = [k for k, v in miners.items() if v[0] == "Slow" and v[1] == "High CPU"]
        fast_high = [k for k, v in miners.items() if v[0] == "Fast" and v[1] == "High CPU"]
        n = len(miners)

    # Generate statistics
    G, d, m = read_graph(False, args.blkchain)
    chain, miner_long, miner_total, ratio = longest_chain_ratios(G, n, d)
    ra_slow_low = aggregate_ratio(miner_long, miner_total, slow_low)
    ra_fast_low = aggregate_ratio(miner_long, miner_total, fast_low)
    ra_slow_high = aggregate_ratio(miner_long, miner_total, slow_high)
    ra_fast_high = aggregate_ratio(miner_long, miner_total, fast_high)
    no_low = no_contribution(miner_total, slow_low+fast_low)
    no_high = no_contribution(miner_total, slow_high+fast_high)
    min_b, max_b, avg_b, num_b = get_branch_stats(G)

    # Write the statistics to the output file
    with open(args.output, "w") as f:
        f.write("Simulation Parameters\n")
        for line in sim_params:
            f.write(line)
        f.write("\n")
        f.write("Miner Statistics\n")
        f.write("Miner ID,Slow/Fast,Low CPU/High CPU,Number of Blocks in Longest Chain,Total Number of Blocks Generated,Ratio\n")
        for i in range(1, n+1):
            f.write(f"{i},{miners[i][0]},{miners[i][1]},{miner_long[i-1]},{miner_total[i-1]},{ratio[i-1]}\n")
        f.write(f"[Number] Slow, Low CPU miners: {len(slow_low)}\n")
        f.write(f"[Number] Fast, Low CPU miners: {len(fast_low)}\n")
        f.write(f"[Number] Slow, High CPU miners: {len(slow_high)}\n")
        f.write(f"[Number] Fast, High CPU miners: {len(fast_high)}\n")
        f.write(f"[Number] Low CPU miners: {len(slow_low)+len(fast_low)}\n")
        f.write(f"[Number] High CPU miners: {len(slow_high)+len(fast_high)}\n")
        f.write("\n")
        f.write("Overall Miner Statistics\n")
        f.write(f"[Average ratio] Slow, Low CPU miners: {ra_slow_low}\n")
        f.write(f"[Average ratio] Fast, Low CPU miners: {ra_fast_low}\n")
        f.write(f"[Average ratio] Slow, High CPU miners: {ra_slow_high}\n")
        f.write(f"[Average ratio] Fast, High CPU miners: {ra_fast_high}\n")
        f.write(f"[Number] Low CPU miners who did not contribute: {no_low}\n")
        f.write(f"[Number] High CPU miners who did not contribute: {no_high}\n")    
        f.write("\n")
        f.write("Blockchain tree Statistics\n")
        f.write(f"Minimum number of branches: {min_b}\n")
        f.write(f"Maximum number of branches: {max_b}\n")
        f.write(f"Average number of branches: {avg_b}\n")
        f.write(f"Total number of branches: {num_b}\n")
        f.write("\n")
        f.write("MPU Node Statistics\n")
        f.write(f"[adv] Attacker 1: {miner_long[0]/miner_total[0] if miner_total[0]!=0 else 'ND'}\n")
        f.write(f"[adv] Attacker 2: {miner_long[1]/miner_total[1] if miner_total[1]!=0 else 'ND'}\n")
        f.write(f"[overall] Overall: {sum(miner_long)/sum(miner_total) if sum(miner_total)!=0 else 'ND'}\n")


    print("Statistics generated successfully")
        
