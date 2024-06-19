# Traffic Prediction in SDN Networks with ComNetsEmu

## Description

The goal of this project is to analyze traffic patterns and predict traffic in a Software Defined Network (SDN). The process involves capturing network traffic packets using RYU, followed by training different machine learning models to predict traffic. The project automates the setup of a network topology in Mininet, generates traffic between hosts, and captures the network traffic and configuration. This is useful for testing and analyzing network performance and behavior under various traffic patterns.

## Requirements

You can install the network emulator by following the instructions on [Prof. Granelli website](https://www.granelli-lab.org/researches/relevant-projects/comnetsemu-labs). This virtual machine includes the Mininet emulator RYU, which are crucial to running our project.

Developed and tested on **Python 3.8.10**.

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

## Traffic Prediction with Machine Learning Models

### Dataset

The dataset utilized in this project comprises CSV files containing network traffic captures. Each file contains valuable information such as timestamps, source and destination MAC addresses, ports, elapsed time, protocol types, and packet lengths.

### Dataset Processing

#### Data Loading and Union

To begin, we load multiple CSV files, each representing different network traffic captures, and merge them into a cohesive DataFrame. This step ensures that we have a comprehensive dataset to work with, combining data from various sources for a holistic analysis.

#### Data Cleaning and Transformation

Before applying machine learning models, it's crucial to clean and transform the dataset to ensure its quality and relevance:

1. **Timestamps**: Convert timestamps to a datetime format, enabling chronological analysis and time-based predictions.

2. **MAC Addresses and Ports**: Convert MAC addresses and port numbers into numerical values. This conversion facilitates computational operations and statistical analysis on these attributes.

3. **Protocol Mapping**: Map protocol types (e.g., TCP, UDP, ICMP) to numerical values. This transformation allows the models to process categorical data effectively.

4. **Handling Missing Values**: Remove rows with non-numeric or missing values. This ensures that our models are trained on complete and reliable data, minimizing potential biases or inaccuracies.

5. **Feature Engineering**: Enhance the dataset by creating additional features that might improve prediction accuracy. For instance, calculating packet counts or deriving new metrics based on network traffic patterns.

### Machine Learning Models

### 1. Random Forest

* **Training**: The Random Forest regression model is trained on the preprocessed training data.
* **Prediction**: It generates predictions on the testing dataset.
* **Evaluation**: Performance metrics such as Mean Squared Error (MSE) and R-squared (R^2) are computed to assess the model's effectiveness.

#### Regression in Random Forest

Random Forest leverages regression techniques to predict packet counts based on a selection of input features. By constructing an ensemble of decision trees, each trained on different subsets of the data, the model enhances predictive accuracy and generalizability.

### 2. ARIMA

* **Data Preparation for ARIMA**: Prepare the data by resampling the time series at regular intervals, a prerequisite for ARIMA modeling.
  
* **Training and Forecasting**: Train the ARIMA model on the training dataset and utilize it to forecast future packet counts.
  
* **Evaluation**: Compare ARIMA's predictions against actual values to evaluate its predictive performance.

#### ARIMA: Order and Fit

ARIMA models are characterized by their (p, d, q) parameters, representing auto-regressive, integrated, and moving average components, respectively. These parameters are crucial in configuring the model's behavior and optimizing its predictive capabilities.

#### Regular Interval Series for ARIMA

To ensure accurate predictions, ARIMA necessitates time series data that is resampled at regular intervals. This step standardizes the temporal granularity of the dataset, aligning it with the model's requirements for effective forecasting.







## Contributions
* Alex Vernazza
* Martina Parenzan
* Raffaella Perna
