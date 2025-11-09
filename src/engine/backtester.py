from typing import List
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from strategies import BaseStrategy

class Backtester:
    def __init__(self, df: pd.DataFrame, strategies: List[BaseStrategy], initial_capital=10000.0, fee=0.001):
        self.df = df
        self.strategies = strategies
        self.initial_capital = initial_capital
        self.fee = fee
        self.returns = None
        
    def plot_equity(self) -> None:
        if self.returns is None:
            raise "Run .run() first"
        
        plt.figure(figsize=(12,6))
        for strategy in self.strategies:
            strategy_name = strategy.__class__.__name__
            self.returns[f'Strategy_Equity_{strategy_name}'].plot()
            
        plt.legend([s.__class__.__name__ for s in self.strategies])
        plt.title("Equity - For strategies")
        plt.ylabel('Portfolio size ($)')
        plt.xlabel('Date')
        plt.show()
         
    def run(self) -> None:
        print("--- BackTester running ---")
        for i, strategy in enumerate(self.strategies):
            print(f"--- Running Strategy {i+1}/{len(self.strategies)}: {strategy.__class__.__name__} ---")
            print(strategy)
            
            df = strategy.generate_features(self.df)
            df = strategy.generate_signals(df)

            strategy_name = strategy.__class__.__name__

            df[f'Returns_{strategy_name}'] = df['Close'].pct_change()
            df[f'Position_{strategy_name}'] = df['Signal'].shift(1).fillna(0)
            df[f'Trades_{strategy_name}'] = df[f'Position_{strategy_name}'].diff().abs()
            df[f'Strategy_Returns_{strategy_name}'] = (df[f'Returns_{strategy_name}'] * df[f'Position_{strategy_name}']) - (self.fee * df[f'Trades_{strategy_name}'])
            df[f'Strategy_Equity_{strategy_name}'] = (1 + df[f'Strategy_Returns_{strategy_name}']).cumprod() * self.initial_capital
            print(f"--- Strategy {i+1} completed ---")
            
        print("--- BackTester ended running ---")
        
        self.returns = df
        
    def get_metrics(self):
        if self.returns is None:
            raise "Run .run() first"
        stats = {
            "Total Return": [],
            "Annualized Return": [],
            "Annualized Volatility": [],
            "Max Drawdown": [],
            "Sharpe Ratio": []
        }
        self.returns.dropna(inplace=True)
        for strategy in self.strategies:
            strategy_name = strategy.__class__.__name__
            equity = self.returns[f'Strategy_Equity_{strategy_name}']

            total_return = (equity.iloc[-1] / equity.iloc[0]) - 1
            
            peak = equity.cummax()
            
            drawdown = (equity - peak) / peak
            max_drawdown = drawdown.min()
            
            length = (equity.index[-1] - equity.index[0]).days / 365.25
            annualised_return = (1 + total_return) ** (1 / length) - 1
            annualised_volatility = self.returns[f'Strategy_Returns_{strategy_name}'].std() * np.sqrt(365)
            
            sharpe_ratio = annualised_return / annualised_volatility
            stats["Total Return"].append(f"{total_return * 100:.2f}%")
            stats["Annualized Return"].append(f"{annualised_return * 100:.2f}%")
            stats["Annualized Volatility"].append(f"{annualised_volatility * 100:.2f}%")
            stats["Max Drawdown"].append(f"{max_drawdown * 100:.2f}%")
            stats["Sharpe Ratio"].append(f"{sharpe_ratio:.2f}")

        metrics_df = pd.DataFrame(stats, index=[s.__class__.__name__ for s in self.strategies])
        return metrics_df.to_dict(orient='index')