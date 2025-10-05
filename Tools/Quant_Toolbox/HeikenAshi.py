from AlgorithmImports import *

class HeikinAshiMomentumAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2024, 1, 1)  # Set Start Date
        self.SetEndDate(2024, 12, 1)    # Set End Date
        self.SetCash(100000)           # Set Strategy Cash
        
        # Select asset
        self.equity = self.AddEquity("SPY", Resolution.Daily)
        self.symbol = self.equity.Symbol
        
        # Historical data to calculate Heikin Ashi values
        self.lookback = 20
        self.history = self.History(self.symbol, self.lookback, Resolution.Daily)
        
        # Schedule function for daily signal check
        self.Schedule.On(self.DateRules.EveryDay(self.symbol), self.TimeRules.BeforeMarketClose(self.symbol, 15), self.TradeLogic)
        
        # Portfolio allocation
        self.position_size = 100  # Shares to buy per position

    def TradeLogic(self):
        data = self.History(self.symbol, self.lookback, Resolution.Daily)
        
        # Calculate Heikin Ashi values
        if 'close' in data.columns and 'open' in data.columns:
            data['HA_close'] = (data['open'] + data['close'] + data['high'] + data['low']) / 4
            data['HA_open'] = 0
            data['HA_open'].iloc[0] = data['open'].iloc[0]

            for i in range(1, len(data)):
                data['HA_open'].iloc[i] = (data['HA_open'].iloc[i - 1] + data['HA_close'].iloc[i - 1]) / 2

            data['HA_high'] = data[['HA_open', 'HA_close', 'high']].max(axis=1)
            data['HA_low'] = data[['HA_open', 'HA_close', 'low']].min(axis=1)

            # Generate signals based on Heikin Ashi values
            data['signals'] = 0
            for i in range(1, len(data)):
                if (data['HA_open'].iloc[i] > data['HA_close'].iloc[i] and
                    data['HA_open'].iloc[i] == data['HA_high'].iloc[i] and
                    abs(data['HA_open'].iloc[i] - data['HA_close'].iloc[i]) > abs(data['HA_open'].iloc[i - 1] - data['HA_close'].iloc[i - 1]) and
                    data['HA_open'].iloc[i - 1] > data['HA_close'].iloc[i - 1]):
                    data['signals'].iloc[i] = 1  # Long signal

                elif (data['HA_open'].iloc[i] < data['HA_close'].iloc[i] and
                      data['HA_open'].iloc[i] == data['HA_low'].iloc[i] and
                      data['HA_open'].iloc[i - 1] < data['HA_close'].iloc[i - 1]):
                    data['signals'].iloc[i] = -1  # Short signal

            # Execute trades based on signals
            current_signal = data['signals'].iloc[-1]
            if current_signal == 1 and not self.Portfolio.Invested:
                self.SetHoldings(self.symbol, 1)
                self.Debug("Long position opened.")
            elif current_signal == -1 and self.Portfolio.Invested:
                self.Liquidate(self.symbol)
                self.Debug("Position closed.")

