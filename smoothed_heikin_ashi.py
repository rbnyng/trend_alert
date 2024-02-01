import pandas as pd

""" def heikin_ashi(df):
    c = ['Open', 'High', 'Low', 'Close']
    ha = df.copy()
    ha['Close'] = (df[c].sum(axis=1)) / 4
    ha['Open'] = (df['Open'].shift(1) + df['Close'].shift(1)) / 2
    ha['High'] = df[c].max(axis=1)
    ha['Low'] = df[c].min(axis=1)
    return ha.dropna()

def smoothed_heikin_ashi(df, n=20, ma_type='EMA'):
    sha = pd.DataFrame(index=df.index, columns=['Open', 'High', 'Low', 'Close'])
    alpha = 2 / (1 + n)
    
    if ma_type.lower() == 'sma':
        alpha = 1 / n
    
    sha['Open'] = df['Open'].ewm(alpha=alpha, adjust=False).mean()
    sha['High'] = df['High'].ewm(alpha=alpha, adjust=False).mean()
    sha['Low'] = df['Low'].ewm(alpha=alpha, adjust=False).mean()
    sha['Close'] = df['Close'].ewm(alpha=alpha, adjust=False).mean()

    return heikin_ashi(sha)
 """

def heikin_ashi_color(haOpen, haClose):
    if haClose > haOpen:
        return 'green'
    elif haClose < haOpen:
        return 'red'
    else:
        return 'doji'
    
def calculate_smoothed_heikin_ashi(data, period=20):
    """
    Calculate Heikin-Ashi values (Open, Close, Low, High) based on Exponential Moving Averages (EMAs)
    of the original Open, Close, Low, and High prices over the specified period.
    
    Args:
    - data (pd.DataFrame): DataFrame containing 'Open', 'Close', 'High', 'Low' columns.
    - period (int): Period over which to calculate the EMAs.
    
    Returns:
    - pd.DataFrame: Original DataFrame with added columns for Heikin-Ashi values and EMAs.
    """
    # Calculate EMAs
    data['openMA'] = data['Open'].ewm(span=period, adjust=False).mean()
    data['closeMA'] = data['Close'].ewm(span=period, adjust=False).mean()
    data['highMA'] = data['High'].ewm(span=period, adjust=False).mean()
    data['lowMA'] = data['Low'].ewm(span=period, adjust=False).mean()

    # Initialize haOpen and haClose columns and calculate haClose
    data['haOpen'] = 0.0
    data['haClose'] = (data['openMA'] + data['highMA'] + data['lowMA'] + data['closeMA']) / 4.0

    # Compute haOpen using a loop to utilize its previous values
    for i in range(1, len(data)):
        data.loc[i, 'haOpen'] = (data.loc[i - 1, 'haOpen'] + data.loc[i - 1, 'haClose']) / 2.0

    # Correcting the first row for haOpen based on the user's logic
    data.loc[0, 'haOpen'] = data.loc[0, 'Open']

    # Calculate haLow and haHigh
    data['haLow'] = data[['lowMA', 'haOpen']].min(axis=1)
    data['haHigh'] = data[['highMA', 'haOpen']].max(axis=1)

    data['HA_Color'] = data.apply(lambda row: heikin_ashi_color(row['haOpen'], row['haClose']), axis=1)
    
    return data

if __name__ == "__main__":
    print("This script is intended to be imported as a module and not run directly.")
