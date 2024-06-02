# Traffic Prediction in SDN Networks with ComNetsEmu

## Description

The goal of this project is to analyze traffic patterns and predict traffic in a Software Defined Network (SDN). The process involves capturing network traffic packets using RYU, followed by training different machine learning models to predict traffic. The project automates the setup of a network topology in Mininet, generates traffic between hosts, and captures the network traffic and configuration. This is useful for testing and analyzing network performance and behavior under various traffic patterns.

## Requirements

You can install the network emulator by following the instructions on [Prof. Granelli website] (https://www.granelli-lab.org/researches/relevant-projects/comnetsemu-labs). This virtual machine includes the Mininet emulator RYU, which are crucial to running our project.

## Getting Started

1. Clone the repository:
    ```
    git clone https://github.com/raffaa/traffic-prediction-comnetsemu.git
    ```
2. Install dependencies using pip:
    ```
    sudo pip3 install -r requirements.txt
    ```

## Usage

### Network topology and traffic generation

Build and start the topology with Mininet and generate traffic:
```
sudo python3 topology.py
```
The script allows users to build a network topology defined in the file and start generating traffic while capturing packets at each network interface. The script includes two network topologies of different complexity. One is a simple topology with two switches linearly connected and three hosts connected to each switch. The other is a more elaborate topology consisting of three switches connected in a loop, each connected to three hosts. You can define which topology you want to use on the command line.

Arguments:
1. ```--topo```: Topology configuration, 0 for simple topology, 1 for complex topology. Default is 0.
2. ```--time```: Duration of the test in seconds. Default is 30.

For example, running this command:
```
sudo python3 main.py --topo 1 --topo 40
```
The script builds a complex topology and generates traffic for 40 seconds. Note that this time does not include some possible overhead due to the configuration setup.

Note: Mininet requires this script to be run as root, therefore using ```sudo``` is mandatory.

### Traffic Prediction

TODO

## Contributions
1. Alex Vernazza
2. Martina Parenzan
3. Raffaella Perna