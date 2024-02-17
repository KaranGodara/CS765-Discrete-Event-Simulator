import argparse
import simpy
import os

from simulator import Simulator

def main():
    # Creating ArgumentParser object
    parser = argparse.ArgumentParser(description='Simulation of a P2P Cryptocurrency Network')

    # Adding arguments
    parser.add_argument('--info', action="store_true", help='Generate info')
    parser.add_argument('--n', type=int, default=50, help='Number of peers in the network')
    parser.add_argument('--z0', type=int, default=50, help='Percentage of slow peers')
    parser.add_argument('--z1', type=int, default=50, help='Percentage of peers with Low CPU')
    parser.add_argument('--T_tx', type=int, default=1000, help='Mean interarrival time between transactions (in ms)')
    parser.add_argument('--I', type=float, default=25, help='Mean interarrival time between blocks (in s)')
    parser.add_argument('--T_sim', type=int, default=200, help='Simulation time (in s)')
    # note I is in secs

    # Parse the command-line arguments
    args = parser.parse_args()

    # env = simpy.Environment(factor=0.001)
    env = simpy.Environment()

    # Simulating the network
    sim = Simulator(args.n, args.z0, args.z1, args.T_tx, args.I, args.T_sim, env)

    # Setting simulation entities
    sim.start_simulation()

    # Starting simulation
    env.run(until=args.T_sim * 1000)

    print("Simulation finished")

    # Make output directory if it doesn't exist
    if not os.path.exists("output"):
        os.makedirs("output")

    # Printing the blockchain of all peers
    sim.print_blockchain()

    # Generating miner info and simulation's parameters
    if args.info:
        sim.generate_info("output/info.txt")

if __name__ == "__main__":
    main()
