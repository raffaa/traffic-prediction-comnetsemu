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
## Running the Code

To execute the traffic prediction code, use the following command in the terminal:

```
python prediction.py
```

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

```python
# DATASET PROCESSING

# Convert the 'Timestamp' column to datetime format
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Dataframe sorting based on Timestamps
df = df.sort_values(by='Timestamp')

# MAC and port columns in numerical values
df['Source MAC'] = df['Source MAC'].apply(lambda x: int(x.replace(':', ''), 16) if isinstance(x, str) else x)
df['Destination MAC'] = df['Destination MAC'].apply(lambda x: int(x.replace(':', ''), 16) if isinstance(x, str) else x)

# Protocol column in numerical values
protocol_mapping = {'TCP': 0, 'UDP': 1, 'ICMP': 2, 'Other': 3}
df['Protocol'] = df['Protocol'].map(protocol_mapping)

# Replace non-numeric and missing values with 0 (or an appropriate value)
df[['Source Port', 'Destination Port', 'Elapsed time', 'Protocol']] = df[['Source Port', 'Destination Port', 'Elapsed time', 'Protocol']].apply(pd.to_numeric, errors='coerce')
df['Length'] = pd.to_numeric(df['Length'], errors='coerce')

df = df.dropna()

# Multiply the traffic by duplicating rows
df = pd.concat([df] * 1, ignore_index=True)

# Calculate the packet counts
df['Packet Count'] = df.groupby('Timestamp').cumcount() + 1

# Calculation of the index corresponding to the last 20% of the time
time_range = df['Timestamp'].max() - df['Timestamp'].min()
time_20_percent = df['Timestamp'].min() + 0.8 * time_range

# Selection of the data before the last 20% of the time for training
train_df = df[df['Timestamp'] < time_20_percent].copy()

# Feature and target selection for the training phase
X_train = train_df[['Source MAC', 'Destination MAC', 'Source Port', 'Destination Port', 'Elapsed time', 'Protocol']]
y_train = train_df['Packet Count']
```


### Machine Learning Models

### 1. Random Forest

* **Training**: The Random Forest regression model is trained on the preprocessed training data.
  
#### Regression in Random Forest

Random Forest leverages regression techniques to predict packet counts based on a selection of input features. By constructing an ensemble of decision trees, each trained on different subsets of the data, the model enhances predictive accuracy and generalizability.

```python
# Training of Random Forest on the first 80% temporal data
regressor = RandomForestRegressor(n_estimators=100, random_state=42)
regressor.fit(X_train, y_train)
```


* **Prediction**: It generates predictions on the testing dataset.

* **Evaluation**: Performance metrics such as Mean Squared Error (MSE) and R-squared (R^2) are computed to assess the model's effectiveness.


### 2. ARIMA

* **Data Preparation for ARIMA**: Prepare the data by resampling the time series at regular intervals, a prerequisite for ARIMA modeling.

#### ARIMA: Order and Fit

ARIMA models are characterized by their (p, d, q) parameters, representing auto-regressive, integrated, and moving average components, respectively. These parameters are crucial in configuring the model's behavior and optimizing its predictive capabilities.

```python
order = (30, 1, 0)  # ARIMA order
model = ARIMA(train_ts, order=order)
model_fit = model.fit()
forecast_steps = len(test_ts)
forecast = model_fit.forecast(steps=forecast_steps)
```

  
* **Training and Forecasting**: Train the ARIMA model on the training dataset and utilize it to forecast future packet counts.

  #### Regular Interval Series for ARIMA

To ensure accurate predictions, ARIMA necessitates time series data that is resampled at regular intervals. This step standardizes the temporal granularity of the dataset, aligning it with the model's requirements for effective forecasting.

  
* **Evaluation**: Compare ARIMA's forecasted values with actual values to evaluate its predictive performance








## Contributions
* Alex Vernazza
* Martina Parenzan
* Raffaella Perna
