import warnings
import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, r2_score
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# Remove previous plots
os.system("rm -rf ./plots/*.png")
# Remove previous comulative dataset
# os.system("rm ./captures/united_traffic.csv")

print("[INFO] Removed previous files.")

# Create plot folder
plots_dir = "./plots"
if not os.path.exists(plots_dir):
    os.makedirs(plots_dir)

print("[INFO] Created plot folder.")

# DATASET UNION
folder_path = './captures'

df_list = []
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        filepath = os.path.join(folder_path, filename)
        df = pd.read_csv(filepath)
        df_list.append(df)

# File union
df = pd.concat(df_list, ignore_index=True)

# DataFrame saving in a unique CSV file
output_file_path = './captures/united_traffic.csv'
df.to_csv(output_file_path, index=False)

df = pd.read_csv(output_file_path)

# DATASET PROCESSING

# Convert the 'Timestamp' column to datetime format
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Multiply the traffic by duplicating rows
df = pd.concat([df] * 2, ignore_index=True)

# Dataframe sorting based on Timestamps
df = df.sort_values(by='Timestamp')

# MAC and port columns in numerical values
df['Source MAC'] = df['Source MAC'].apply(lambda x: int(x.replace(':', ''), 16) if isinstance(x, str) else x)
df['Destination MAC'] = df['Destination MAC'].apply(lambda x: int(x.replace(':', ''), 16) if isinstance(x, str) else x)

# Protocol column in numerical values
protocol_mapping = {'TCP': 0, 'UDP': 1, 'ICMP': 2, 'Other': 3}
df['Protocol'] = df['Protocol'].map(protocol_mapping)

# Find and drop non-numeric and missing values
df[['Source Port', 'Destination Port', 'Elapsed time', 'Protocol']] = df[['Source Port', 'Destination Port', 'Elapsed time', 'Protocol']].apply(pd.to_numeric, errors='coerce')
df['Length'] = pd.to_numeric(df['Length'], errors='coerce')

df = df.dropna()

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

# Definition of the desired sampling intervals (0.1s, 0.3s, 0.5s)
sampling_intervals = ['100L', '300L', '500L']

# RANDOM FOREST

print("[INFO] Training with Random Forest.")

# Training of Random Forest on the first 80% temporal data
regressor = RandomForestRegressor(n_estimators=100, random_state=42)
regressor.fit(X_train, y_train)

# Predictions on the last 20% temporal data
test_df = df[df['Timestamp'] >= time_20_percent].copy()
X_test = test_df[['Source MAC', 'Destination MAC', 'Source Port', 'Destination Port', 'Elapsed time', 'Protocol']]
y_test = test_df['Packet Count']
y_pred_last_20_percent = regressor.predict(X_test)

# Metrics evaluation
print("Metrics evaluation:")
mse_train = mean_squared_error(y_train, regressor.predict(X_train))
r2_train = r2_score(y_train, regressor.predict(X_train))

mse_test = mean_squared_error(y_test, y_pred_last_20_percent)
r2_test = r2_score(y_test, y_pred_last_20_percent)

print(f'Training MSE: {mse_train}, R2: {r2_train}')
print(f'Test MSE: {mse_test}, R2: {r2_test}')

# Adding predictions to the test DataFrame
test_df.loc[:, 'Predicted Packet Count'] = y_pred_last_20_percent

# Plot Random Forest
fig, axss = plt.subplots(3, 1, figsize=(18, 6))
for i, interval in enumerate(sampling_intervals):
    # Sampled Dataframe generation for train and test phases
    train_df_sampled = train_df.set_index('Timestamp').resample(interval).count().reset_index()
    test_df_sampled = test_df.set_index('Timestamp').resample(interval).count().reset_index()

    # Plot of real train data and predicted test data
    axss[i].plot(train_df_sampled['Timestamp'], train_df_sampled['Packet Count'], label='Actual Packet Count', color='blue')
    axss[i].plot(test_df_sampled['Timestamp'], test_df_sampled['Predicted Packet Count'], label='Predicted Packet Count', color='orange')
    axss[i].axvline(x=time_20_percent, linestyle='--', color='red', label='80%-20% Split')

    axss[i].set_xlabel('Timestamp')
    axss[i].set_ylabel('Packet Count')
    axss[i].set_title(f'Random Forest: Predictions vs Actual Packet Count (Sampled every {interval})')
    axss[i].legend()
    axss[i].grid(True)

