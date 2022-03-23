'''
    Demystifying Time-Series Momentum Strategies: Volatility Estimators, Trading Rules and Pairwise Correlations
    This paper proposed 3 modifications to the basic time-series momentum strategies in order to reduce portfolio turnover and improve portfolio performance.
        1. Volatility Estimator: Yang and Zhang (2000) range-based estimator, which replaces the traditional estimator (standard deviation of past daily returns)
        2. Trading Rules: Trading positions takes a continuum of values between -1 and +1 to reflect the statistical strength of price trend, which replaces the traditional trading rules (binary +1 or -1 based on the sign of historical mean return)
        3. Pairwise Correlations: Incorporate signed pairwise correlations in the weighing scheme of portfolio construction
    Reference:
    [1] Baltas, Nick and Kosowski, Robert, "Demystifying Time-Series Momentum Strategies: Volatility Estimators, Trading Rules and Pairwise Correlations", May 8, 2017.
        URL: https://pdfs.semanticscholar.org/a2e9/df201d4b4774fda84a961cc804f2450988c5.pdf
    [2] Yang, Dennis, and Qiang Zhang, "Drift‐Independent Volatility Estimation Based on High, Low, Open, and Close Prices", The Journal of Business, vol. 73, no. 3, 2000, pp. 477–492.
        URL: www.jstor.org/stable/10.1086/209650.'''

from datetime import timedelta
import numpy as np
import pandas as pd

def GetCorrelationFactor(self, history, trade_signals, available_symbols):
        '''
        Calculate the Correlation Factor, which is a function of the average pairwise correlation of all portfolio contituents
        - the calculation is based on past three month pairwise correlation
        - Notations:
            rho_bar - average pairwise correlation of all portfolio constituents
            CF_rho_bar - the correlation factor as a function of rho_bar'''

        # Get the past three month simple daily returns for all securities
        settle = history.settle.unstack(level = 0)
        past_three_month_returns = settle.pct_change().loc[settle.index[-1]-timedelta(self.ThreeMonths):]

        # Get number of assets
        N_assets = len(available_symbols)

        # Get the pairwise signed correlation matrix for all assets
        correlation_matrix = past_three_month_returns.corr()

        # Calculate rho_bar
        summation = 0
        for i in range(N_assets-1):
            for temp in range(N_assets - 1 - i):
                j = i + temp + 1
                x_i = trade_signals[i]
                x_j = trade_signals[j]
                rho_i_j = correlation_matrix.iloc[i,j]
                summation += x_i * x_j * rho_i_j

        # Equation 14 in [1]
        rho_bar = (2 * summation) / (N_assets * (N_assets - 1))

        # Calculate the correlation factor (CF_rho_bar)
        # Equation 18 in [1]
        return np.sqrt(N_assets / (1 + (N_assets - 1) * rho_bar))


    def GetTradingSignal(self, history):
        '''
        TREND Trading Signal
        - Uses the t-statistics of historical daily log-returns to reflect the strength of price movement trend
        - TREND Signal Conditions:
            t-stat > 1 => TREND Signal = 1
            t-stat < 1 => TREND Signal = -1
            -1 < t-stat < 1 => TREND Signal = t-stat
            '''
        settle = history.settle.unstack(level = 0)

        # daily futures log-returns based on close-to-close
        log_returns = np.log(settle/settle.shift(1)).dropna()

        # Calculate the t-statistics as
        # (mean-0)/(stdev/sqrt(n)), where n is sample size
        mean = np.mean(log_returns)
        std = np.std(log_returns)
        n = len(log_returns)
        t_stat = mean/(std/np.sqrt(n))

        # cap holding at 1 and -1
        return np.clip(t_stat, a_max=1, a_min=-1)

    def GetYZVolatility(self, history, available_symbols):
        '''
        Yang and Zhang 'Drift-Independent Volatility Estimation'
        Formula: sigma_YZ^2 = sigma_OJ^2 + self.k * sigma_SD^2 + (1-self.k)*sigma_RS^2 (Equation 20 in [1])
            where,  sigma_OJ - (Overnight Jump Volitility estimator)
                    sigma_SD - (Standard Volitility estimator)
                    sigma_RS - (Rogers and Satchell Range Volatility estimator)'''
        YZ_volatility = []

        time_index = history.loc[available_symbols[0]].index
        today = time_index[-1]

        #Calculate YZ volatility for each security and append to list
        for ticker in available_symbols:
            past_month_ohlc = history.loc[ticker].loc[today-timedelta(self.OneMonth):today]
            open, high, low, close = past_month_ohlc.open, past_month_ohlc.high, past_month_ohlc.low, past_month_ohlc.settle
            estimation_period = past_month_ohlc.shape[0]

            # Calculate constant parameter k for Yang and Zhang volatility estimator
            # using the formula found in Yang and Zhang (2000)
            k = 0.34 / (1.34 + (estimation_period + 1) / (estimation_period - 1))

            # sigma_OJ (overnight jump => stdev of close-to-open log returns)
            open_to_close_log_returns = np.log(open/close.shift(1))
            open_to_close_log_returns = open_to_close_log_returns[np.isfinite(open_to_close_log_returns)]
            sigma_OJ = np.std(open_to_close_log_returns)

            # sigma_SD (standard deviation of close-to-close log returns)
            close_to_close_log_returns = np.log(close/close.shift(1))
            close_to_close_log_returns = close_to_close_log_returns[np.isfinite(close_to_close_log_returns)]
            sigma_SD = np.std(close_to_close_log_returns)

            # sigma_RS (Rogers and Satchell (1991))
            h = np.log(high/open)
            l = np.log(low/open)
            c = np.log(close/open)
            sigma_RS_daily = (h * (h - c) + l * (l - c))**0.5
            sigma_RS_daily = sigma_RS_daily[np.isfinite(sigma_RS_daily)]
            sigma_RS = np.mean(sigma_RS_daily)

            # daily Yang and Zhang volatility
            sigma_YZ = np.sqrt(sigma_OJ**2 + k * sigma_SD**2 + (1 - k) * sigma_RS**2)

            # append annualized volatility to the list
            YZ_volatility.append(sigma_YZ*np.sqrt(252))

        return YZ_volatility
