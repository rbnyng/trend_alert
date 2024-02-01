import pandas as pd
import numpy as np

def calculate_hma_signals(df, price_col='price', HMA_length=55, lookback=3):
    """
    Calculate Hull Moving Average (HMA) signals, concavity, and assign colors for visualization.
    
    Args:
    - df (pd.DataFrame): DataFrame containing 'high' and 'low' price columns.
    - price_col (str): Name of the column to store the average price (high+low)/2.
    - HMA_length (int): Length of the HMA.
    - lookback (int): Lookback period for calculating delta and concavity.
    
    Returns:
    - pd.DataFrame: DataFrame with added columns for HMA, concavity, turning points, buy/sell signals, divergence, and color.
    """
    def HMA(series, length):
        """Calculate Hull Moving Average (HMA) on a Pandas Series."""
        # Calculate the Weighted Moving Average (WMA) with half length
        half_length = int(length / 2)
        sqrt_length = int(np.sqrt(length))
        half_wma = series.rolling(window=half_length).apply(lambda x: np.dot(x, np.arange(1, half_length + 1)) / np.arange(1, half_length + 1).sum(), raw=True)
        
        # Calculate the WMA for the full length
        full_wma = series.rolling(window=length).apply(lambda x: np.dot(x, np.arange(1, length + 1)) / np.arange(1, length + 1).sum(), raw=True)
        
        # Calculate the difference WMA, which is 2 * half WMA - full WMA
        diff_wma = 2 * half_wma - full_wma
        
        # Calculate the WMA of the difference WMA with square root of the specified length
        hma = diff_wma.rolling(window=sqrt_length).apply(lambda x: np.dot(x, np.arange(1, sqrt_length + 1)) / np.arange(1, sqrt_length + 1).sum(), raw=True)
        
        return hma    
    
    # Calculate price and HMA
    df[price_col] = (df['High'] + df['Low']) / 2
    df['HMA'] = HMA(df[price_col], HMA_length)

    # Calculate Delta, Delta per Bar, and Next Bar
    df['delta'] = df['HMA'].shift(1) - df['HMA'].shift(lookback + 1)
    df['delta_per_bar'] = df['delta'] / lookback
    df['next_bar'] = df['HMA'].shift(1) + df['delta_per_bar']

    # Determine Concavity
    df['concavity'] = np.where(df['HMA'] > df['next_bar'], 1, -1)

    # Find Turning Points
    df['turning_point'] = np.where(df['concavity'].diff() != 0, df['HMA'], np.nan)

    # Identify Buy/Sell Signals
    # df['sell'] = np.where((~df['turning_point'].isna()) & (df['concavity'] == -1), df['High'], np.nan)
    # df['buy'] = np.where((~df['turning_point'].isna()) & (df['concavity'] == 1), df['Low'], np.nan)

    # Calculate Divergence
    # df['divergence'] = df['HMA'] - df['next_bar']

    # Assign colors based on concavity and HMA trend
    # Green: Concave Up but HMA decreasing. The 'mood' has changed and the declining trend of the HMA is slowing. 
    # Light Green: Concave up and HMA increasing. Price is increasing, and since the curve is still concave up, it is accelerating upward.
    # Orange: Concavity is now downward, and though price is still increasing, the rate has slowed, perhaps the mood has become less enthusiastic. 
    # Red: Concave down and HMA decreasing. Not good for long trades, but get ready for a turning point to enter long on again.

    conditions = [
        (df['concavity'] == -1) & (df['HMA'] > df['HMA'].shift(1)),
        (df['concavity'] == -1),
        (df['concavity'] == 1) & (df['HMA'] < df['HMA'].shift(1)),
        (df['concavity'] == 1)
    ]
    color_choices = ['dark_orange', 'red', 'dark_green', 'green']
    df['HMA_color'] = np.select(conditions, color_choices, default='none')

    return df

if __name__ == "__main__":
    print("This script is intended to be imported as a module and not run directly.")
