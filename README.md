# CS765-Discrete-Event-Simulator

## Team Members 
| Name | Roll Number |
| --- | --- |
|Guramrit Singh | 210050061|
|Isha Arora | 210050070|
|Karan Godara | 210050082|

## Running instructions
- The simulator and analyser are written in Python3

### Simulator
- The simulator is run by run.py
- To see the usage of the simulator, run the following command:
```python3 run.py --help```
- The above command will display the following:
```
usage: run.py [-h] [--info] [--n N] [--z0 Z0] [--z1 Z1] [--T_tx T_TX] [--I I] [--T_sim T_SIM]

Simulation of a P2P Cryptocurrency Network

options:
  -h, --help     show this help message and exit
  --info         Generate info
  --n N          Number of peers in the network
  --z0 Z0        Percentage of slow peers
  --z1 Z1        Percentage of peers with Low CPU
  --T_tx T_TX    Mean interarrival time between transactions (in ms)
  --I I          Mean interarrival time between blocks (in s)
  --T_sim T_SIM  Simulation time (in s)
```
- Options are given default values, so if you want to run the simulator with the default values, you can simply run:
```python3 run.py```
- The default values are:
    - n: 50
    - z0: 50
    - z1: 50
    - T_tx: 1000
    - I: 25
    - T_sim: 200
- The output of the simulator will be stored in the output directory. The following files will be generated:
    - blockchain_{i}.txt: The blockchain of the i-th miner, 1<=i<=n
    - info.txt: The info about the miners if --info flag is used, this file is required for the analyser

### Analyser
- The analysis of simulator is done by analyser.py
- To see the usage of the analyser, run the following command:
```python3 analyser.py --help```
- The above command will display the following:
```
usage: analyser.py [-h] [--blkchain BLKCHAIN] [--info_file INFO_FILE] [--only_plot] [--output OUTPUT]

Analyser for the blockchain

options:
  -h, --help            show this help message and exit
  --blkchain BLKCHAIN   File containing the blockchain
  --info_file INFO_FILE
                        File containing info about miners
  --only_plot           Only plot blockchain tree and exit
  --output OUTPUT       Output file
```
- Options are given default values, so if you want to run the analyser with the default values, you can simply run:
```python3 analyser.py```
- The default values are:
  - blkchain: output/blockchain_1.txt
  - info_file: output/info.txt
  - output: output/final_stats.txt
- The output of the simulator will be stored in the output directory. The following files will be generated:
    - blockchain.png: The blockchain tree corresponding to the blockchain file
    - final_stats.txt: The final stats of the blockchain if --only_plot flag is not used
