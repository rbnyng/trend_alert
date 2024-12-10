import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define a function to read the last state
def read_last_state(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return file.read().strip()
    return None

# Define a function to write the current state
def write_current_state(file_path, state):
    with open(file_path, 'w') as file:
        file.write(state)

# Fetch historical data
def fetch_data(ticker, start_date='2010-01-01'):
    logging.info(f"Fetching data for {ticker}")
    return yf.download(ticker, start=start_date).reset_index()

def calculate_momentum(data):
    periods = [21, 63, 126, 252]  # 1-3-6-12 month periods in trading days
    weights = [12, 4, 2, 1]  # weights for the momentum calculation

    momentum_parts = [(data['Close'] / data['Close'].shift(period) - 1) * weight
                      for period, weight in zip(periods, weights)]

    momentum = pd.concat(momentum_parts, axis=1).sum(axis=1) / 19
    data['Momentum'] = momentum

    return data

def calculate_signals(vix_data, spy_data, vxus_data, bnd_data):
    vix_signal = vix_data['Close'].iloc[-1] < 25.00

    spy_close, spy_sma = spy_data['Close'].align(spy_data['SMA_200'], join='inner')
    spy_signal = (spy_close.iloc[-10:] > spy_sma.iloc[-10:]).all()

    vxus_signal = vxus_data['Momentum'].iloc[-1] > 0
    bnd_signal = bnd_data['Momentum'].iloc[-1] > 0

    signals = {
        'VIX <25 Signal': vix_signal,
        'SPY >200 SMA Signal': spy_signal,
        'VXUS 1-3-6-12 Signal': vxus_signal,
        'BND 1-3-6-12 Signal': bnd_signal
    }

    return signals

def determine_allocation(signals):
    true_signals = sum(signals.values())
    if true_signals == 4:
        return 'TQQQ'
    elif true_signals == 2 or true_signals == 3:
        return 'QQQ'
    else:
        return 'GLD'

def merge_data(vix_data, spy_data, vxus_data, bnd_data, tqqq_data, qqq_data, gld_data):
    merged_data = spy_data[['Date', 'Close', 'SMA_200']].merge(vix_data[['Date', 'Close']], on='Date', suffixes=('', '_VIX'))
    merged_data = merged_data.merge(vxus_data[['Date', 'Momentum']], on='Date', suffixes=('', '_VXUS'))
    merged_data = merged_data.merge(bnd_data[['Date', 'Momentum']], on='Date', suffixes=('', '_BND'))
    merged_data = merged_data.merge(tqqq_data[['Date', 'Close']], on='Date', suffixes=('', '_TQQQ'))
    merged_data = merged_data.merge(qqq_data[['Date', 'Close']], on='Date', suffixes=('', '_QQQ'))
    merged_data = merged_data.merge(gld_data[['Date', 'Close']], on='Date', suffixes=('', '_GLD'))
    merged_data.columns = ['Date', 'SPY_Close', 'SPY_SMA_200', 'VIX_Close', 'VXUS_Momentum', 'BND_Momentum', 'TQQQ_Close', 'QQQ_Close', 'GLD_Close']

    return merged_data

def check_signals_and_allocate(merged_data):
    merged_data['VIX_Signal'] = merged_data['VIX_Close'] < 25.00
    merged_data['SPY_Signal'] = (merged_data['SPY_Close'] > merged_data['SPY_SMA_200']).rolling(window=10).apply(lambda x: x.all()).astype(bool)
    merged_data['VXUS_Signal'] = merged_data['VXUS_Momentum'] > 0
    merged_data['BND_Signal'] = merged_data['BND_Momentum'] > 0

    merged_data['Allocation'] = merged_data.apply(
        lambda row: determine_allocation({
            'VIX <25 Signal': row['VIX_Signal'],
            'SPY >200 SMA Signal': row['SPY_Signal'],
            'VXUS 1-3-6-12 Signal': row['VXUS_Signal'],
            'BND 1-3-6-12 Signal': row['BND_Signal']
        }), axis=1)
    
    return merged_data

def send_email(subject, body):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    receiver_email = os.environ.get('RECEIVER_EMAIL')
    
    if not sender_email or not sender_password:
        raise ValueError("Email credentials are not set in environment variables.")
    
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = receiver_email
    message.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())

def main():
    state_file_path = 'state.txt'
    last_state = read_last_state(state_file_path)

    if os.environ.get('SEND_TEST_EMAIL') == 'true':
        send_email('Test Email', 'This is a test email.')
    
    vix_data = fetch_data('^VIX')
    spy_data = fetch_data('SPY')
    vxus_data = fetch_data('VXUS')
    bnd_data = fetch_data('BND')
    tqqq_data = fetch_data('TQQQ')
    qqq_data = fetch_data('QQQ')
    gld_data = fetch_data('GLD')

    spy_data['SMA_200'] = spy_data['Close'].rolling(window=200).mean()
    vxus_data = calculate_momentum(vxus_data)
    bnd_data = calculate_momentum(bnd_data)

    signals = calculate_signals(vix_data, spy_data, vxus_data, bnd_data)
    allocation = determine_allocation(signals)
    current_state = f'{sum(signals.values())} signals hold true. Allocation: {allocation}'
    signal_states = "\n".join([f"{signal}: {'True' if state else 'False'}" for signal, state in signals.items()])

    data_merged = merge_data(vix_data, spy_data, vxus_data, bnd_data, tqqq_data, qqq_data, gld_data)
    data_labeled = check_signals_and_allocate(data_merged)
    data_last_seven = data_labeled.iloc[-7:]
    
    data_last_seven.iloc[::-1].to_csv('last_seven_days.csv')

    if current_state != last_state:
        subject = 'TQQQ Leveraged ETF Strategy Alert'
        body = f'The market condition has changed.\n{current_state}\n\nSignal States:\n{signal_states}\n\n[Check repository](https://github.com/rbnyng/trend_alert)'
        send_email(subject, body)
        write_current_state(state_file_path, current_state)

if __name__ == '__main__':
    main()