plt.tight_layout()
# plt.show()
plt.savefig('./plots/random-forest.png')
print("Random Forest plot saved.")

# ARIMA

print("[INFO] Training with ARIMA.")

df_arima = df[['Timestamp', 'Packet Count']].copy()
results_arima = {}

# Perform Dickey-Fuller test on a sample of the data
sample_size = 10000
df_sample = df_arima['Packet Count'].sample(n=sample_size, random_state=42)

print(f"Statistics on a subset of size {sample_size}:")

# stationariety test (Dickey-Fuller)
result = adfuller(df_sample)
print('ADF Statistic:', result[0])
print('p-value:', result[1])
for key, value in result[4].items():
    print('Critial Values:')
    print(f'   {key}, {value}')

# Tracciare i grafici ACF e PACF
fig, ax = plt.subplots(2, 1, figsize=(12, 8))

plot_acf(df_sample, lags=40, ax=ax[0])
plot_pacf(df_sample, lags=40, ax=ax[1])
plt.tight_layout()
plt.savefig('./plots/p-acf.png')
print("ACF and PACF plot saved.")

fig, axs = plt.subplots(3, 1, figsize=(18, 6))
warnings.filterwarnings("ignore", category=UserWarning)

for i, interval in enumerate(sampling_intervals):
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

    order = (30, 0, 30)  # ARIMA order
    model = ARIMA(train_ts, order=order)
    model_fit = model.fit(method_kwargs={'maxiter':800})
    forecast_steps = len(test_ts)
    forecast = model_fit.forecast(steps=forecast_steps)

    # Dataframe generation for test set and ARIMA forecastings
    test_df_arima = pd.DataFrame({'Timestamp': test_ts.index, 'Packet Count': test_ts.values, 'ARIMA Predicted Packet Count': forecast.values})
    results_arima[interval] = test_df_arima

    # Plot of real data and predicted data: ARIMA
    axs[i].plot(df_sampled['Timestamp'], df_sampled['Packet Count'], label='Actual Packet Count', color='blue')
    axs[i].plot(test_df_arima['Timestamp'], test_df_arima['ARIMA Predicted Packet Count'], label='ARIMA Predicted Packet Count', color='orange')
    
    split_point = df_sampled['Timestamp'].iloc[train_size]
    axs[i].axvline(x=split_point, linestyle='--', color='red', label='80%-20% Split')

    axs[i].set_xlabel('Timestamp')
    axs[i].set_ylabel('Packet Count')
    axs[i].set_title(f'ARIMA: Predictions vs Actual Packet Count (Sampled every {interval})')
    axs[i].legend()
    axs[i].grid(True)

plt.tight_layout()
# plt.show()
plt.savefig('./plots/arima.png')
print("ARIMA plot saved.")

print("[INFO] Plotting comparison.")
# Plot comparison between all the last 20% predicted data (RF + ARIMA)
plt.figure(figsize=(18, 9))
for i, interval in enumerate(sampling_intervals):
    plt.subplot(3, 1, i + 1)
    
    # Random Forest
    plt.plot(test_df.set_index('Timestamp').resample(interval).count().reset_index()['Timestamp'],
             test_df.set_index('Timestamp').resample(interval).count().reset_index()['Packet Count'], label='Actual Packet Count', color='blue')
    plt.plot(test_df.set_index('Timestamp').resample(interval).count().reset_index()['Timestamp'],
             test_df.set_index('Timestamp').resample(interval).count().reset_index()['Predicted Packet Count'], label='Random Forest Predicted Packet Count', color='orange')
    
    # ARIMA
    test_df_arima = results_arima[interval]
    plt.plot(test_df_arima['Timestamp'], test_df_arima['ARIMA Predicted Packet Count'], label='ARIMA Predicted Packet Count', linestyle='--', color='green')
    
    plt.axvline(x=time_20_percent, linestyle='--', color='red', label='80%-20% Split')

    plt.xlabel('Timestamp')
    plt.ylabel('Packet Count')
    plt.title(f'Random Forest vs ARIMA Predictions (Sampled every {sampling_intervals[i]})')
    plt.legend()
    plt.grid(True)

plt.tight_layout()
# plt.show()
plt.savefig('./plots/comparison.png')
print("Compared plots saved.")

print("[INFO] Done.")