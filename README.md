# Traffic Prediction in SDN Networks with ComNetsEmu

## Description

The goal of this project is to analyze traffic patterns and predict traffic in a Software Defined Network (SDN). The process involves capturing network traffic packets using RYU, followed by training different machine learning models to predict traffic. The project automates the setup of a network topology in Mininet, generates traffic between hosts, and captures the network traffic and configuration. This is useful for testing and analyzing network performance and behavior under various traffic patterns.

## Requirements

You can install the network emulator by following the instructions on [Prof. Granelli website](https://www.granelli-lab.org/researches/relevant-projects/comnetsemu-labs). This virtual machine includes the Mininet emulator RYU, which are crucial to running our project.

## Getting Started

* Clone the repository:
    ```
    git clone https://github.com/raffaa/traffic-prediction-comnetsemu.git
    ```
* Install dependencies using pip:
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
* ```--topo```: Topology configuration, 0 for simple topology, 1 for complex topology. Default is 0.
* ```--time```: Duration of the test in seconds. Default is 30.

For example, running this command:
```
sudo python3 main.py --topo 1 --topo 40
```
The script builds a complex topology and generates traffic for 40 seconds. Note that this time does not include some possible overhead due to the configuration setup.

Note: Mininet requires this script to be run as root, therefore using ```sudo``` is mandatory.

## Traffic Prediction with Machine learning Models

This repository contains Python scripts for predicting network traffic using machine learning techniques. The main focus is on comparing the performance of Random Forest and ARIMA models in predicting network traffic.

### Dataset

The dataset used in this project consists of network traffic captures stored in CSV files. These files contain information such as timestamps, source and destination MAC addresses, ports, elapsed time, protocol, and packet lengths.

### Dataset Processing

**Data Loading and Union:** Multiple CSV files containing network traffic captures are loaded and merged into a single DataFrame.


**Data Cleaning and Transformation:**
Timestamps are converted to datetime format.
MAC addresses and ports are converted to numerical values.
Protocol column is mapped to numerical values.
Non-numeric and missing values are replaced with appropriate values.


**Temporal Splitting:** The dataset is split into training and testing sets, with the training set containing the first 80% of the temporal data and the testing set containing the last 20%.


## Machine Learning Models

### 1. Random Forest

* **Training**: Random Forest regression model is trained on the training data.
* **Prediction**: Predictions are made on the testing data.
* **Evaluation**: Mean Squared Error (MSE) and R-squared (R^2) scores are computed to evaluate the model's performance.
  
### 2. ARIMA

* **Data Preparation**: Data is resampled similarly to Prophet for ARIMA modeling.
* **Training:** ARIMA model is trained on the training data.
* **Prediction:** Predictions are made on the testing data.
* **Evaluation:** Predictions are compared against actual values to assess model performance.

## Results Visualization



## Contributions
* Alex Vernazza
* Martina Parenzan
* Raffaella Perna
