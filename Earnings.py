import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind

# Fetch data for Apple93 (AAPL)
apple = yf.Ticker("AAPL")
hist = apple.history(start="2018-01-01", end="2023-12-31")

# Fetch historical quarterly financials
earnings = apple.get_financials(freq='quarterly').T

# Debug: Check earnings data
print("Quarterly Financials Data:")
print(earnings[['Net Income']])
print(f"Total earnings rows: {len(earnings)}")

# Ensure earnings index is datetime and timezone-aware
earnings.index = pd.to_datetime(earnings.index).tz_localize('UTC')

# Filter to desired range (2018–2023)
earnings = earnings[(earnings.index >= "2018-01-01") & (earnings.index <= "2023-12-31")]

# Use Net Income growth as a proxy for sentiment
earnings['Surprise'] = earnings['Net Income'].pct_change(fill_method=None)
earnings = earnings.dropna(subset=['Surprise'])

# Function to adjust earnings date to next trading day
def get_next_trading_day(date, hist):
    idx = hist.index.get_indexer([date], method='bfill')[0]
    if idx == -1:
        return None
    return hist.index[idx]

# Adjust earnings dates
earnings['AdjustedDate'] = [get_next_trading_day(date, hist) for date in earnings.index]
earnings = earnings.dropna(subset=['AdjustedDate'])

# Debug: Print adjusted dates and surprises
print("\nAdjusted Earnings Dates and Surprises:")
print(earnings[['AdjustedDate', 'Surprise']])

# Function to calculate N-day returns
def calculate_returns(dates, hist, surprises, N, threshold=0.0):
    positive_returns = []
    negative_returns = []
    for date, surprise in zip(dates, surprises):
        if pd.notna(surprise):
            if date in hist.index:
                idx = hist.index.get_loc(date)
                if idx + N < len(hist):
                    price_start = hist['Close'].iloc[idx]
                    price_end = hist['Close'].iloc[idx + N]
                    ret = (price_end - price_start) / price_start
                    if surprise > threshold:
                        positive_returns.append(ret)
                    elif surprise < -threshold:
                        negative_returns.append(ret)
    return positive_returns, negative_returns

# Analyze returns for N=1, 3, 5 days
N_values = [1, 3, 5]
for N in N_values:
    pos_returns, neg_returns = calculate_returns(earnings['AdjustedDate'], hist, earnings['Surprise'], N)
    if len(pos_returns) < 2 or len(neg_returns) < 2:
        print(f"For N={N} days: Insufficient data.")
        print(f"Positive surprises: {len(pos_returns)}, Negative surprises: {len(neg_returns)}")
        if pos_returns:
            print(f"Avg return after positive surprise: {np.mean(pos_returns):.4f}")
        if neg_returns:
            print(f"Avg return after negative surprise: {np.mean(neg_returns):.4f}")
        print()
    else:
        avg_pos = np.mean(pos_returns)
        avg_neg = np.mean(neg_returns)
        t_stat, p_value = ttest_ind(pos_returns, neg_returns, equal_var=False)
        print(f"For N={N} days:")
        print(f"Average return after positive surprise: {avg_pos:.4f}")
        print(f"Average return after negative surprise: {avg_neg:.4f}")
        print(f"p-value: {p_value:.4f}")
        print()

print("Summary:")
print(f"Number of positive surprises: {len([x for x in earnings['Surprise'] if pd.notna(x) and x > 0])}")
print(f"Number of negative surprises: {len([x for x in earnings['Surprise'] if pd.notna(x) and x < 0])}")