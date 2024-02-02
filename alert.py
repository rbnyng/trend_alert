import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from helpers.hull_moving_average_concavity import calculate_hma_signals
from helpers.smoothed_heikin_ashi import calculate_smoothed_heikin_ashi
from helpers.apply_labels import apply_labels

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

def write_last7_data(data, file_path='last_seven_days.csv'):
    data.to_csv(file_path, index=False)

# Path to the state file
state_file_path = 'state.txt'

# Read the last state
last_state = read_last_state(state_file_path)

# Check for test email environment variable
if os.environ.get('SEND_TEST_EMAIL') == 'true':
    # SMTP server configuration
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = os.environ['SENDER_EMAIL']
    sender_password = os.environ['SENDER_PASSWORD']
    receiver_email = os.environ['RECEIVER_EMAIL']

    # Create the email message
    message = MIMEMultipart()
    message['Subject'] = 'Test Email'
    message['From'] = sender_email
    message['To'] = receiver_email
    body = 'This is a test email.'
    message.attach(MIMEText(body, 'plain'))

    # Send the email
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()

# Fetch historical data
data = yf.download('QQQ', start='2000-01-01').reset_index()

data = calculate_smoothed_heikin_ashi(data)
data = calculate_hma_signals(data)
data['EMA_50'] = data['Close'].ewm(span=50, adjust=False).mean()
data['EMA_200'] = data['Close'].ewm(span=200, adjust=False).mean()
data = apply_labels(data)

latest_data = data.tail(1)

current_state = latest_data['Alert'].iloc[0] + " " + latest_data['Market_Condition'].iloc[0]

write_last7_data(data.tail(7)[['Date', 'Open', 'High', 'Low', 'Close', 'HA_Color', 'HMA_color', 'Alert', 'Market_Condition']])

if current_state != last_state:
    # change detected, send an email
    # SMTP server configuration
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    receiver_email = os.environ.get('RECEIVER_EMAIL')
    
    if not sender_email or not sender_password:
        raise ValueError("Email credentials are not set in environment variables.")
        
    # Create the email message
    message = MIMEMultipart()
    message['Subject'] = 'QQQ Market Condition Change Alert'
    message['From'] = sender_email
    message['To'] = receiver_email
    body = 'The QQQ market condition has changed.\n' + current_state
    message.attach(MIMEText(body, 'plain'))

    # Send the email
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()

    write_current_state(state_file_path, current_state)
