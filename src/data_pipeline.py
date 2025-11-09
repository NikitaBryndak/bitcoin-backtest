import pandas as pd
import warnings

warnings.filterwarnings('ignore')
class DataLoader:
    
    def load_data(filepath="./data/data.csv"):
        print("--- Loading Data... ---")
        
        try:
            df = pd.read_csv(filepath)
        except FileNotFoundError:
            raise f"No file at {filepath}"

        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        
        df.sort_index(inplace=True)
            
        # TODO: Make resampling frequency configurable
        # TODO: Do not hardcode column names
        df = df.resample('1D').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume BTC': 'sum', 
            'Volume USD': 'sum'
        }).dropna()    
        
        if df[['Open', 'High', 'Low', 'Close']].isnull().any().any():
            df.fillna(method='ffill', inplace=True)
            
        print("--- Data is loaded ---")
        return df