import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind

# Fetch data for Apple (AAPL)
apple = yf.Ticker("AAPL")
recommendations = apple.recommendations_summary
hist = apple.history(start="2023-06-01", end="2024-01-15")

# Debug: Inspect recommendations and hist
print("Recommendations Summary head:")
print(recommendations.head())
print("Columns:", recommendations.columns.tolist())
print("\nHist index range:", hist.index[0], "to", hist.index[-1])

# Calculate sentiment score
recommendations['Sentiment'] = (5 * recommendations['strongBuy'] + 
                               4 * recommendations['buy'] + 
                               3 * recommendations['hold'] + 
                               2 * recommendations['sell'] + 
                               1 * recommendations['strongSell']) / \
                              (recommendations['strongBuy'] + recommendations['buy'] + 
                               recommendations['hold'] + recommendations['sell'] + 
                               recommendations['strongSell'])

# Map periods to approximate dates
today = pd.to_datetime("2023-12-31").tz_localize('UTC')
period_map = {'0m': 0, '-1m': -1, '-2m': -2, '-3m': -3}
recommendations['MonthsAgo'] = recommendations['period'].map(lambda x: period_map[x])
recommendations['ApproxDate'] = [today + pd.offsets.MonthEnd(n) for n in recommendations['MonthsAgo']]

print("\nApproxDate values:")
print(recommendations['ApproxDate'])

# Adjust dates to the nearest trading day in hist
def get_nearest_trading_day(date, hist):
    idx = hist.index.get_indexer([date], method='nearest')[0]
    if idx == -1:
        print(f"Warning: No trading day found for {date}")
        return None
    return hist.index[idx]

recommendations['AdjustedDate'] = [get_nearest_trading_day(date, hist) for date in recommendations['ApproxDate']]
print("\nAdjusted Dates:")
print(recommendations['AdjustedDate'])

recommendations = recommendations.dropna(subset=['AdjustedDate'])
recommendations = recommendations.set_index('AdjustedDate')
recommendations = recommendations.sort_index()

# Calculate sentiment changes
recommendations['SentimentChange'] = recommendations['Sentiment'].diff()

# Debug: Print sentiment and changes
print("\nSentiment Scores and Changes:")
print(recommendations[['Sentiment', 'SentimentChange']])

# Function to calculate N-day returns
def calculate_returns(dates, hist, sentiment_changes, N, threshold=0.0):
    positive_returns = []
    negative_returns = []
    for date, change in zip(dates, sentiment_changes):
        if pd.notna(change):
            if date in hist.index:
                idx = hist.index.get_loc(date)
                if idx + N < len(hist):
                    price_start = hist['Close'].iloc[idx]
                    price_end = hist['Close'].iloc[idx + N]
                    ret = (price_end - price_start) / price_start
                    if change > threshold:
                        positive_returns.append(ret)
                    elif change < -threshold:
                        negative_returns.append(ret)
    return positive_returns, negative_returns

# Analyze returns for N=1, 3, 5 days
N_values = [1, 3, 5]
for N in N_values:
    pos_returns, neg_returns = calculate_returns(recommendations.index, hist, 
                                                 recommendations['SentimentChange'], N, threshold=0.0)
    if len(pos_returns) < 2 or len(neg_returns) < 2:
        print(f"For N={N} days: Insufficient data.")
        print(f"Positive changes: {len(pos_returns)}, Negative changes: {len(neg_returns)}")
        if pos_returns:
            print(f"Avg return after positive sentiment: {np.mean(pos_returns):.4f}")
        if neg_returns:
            print(f"Avg return after negative sentiment: {np.mean(neg_returns):.4f}")
        print()
    else:
        avg_pos = np.mean(pos_returns)
        avg_neg = np.mean(neg_returns)
        t_stat, p_value = ttest_ind(pos_returns, neg_returns, equal_var=False)
        print(f"For N={N} days:")
        print(f"Average return after positive sentiment change: {avg_pos:.4f}")
        print(f"Average return after negative sentiment change: {avg_neg:.4f}")
        print(f"p-value: {p_value:.4f}")
        print()

