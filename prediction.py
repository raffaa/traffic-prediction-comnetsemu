#codice finale
import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, r2_score
import seaborn as sns
import numpy as np

# DATASET UNION
folder_path = 'C:\\Users\\Utente\\Desktop\\networking2\\captures-high'

df_list = []
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        filepath = os.path.join(folder_path, filename)
        df = pd.read_csv(filepath)
        df_list.append(df)

# File union
df = pd.concat(df_list, ignore_index=True)

# DataFrame saving in a unique CSV file
output_file_path = r'C:\\Users\\Utente\\Desktop\\networking2\\captures-high\\united_traffic.csv'
df.to_csv(output_file_path, index=False)

df = pd.read_csv(output_file_path)

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
df = pd.concat([df] * 2, ignore_index=True)

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

# RANDOM FOREST

# Training of Random Forest on the first 80% temporal data
regressor = RandomForestRegressor(n_estimators=100, random_state=42)
regressor.fit(X_train, y_train)

# Predictions on the last 20% temporal data
test_df = df[df['Timestamp'] >= time_20_percent].copy()
X_test = test_df[['Source MAC', 'Destination MAC', 'Source Port', 'Destination Port', 'Elapsed time', 'Protocol']]
y_test = test_df['Packet Count']
y_pred_last_20_percent = regressor.predict(X_test)

# Metrics evaluation
mse_train = mean_squared_error(y_train, regressor.predict(X_train))
r2_train = r2_score(y_train, regressor.predict(X_train))

mse_test = mean_squared_error(y_test, y_pred_last_20_percent)
r2_test = r2_score(y_test, y_pred_last_20_percent)

print(f'Training MSE: {mse_train}, R2: {r2_train}')
print(f'Test MSE: {mse_test}, R2: {r2_test}')

# Adding predictions to the test DataFrame
test_df.loc[:, 'Predicted Packet Count'] = y_pred_last_20_percent

# Definition of the desired sampling intervals (0.1s, 0.3s, 0.5s)
sampling_intervals = ['0.1s', '0.3s', '0.5s']

# Plot Random Forest
for interval in sampling_intervals:
    plt.figure(figsize=(18, 8))
    # Sampled Dataframe generation for train and test phases
    train_df_sampled = train_df.set_index('Timestamp').resample(interval).count().reset_index()
    test_df_sampled = test_df.set_index('Timestamp').resample(interval).count().reset_index()

    # Plot of real train data and predicted test data
    plt.plot(train_df_sampled['Timestamp'], train_df_sampled['Packet Count'], label='Actual Packet Count', color='blue')
    plt.plot(test_df_sampled['Timestamp'], test_df_sampled['Packet Count'], color='blue')
    plt.plot(test_df_sampled['Timestamp'], test_df_sampled['Predicted Packet Count'], label='Predicted Packet Count', color='orange')
    plt.axvline(x=time_20_percent, linestyle='--', color='red', label='80%-20% Split')

    plt.xlabel('Timestamp')
    plt.ylabel('Packet Count')
    plt.title(f'Random Forest: Predictions vs Actual Packet Count (Sampled every {interval})')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# ARIMA
df_arima = df[['Timestamp', 'Packet Count']].copy()
results_arima = {}

for interval in sampling_intervals:
    plt.figure(figsize=(18, 8))
    # Data sampling for ARIMA
    df_sampled = df_arima.set_index('Timestamp').resample(interval).count().reset_index()
    
    # Regular temporal series generation for ARIMA
    y = df_sampled['Packet Count'].values
    index_regolare = pd.date_range(start=df_sampled['Timestamp'].min(), periods=len(y), freq=interval)
    ts_regolare = pd.Series(y, index=index_regolare)

    # Training of ARIMA on the first 80% temporal data
    train_size = int(len(ts_regolare) * 0.8)
    train_ts = ts_regolare[:train_size]
    test_ts = ts_regolare[train_size:]

    # Check if train_ts and test_ts have no missing values
    train_ts.dropna(inplace=True)
    test_ts.dropna(inplace=True)

    order = (30, 1, 0)  # ARIMA order
    model = ARIMA(train_ts, order=order)
    model_fit = model.fit()
    forecast_steps = len(test_ts)
    forecast = model_fit.forecast(steps=forecast_steps)

    # Dataframe generation for test set and ARIMA forecastings
    test_df_arima = pd.DataFrame({'Timestamp': test_ts.index, 'Packet Count': test_ts.values, 'ARIMA Predicted Packet Count': forecast.values})
    results_arima[interval] = test_df_arima

    # Plot of real data and predicted data: ARIMA
    plt.plot(df_sampled['Timestamp'], df_sampled['Packet Count'], label='Actual Packet Count', color='blue')
    plt.plot(test_df_arima['Timestamp'], test_df_arima['ARIMA Predicted Packet Count'], label='ARIMA Predicted Packet Count', color='orange')
    
    split_point = df_sampled['Timestamp'].iloc[train_size]
    plt.axvline(x=split_point, linestyle='--', color='red', label='80%-20% Split')

    plt.xlabel('Timestamp')
    plt.ylabel('Packet Count')
    plt.title(f'ARIMA: Predictions vs Actual Packet Count (Sampled every {interval})')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Plot comparison between all the last 20% predicted data (RF + ARIMA)
for interval in sampling_intervals:
    plt.figure(figsize=(18, 8))
    
    # Random Forest
    plt.plot(test_df.set_index('Timestamp').resample(interval).count().reset_index()['Timestamp'],
             test_df.set_index('Timestamp').resample(interval).count().reset_index()['Packet Count'], label='Actual Packet Count', color='blue')
    plt.plot(test_df.set_index('Timestamp').resample(interval).count().reset_index()['Timestamp'],
             test_df.set_index('Timestamp').resample(interval).count().reset_index()['Predicted Packet Count'], label='RF Predicted Packet Count',  linestyle='--', color='orange')
    
    # ARIMA
    arima_test = results_arima[interval]
    plt.plot(arima_test['Timestamp'], arima_test['ARIMA Predicted Packet Count'], label='ARIMA Predicted Packet Count',  linestyle='--', color='limegreen')
    
    plt.xlabel('Timestamp')
    plt.ylabel('Packet Count')
    plt.title(f'Predictions vs Actual Packet Count (Sampled every {interval})')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
