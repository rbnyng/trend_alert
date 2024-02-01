import pandas as pd

def apply_labels(df):
    df_copy = df.copy()
    
    df_copy['Alert'] = ''
    df_copy['Market_Condition'] = ''  
    
    for i in range(len(df_copy)):
        close = df_copy.loc[i, 'haClose']
        ema_50 = df_copy.loc[i, 'EMA_50']
        ema_200 = df_copy.loc[i, 'EMA_200']
        ha_color = df_copy.loc[i, 'HA_Color']
        hma_color = df_copy.loc[i, 'HMA_color']
        
        # Determine market condition
        if close < ema_50 and close < ema_200:
            df_copy.loc[i, 'Market_Condition'] = 'Bear'
            # Bear market conditions
            if ha_color == 'green' and hma_color in ['green', 'dark_green']:
                df_copy.loc[i, 'Alert'] = 'Long Alert (Bear)'
            elif hma_color in ['dark_orange', 'red'] or ha_color == 'red':
                df_copy.loc[i, 'Alert'] = 'Sell Alert (Bear)'
                
        elif close > ema_50 and close > ema_200:
            df_copy.loc[i, 'Market_Condition'] = 'Bull'
            # Bull market conditions
            if ha_color == 'green' and hma_color in ['green', 'dark_green']:
                df_copy.loc[i, 'Alert'] = 'Long Alert (Bull)'
            elif hma_color == 'red' or ha_color == 'red':
                df_copy.loc[i, 'Alert'] = 'Sell Alert (Bull)'
            elif hma_color == 'dark_orange':
                df_copy.loc[i, 'Alert'] = 'Orange HMA Alert (Bull)'
                
        else:
            df_copy.loc[i, 'Market_Condition'] = 'Sideways'
            # Sideways market conditions
            if ha_color == 'green' and hma_color in ['green', 'dark_green']:
                df_copy.loc[i, 'Alert'] = 'Long Alert (Sideways)'
            elif hma_color in ['dark_orange', 'red'] or ha_color == 'red':
                df_copy.loc[i, 'Alert'] = 'Sell Alert (Sideways)'

    return df_copy