print("Summary:")
print(f"Number of positive sentiment changes (>0.0): {len([x for x in recommendations['SentimentChange'] if pd.notna(x) and x > 0.0])}")
print(f"Number of negative sentiment changes (<0.0): {len([x for x in recommendations['SentimentChange'] if pd.notna(x) and x < 0.0])}")


'''
Analyzing the Output
Raw Data:
The recommendations_summary provides 4 periods (0m to -3m), consistent with its limit.
Date Mapping:
ApproxDate: 2023-09-30, 2023-10-31, 2023-11-30, 2023-12-31 (UTC).
AdjustedDate: Adjusted to the nearest trading days in hist:
2023-09-29 (Friday, before Saturday 9/30).
2023-10-31 (Tuesday, matches exactly).
2023-11-30 (Thursday, matches exactly).
2023-12-29 (Friday, before Sunday 12/31).
hist range (2023-06-01 to 2024-01-12) covers these dates, and the timezone shift (America/New_York) is handled correctly.
Sentiment Scores and Changes:
text
Wrap
Copy
AdjustedDate                Sentiment  SentimentChange
2023-09-29 00:00:00-04:00   3.744681          NaN
2023-10-31 00:00:00-04:00   3.744681     0.000000
2023-11-30 00:00:00-05:00   3.673913    -0.070768
2023-12-29 00:00:00-05:00   3.630435    -0.043478
Three changes: one neutral (0.0), two negative (-0.070768, -0.043478).
Returns Analysis:
N=1 days: Avg return after negative sentiment: -0.0145 (1.45% drop).
N=3 days: Avg return after negative sentiment: -0.0184 (1.84% drop).
N=5 days: Avg return after negative sentiment: -0.0067 (0.67% drop).
Insufficient Data: Only 2 negative changes and 0 positive changes, so no t-test (needs ≥2 per group).
Summary:
0 positive changes (>0.0).
2 negative changes (<0.0).
Is It Working as Intended?
Yes, mechanically, the script is doing what it should:

It calculates sentiment scores from the aggregated ratings.
It adjusts dates to trading days and computes changes.
It measures price returns following these changes. However, the 4-period limit of recommendations_summary restricts us to 3 data points (2 negative, 0 positive), which isn’t enough for a robust statistical analysis or to fully answer your question about profitability.
Concise Summary with Correlations/Patterns
Based on the output:

Data: Analyst sentiment scores were derived from recommendations_summary for Apple (AAPL) over 4 periods (approx. September to December 2023). Sentiment changes were calculated and aligned with price data from 2023-06-01 to 2024-01-12.
Findings:
Negative Sentiment Changes: Two instances of declining sentiment (-0.070768 on 2023-11-30, -0.043478 on 2023-12-29) were followed by average price drops:
1 day: -1.45%.
3 days: -1.84%.
5 days: -0.67%.
Positive Sentiment Changes: None observed (0 changes > 0.0).
Correlation: With only two negative events and no positive ones, a formal correlation (e.g., Pearson) can’t be computed. However, the consistent negative returns after sentiment declines suggest a directional pattern—price tends to fall when sentiment worsens.
Patterns: Negative sentiment shifts align with short-term price declines, strongest over 1-3 days (-1.45% to -1.84%), weakening by 5 days (-0.67%). The lack of positive changes limits broader conclusions.
Assessing Profitability
Riding Negative Sentiment: Shorting AAPL after a negative sentiment change could yield gains (e.g., 1.45% over 1 day, 1.84% over 3 days). However:
Sample Size: Only 2 events make this anecdotal, not statistically reliable.
Costs: Transaction fees and timing risks could offset small gains.
Riding Positive Sentiment: No data to assess (0 positive changes).
Limitations: The 4-period cap means we’re working with minimal data, reducing confidence in the pattern’s consistency.
'''