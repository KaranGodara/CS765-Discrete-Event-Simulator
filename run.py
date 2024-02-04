import argparse
import simpy

from simulator import Simulator

def main():
    # Creating ArgumentParser object
    parser = argparse.ArgumentParser(description='Simulation of a P2P Cryptocurrency Network')

    # Adding arguments
    parser.add_argument('--n', type=int, default=10, help='Number of peers in the network')
    parser.add_argument('--z0', type=int, default=50, help='Percentage of slow peers')
    parser.add_argument('--z1', type=int, default=50, help='Percentage of peers with Low CPU')
    parser.add_argument('--T_tx', type=int, default=100, help='Mean interarrival time between transactions (in ms)')
    parser.add_argument('--I', type=int, default=1, help='Mean interarrival time between blocks (in s)')
    # note I is in secs

    # Parse the command-line arguments
    args = parser.parse_args()

    # env = simpy.Environment(factor=0.001)
    env = simpy.Environment()

    # Simulating the network
    sim = Simulator(args.n, args.z0, args.z1, args.T_tx, args.I, env)

    # Setting simulation entities
    sim.start_simulation()

    # Starting simulation
    env.run(until=10000)

if __name__ == "__main__":
    main()
