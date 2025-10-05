## Baseline code for Financial analysis from FinViz data
## S.M. Laignel - 8 Oct 24
## No validation carried out yet - ohlc graph is not working

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf
from typing import List, Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Universe:
    """
    Base class representing a universe of stocks loaded from a CSV file.
    Provides common preprocessing and utility methods.
    """
    def __init__(self, data_path: str):
        """
        Initialize the Universe with data from the specified CSV file.

        Args:
            data_path (str): Path to the CSV file containing stock data.
        """
        self.data = pd.read_csv(data_path)
        self.preprocess_data()

    def preprocess_data(self):
        """
        Preprocess the loaded data by cleaning column names, removing unwanted characters,
        converting columns to numeric types, and dropping rows with missing essential data.
        """
        # Strip whitespace from column headers
        self.data.columns = self.data.columns.str.strip()

        # Remove commas, percentage signs, and other non-numeric characters from numeric columns
        self.data.replace({',': '', '%': ''}, regex=True, inplace=True)

        # Define numeric columns to convert
        numeric_columns = [
            'Price', '20-Day Simple Moving Average', '50-Day Simple Moving Average',
            '200-Day Simple Moving Average', 'Volume', 'Average Volume', 'Market Cap',
            'Current Ratio', 'Profit Margin', 'Return on Assets', 'Return on Equity',
            'LT Debt/Equity', 'P/E', 'P/B', 'EPS (ttm)'
        ]

        # Convert columns to numeric types, coercing errors to NaN
        for col in numeric_columns:
            if col in self.data.columns:
                self.data[col] = pd.to_numeric(self.data[col], errors='coerce')

        # Define essential columns that must not have NaN values
        essential_columns = [
            'Ticker', 'Price', '20-Day Simple Moving Average',
            '50-Day Simple Moving Average', '200-Day Simple Moving Average',
            'Volume', 'Average Volume', 'Market Cap'
        ]

        # Drop rows with NaN in essential columns
        self.data.dropna(subset=essential_columns, inplace=True)
        self.data.reset_index(drop=True, inplace=True)

    def describe(self):
        """
        Print a statistical summary and the first few rows of the dataset.
        """
        print(self.data.describe())
        print(self.data.head())

    def score_and_get_top(self, scoring_criteria: str, ascending: bool = True, top_n: int = 10, data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Score the stocks based on the specified criteria and return the top N stocks.

        Args:
            scoring_criteria (str): The column name to base the scoring on.
            ascending (bool): Whether a lower score is better. True for ascending, False for descending.
            top_n (int): Number of top stocks to return.
            data (Optional[pd.DataFrame]): DataFrame to score. If None, uses the entire dataset.

        Returns:
            pd.DataFrame: Top N stocks based on the scoring criteria.
        """
        if data is None:
            data = self.data
        data = data.copy()  # Avoid SettingWithCopyWarning
        data['Score'] = data[scoring_criteria].rank(ascending=ascending, method='first')
        top_stocks = data.nsmallest(top_n, 'Score') if ascending else data.nlargest(top_n, 'Score')
        return top_stocks

    def components(self) -> List[str]:
        """
        Get the list of stock tickers in the universe.

        Returns:
            List[str]: List of ticker symbols.
        """
        return self.data['Ticker'].tolist()

    def profile(self, tickers: Optional[List[str]] = None, universe_name: Optional[str] = "Universe Components"):
        """
        Plot a scatter plot of volatility vs. cumulative return and compare portfolio performance against SPY.

        The OHLC plot for the portfolio is generated separately using mplfinance.

        Args:
            tickers (Optional[List[str]]): List of ticker symbols to profile. 
                                           If None, profiles all components.
            universe_name (Optional[str]): Name of the sub-universe for the plot titles.
        """
        if tickers is None:
            tickers = self.components()

        if not tickers:
            print("No tickers provided for profiling.")
            return

        # Initialize lists to store volatility and returns
        volatilities = []
        returns = []
        valid_tickers = []

        # Define date range: last 3 months
        end_date = datetime.today()
        start_date = end_date - relativedelta(months=3)
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        # Download historical data for all tickers at once to optimize performance
        try:
            # Set auto_adjust=False to retain 'Adj Close'
            stock_data = yf.download(tickers, start=start_str, end=end_str, progress=False, group_by='ticker', auto_adjust=False)
        except Exception as e:
            print(f"Error downloading data for tickers: {e}")
            return

        for ticker in tickers:
            try:
                if len(tickers) == 1:
                    data = stock_data
                else:
                    if ticker not in stock_data.columns.levels[0]:
                        print(f"Ticker {ticker} data not found in downloaded data.")
                        continue
                    data = stock_data[ticker]
                if not data.empty:
                    # Ensure 'Adj Close' exists
                    if 'Adj Close' not in data.columns:
                        raise KeyError("'Adj Close' column missing.")

                    # Calculate daily returns
                    data['Daily_Return'] = data['Adj Close'].pct_change(fill_method=None)
                    # Calculate volatility (standard deviation of daily returns)
                    volatility = data['Daily_Return'].std()
                    # Calculate cumulative return over the period
                    cumulative_return = (data['Daily_Return'] + 1).prod() - 1

                    volatilities.append(volatility)
                    returns.append(cumulative_return)
                    valid_tickers.append(ticker)
            except Exception as e:
                print(f"Error processing {ticker}: {e}")

        if not valid_tickers:
            print("No valid tickers to profile after processing.")
            return

        # Prepare subplots: 1 row, 2 columns
        fig, axs = plt.subplots(1, 2, figsize=(18, 7))

        # ------------------ Scatter Plot ------------------
        axs[0].scatter(volatilities, returns, alpha=0.7)
        for i, ticker in enumerate(valid_tickers):
            axs[0].annotate(ticker, (volatilities[i], returns[i]), fontsize=9)
        axs[0].set_xlabel('Volatility (Std Dev of Daily Returns)')
        axs[0].set_ylabel('Cumulative Return (Last 3 Months)')
        axs[0].set_title(f'Volatility vs. Return for {universe_name}')
        axs[0].grid(True)

        # ------------------ Portfolio vs SPY Plot ------------------
        # Include SPY in the list for benchmark comparison
        portfolio_tickers = valid_tickers  # Use only valid tickers
        benchmark_ticker = 'SPY'
        all_tickers = portfolio_tickers + [benchmark_ticker]

        # Download historical data for portfolio and SPY
        try:
            portfolio_data = yf.download(all_tickers, start=start_str, end=end_str, progress=False, auto_adjust=False)
        except Exception as e:
            print(f"Error downloading portfolio and benchmark data: {e}")
            axs[1].text(0.5, 0.5, 'Error downloading data.', horizontalalignment='center', verticalalignment='center', fontsize=12)
            axs[1].set_title(f'Portfolio vs SPY for {universe_name}')
            axs[1].axis('off')
        else:
            if len(all_tickers) == 1:
                portfolio_close = portfolio_data['Close']
            else:
                portfolio_close = portfolio_data['Close']

            # Separate portfolio stocks and benchmark
            if benchmark_ticker not in portfolio_close.columns:
                print(f"Benchmark ticker {benchmark_ticker} not found in downloaded data.")
                axs[1].text(0.5, 0.5, f'{benchmark_ticker} data not available.', horizontalalignment='center', verticalalignment='center', fontsize=12)
                axs[1].set_title(f'Portfolio vs SPY for {universe_name}')
                axs[1].axis('off')
            else:
                # Drop benchmark from portfolio stocks
                portfolio_close = portfolio_close.drop(columns=[benchmark_ticker], errors='ignore')

                if portfolio_close.empty:
                    print("No portfolio stocks data available.")
                    axs[1].text(0.5, 0.5, 'No portfolio stocks data available.', horizontalalignment='center', verticalalignment='center', fontsize=12)
                    axs[1].set_title(f'Portfolio vs SPY for {universe_name}')
                    axs[1].axis('off')
                else:
                    # Calculate daily returns for portfolio stocks
                    portfolio_returns = portfolio_close.pct_change(fill_method=None).dropna()

                    if portfolio_returns.empty:
                        print("No portfolio returns calculated.")
                        axs[1].text(0.5, 0.5, 'No portfolio returns calculated.', horizontalalignment='center', verticalalignment='center', fontsize=12)
                        axs[1].set_title(f'Portfolio vs SPY for {universe_name}')
                        axs[1].axis('off')
                    else:
                        # Calculate equally weighted portfolio returns
                        equally_weighted_returns = portfolio_returns.mean(axis=1)

                        # Calculate cumulative returns
                        portfolio_cumulative = (equally_weighted_returns + 1).cumprod()

                        # Calculate SPY returns
                        spy_data = portfolio_data['Adj Close'][benchmark_ticker].pct_change(fill_method=None).dropna()
                        spy_cumulative = (spy_data + 1).cumprod()

                        # Align the two series
                        combined_df = pd.concat([portfolio_cumulative, spy_cumulative], axis=1, join='inner')
                        combined_df.columns = ['Portfolio', 'SPY']

                        if combined_df.empty:
                            print("No overlapping dates between portfolio and SPY data.")
                            axs[1].text(0.5, 0.5, 'No overlapping dates for comparison.', horizontalalignment='center', verticalalignment='center', fontsize=12)
                            axs[1].set_title(f'Portfolio vs SPY for {universe_name}')
                            axs[1].axis('off')
                        else:
                            # Plot the cumulative returns
                            axs[1].plot(combined_df.index, combined_df['Portfolio'], label='Equally Weighted Portfolio')
                            axs[1].plot(combined_df.index, combined_df['SPY'], label='SPY Benchmark')
                            axs[1].set_xlabel('Date')
                            axs[1].set_ylabel('Cumulative Return')
                            axs[1].set_title(f'Portfolio vs SPY for {universe_name}')
                            axs[1].legend()
                            axs[1].grid(True)

        plt.tight_layout()
        plt.show()

        # ------------------ OHLC Plot for Portfolio ------------------
        # Calculate daily OHLC values for the portfolio
        try:
            # Ensure portfolio_close has data
            if 'Portfolio' in locals() and not combined_df.empty:
                # Create a DataFrame for the portfolio's daily returns
                portfolio_daily_returns = equally_weighted_returns

                # Calculate the portfolio's daily price assuming starting value of $100
                portfolio_price = (1 + portfolio_daily_returns).cumprod() * 100

                # Create OHLC data
                portfolio_ohlc = portfolio_price.resample('D').ohlc()
                portfolio_ohlc.dropna(inplace=True)

                # Alternatively, calculate OHLC using resampling if you have intraday data
                # Here, since we have daily data, OHLC will be the same as Open and Close
                # To simulate OHLC, we can shift the prices
                portfolio_ohlc = pd.DataFrame({
                    'Open': portfolio_price.shift(1),
                    'High': portfolio_price.rolling(window=2).max(),
                    'Low': portfolio_price.rolling(window=2).min(),
                    'Close': portfolio_price
                }).dropna()

                # Plot OHLC using mplfinance
                mpf.plot(
                    portfolio_ohlc,
                    type='ohlc',
                    style='charles',
                    title=f'OHLC for Equally Weighted Portfolio in {universe_name}',
                    ylabel='Portfolio Value ($)',
                    volume=False,
                    show_nontrading=False
                )
            else:
                print("Portfolio data not available for OHLC plotting.")
        except Exception as e:
            print(f"Error generating OHLC plot for portfolio: {e}")


# High Momentum Sub-Class
class HighMomentumUniverse(Universe):
    """
    Subclass of Universe to identify high momentum stocks based on specific criteria.
    """
    def __init__(self, data_path: str):
        super().__init__(data_path)

    def calculate_high_momentum(self) -> pd.DataFrame:
        """
        Calculate high momentum scores and return the top 10 high momentum stocks.

        Returns:
            pd.DataFrame: Top 10 high momentum stocks.
        """
        required_columns = [
            'Price', '20-Day Simple Moving Average', '50-Day Simple Moving Average',
            '200-Day Simple Moving Average', 'Volume', 'Average Volume', 'Market Cap'
        ]
        for column in required_columns:
            if column not in self.data.columns:
                raise KeyError(f"Column '{column}' not found in data")

        # Define high momentum criteria
        self.data['Above_SMA20'] = self.data['Price'] > self.data['20-Day Simple Moving Average']
        self.data['MA_Hierarchy'] = (
            (self.data['20-Day Simple Moving Average'] > self.data['50-Day Simple Moving Average']) & 
            (self.data['50-Day Simple Moving Average'] > self.data['200-Day Simple Moving Average'])
        )
        self.data['Relative_Volume'] = self.data['Volume'] / self.data['Average Volume']
        self.data['High_Momentum_Score'] = (
            self.data['Above_SMA20'].astype(int) + 
            self.data['MA_Hierarchy'].astype(int) + 
            (self.data['Relative_Volume'] > 1).astype(int)
        )

        # Get top 10 high momentum stocks
        high_momentum_stocks = self.score_and_get_top(
            scoring_criteria='High_Momentum_Score', 
            ascending=False, 
            top_n=10
        )
        return high_momentum_stocks


# Mean Reversion Sub-Class
class MeanReversionUniverse(Universe):
    """
    Subclass of Universe to identify mean-reverting stocks based on specific criteria.
    """
    def __init__(self, data_path: str):
        super().__init__(data_path)

    def calculate_mean_reversion(self, window: int = 20) -> pd.DataFrame:
        """
        Calculate mean reversion scores and return the top 10 mean-reverting stocks.
        Limits yfinance calls to 10 stocks.

        Args:
            window (int): Rolling window size for moving average calculation.

        Returns:
            pd.DataFrame: Top 10 mean-reverting stocks.
        """
        if 'Price' not in self.data.columns:
            raise KeyError("Column 'Price' not found in data")

        # Initial candidate selection based on existing data
        candidates = self.data.copy()
        candidates['Price_Change'] = candidates['Price'] / candidates['20-Day Simple Moving Average'] - 1
        # Select top 10 candidates with lowest Price_Change (i.e., most below SMA20)
        candidates = candidates.sort_values('Price_Change').head(10)
        tickers = candidates['Ticker'].tolist()

        mean_reversion_scores = []
        for ticker in tickers:
            try:
                # Download historical data for a valid period
                stock_data = yf.download(
                    ticker, 
                    start=(datetime.today() - relativedelta(months=3)).strftime('%Y-%m-%d'),
                    end=datetime.today().strftime('%Y-%m-%d'), 
                    progress=False, 
                    auto_adjust=False
                )
                if not stock_data.empty and len(stock_data) >= window:
                    # Calculate moving average and deviation
                    stock_data['Moving_Avg'] = stock_data['Adj Close'].rolling(window=window).mean()
                    stock_data['Deviation'] = stock_data['Adj Close'] - stock_data['Moving_Avg']
                    latest_deviation = stock_data['Deviation'].iloc[-1]
                    mean_reversion_scores.append({
                        'Ticker': ticker, 
                        'Mean_Reversion_Score': -abs(latest_deviation)
                    })
                else:
                    mean_reversion_scores.append({
                        'Ticker': ticker, 
                        'Mean_Reversion_Score': np.nan
                    })
            except Exception as e:
                print(f"Error processing {ticker}: {e}")
                mean_reversion_scores.append({
                    'Ticker': ticker, 
                    'Mean_Reversion_Score': np.nan
                })

        scores_df = pd.DataFrame(mean_reversion_scores).dropna()
        if scores_df.empty:
            print("No valid mean reversion scores calculated.")
            return pd.DataFrame()

        merged_df = pd.merge(self.data, scores_df, on='Ticker')
        mean_reverting_stocks = merged_df.nsmallest(10, 'Mean_Reversion_Score')
        return mean_reverting_stocks


# Undervalued Stocks Sub-Class
class UndervaluedUniverse(Universe):
    """
    Subclass of Universe to identify undervalued stocks based on specific financial metrics.
    """
    def __init__(self, data_path: str):
        super().__init__(data_path)

    def calculate_undervalued_stocks(self) -> pd.DataFrame:
        """
        Identify undervalued stocks based on predefined financial thresholds
        and return the top 10 undervalued stocks.

        Returns:
            pd.DataFrame: Top 10 undervalued stocks.
        """
        thresholds = {
            'Current Ratio': 1.5,          # Should be greater than 1.5
            'Profit Margin': 0,            # Should be positive
            'Return on Assets': 0.05,      # Should be greater than 5%
            'Return on Equity': 0.10,      # Should be greater than 10%
            'LT Debt/Equity': 0.5,         # Should be less than 0.5
            'P/E': 0,                       # Should be positive
            'P/B': 1,                       # Should be less than 1
            'EPS (ttm)': 0                  # Should be positive
        }

        # Verify all required columns are present
        for column in thresholds.keys():
            if column not in self.data.columns:
                raise KeyError(f"Column '{column}' not found in data")

        # Apply filtering conditions based on thresholds
        self.data_filtered = self.data[
            (self.data['Current Ratio'] > thresholds['Current Ratio']) &
            (self.data['Profit Margin'] > thresholds['Profit Margin']) &
            (self.data['Return on Assets'] > thresholds['Return on Assets']) &
            (self.data['Return on Equity'] > thresholds['Return on Equity']) &
            (self.data['LT Debt/Equity'] < thresholds['LT Debt/Equity']) &
            (self.data['P/E'] > thresholds['P/E']) &
            (self.data['P/B'] < thresholds['P/B']) &
            (self.data['EPS (ttm)'] > thresholds['EPS (ttm)'])
        ]

        if self.data_filtered.empty:
            print("No undervalued stocks found based on the given thresholds.")
            return pd.DataFrame()

        # Score undervalued stocks based on average of P/E and P/B ratios
        self.data_filtered = self.data_filtered.copy()
        self.data_filtered['Undervalued_Score'] = self.data_filtered[['P/E', 'P/B']].mean(axis=1)
        undervalued_stocks = self.score_and_get_top(
            scoring_criteria='Undervalued_Score', 
            ascending=True, 
            top_n=10, 
            data=self.data_filtered
        )
        return undervalued_stocks


# Breakout Potential Sub-Class
class BreakoutPotentialUniverse(Universe):
    """
    Subclass of Universe to identify stocks with breakout potential based on ATR.
    """
    def __init__(self, data_path: str):
        super().__init__(data_path)

    def calculate_breakout_potential(self, window: int = 20) -> pd.DataFrame:
        """
        Calculate breakout potential scores and return the top 10 breakout potential stocks.
        Limits yfinance calls to 10 stocks.

        Args:
            window (int): Rolling window size for ATR calculation.

        Returns:
            pd.DataFrame: Top 10 breakout potential stocks.
        """
        if 'Price' not in self.data.columns:
            raise KeyError("Column 'Price' not found in data")

        # Initial candidate selection based on existing data
        candidates = self.data.copy()
        candidates['Relative_Volume'] = candidates['Volume'] / self.data['Average Volume']
        # Select top 10 candidates with highest Relative Volume
        candidates = candidates.sort_values('Relative_Volume', ascending=False).head(10)
        tickers = candidates['Ticker'].tolist()

        breakout_scores = []
        for ticker in tickers:
            try:
                # Download historical data for a valid period
                stock_data = yf.download(
                    ticker, 
                    start=(datetime.today() - relativedelta(months=3)).strftime('%Y-%m-%d'),
                    end=datetime.today().strftime('%Y-%m-%d'), 
                    progress=False, 
                    auto_adjust=False
                )
                if not stock_data.empty and len(stock_data) >= window:
                    # Calculate True Range
                    stock_data['High-Low'] = stock_data['High'] - stock_data['Low']
                    stock_data['High-Close'] = abs(stock_data['High'] - stock_data['Close'].shift(1))
                    stock_data['Low-Close'] = abs(stock_data['Low'] - stock_data['Close'].shift(1))
                    stock_data['True_Range'] = stock_data[['High-Low', 'High-Close', 'Low-Close']].max(axis=1)
                    # Calculate ATR
                    stock_data['ATR'] = stock_data['True_Range'].rolling(window=window).mean()
                    latest_atr = stock_data['ATR'].iloc[-1]
                    latest_price = stock_data['Close'].iloc[-1]
                    breakout_score = latest_atr / latest_price
                    breakout_scores.append({
                        'Ticker': ticker, 
                        'Breakout_Score': breakout_score
                    })
                else:
                    breakout_scores.append({
                        'Ticker': ticker, 
                        'Breakout_Score': np.nan
                    })
            except Exception as e:
                print(f"Error processing {ticker}: {e}")
                breakout_scores.append({
                    'Ticker': ticker, 
                    'Breakout_Score': np.nan
                })

        scores_df = pd.DataFrame(breakout_scores).dropna()
        if scores_df.empty:
            print("No breakout potential scores calculated.")
            return pd.DataFrame()

        merged_df = pd.merge(self.data, scores_df, on='Ticker')
        breakout_stocks = merged_df.nlargest(10, 'Breakout_Score')
        return breakout_stocks


# Example Usage
if __name__ == "__main__":
    data_path = 'finviz(1).csv'  # Path to your CSV file

    # Instantiate and calculate High Momentum Universe
    high_momentum_universe = HighMomentumUniverse(data_path)
    high_momentum_stocks = high_momentum_universe.calculate_high_momentum()
    print("High Momentum Stocks:")
    print(high_momentum_stocks)
    # Profile only the top 10 high momentum stocks with appropriate title
    if not high_momentum_stocks.empty:
        high_momentum_universe.profile(tickers=high_momentum_stocks['Ticker'].tolist(), universe_name="High Momentum")

    # Instantiate and calculate Mean Reversion Universe
    mean_reversion_universe = MeanReversionUniverse(data_path)
    mean_reverting_stocks = mean_reversion_universe.calculate_mean_reversion()
    print("\nMean Reverting Stocks:")
    print(mean_reverting_stocks)
    if not mean_reverting_stocks.empty:
        # Profile only the top 10 mean reverting stocks with appropriate title
        mean_reversion_universe.profile(tickers=mean_reverting_stocks['Ticker'].tolist(), universe_name="Mean Reversion")

    # Instantiate and calculate Undervalued Universe
    undervalued_universe = UndervaluedUniverse(data_path)
    undervalued_stocks = undervalued_universe.calculate_undervalued_stocks()
    print("\nUndervalued Stocks:")
    print(undervalued_stocks)
    if not undervalued_stocks.empty:
        # Profile undervalued stocks with appropriate title
        undervalued_universe.profile(tickers=undervalued_stocks['Ticker'].tolist(), universe_name="Undervalued")

    # Instantiate and calculate Breakout Potential Universe
    breakout_potential_universe = BreakoutPotentialUniverse(data_path)
    breakout_stocks = breakout_potential_universe.calculate_breakout_potential()
    print("\nBreakout Potential Stocks:")
    print(breakout_stocks)
    if not breakout_stocks.empty:
        # Profile only the top 10 breakout potential stocks with appropriate title
        breakout_potential_universe.profile(tickers=breakout_stocks['Ticker'].tolist(), universe_name="Breakout Potential")
