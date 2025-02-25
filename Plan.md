Step 1: Set Up Free API Access
Sign up for a free API key from Financial Modeling Prep (FMP)

Alternatively, register for Alpha Vantage's free API key (25 requests/day)

Consider Marketstack or Twelve Data as backup options for historical price data

Step 2: Determine Your Target Company
Select a large tech company with significant analyst coverage (e.g., Apple, Microsoft, NVIDIA)

Ensure the company has sufficient analyst ratings for meaningful analysis

Step 3: Gather Analyst Sentiment Data
Use the FMP Upgrades & Downgrades API to collect analyst ratings

Request data using: https://financialmodelingprep.com/api/v4/upgrades-downgrades?symbol=TICKER

Download and organize:

Rating dates

Previous ratings

New ratings

Analyst firms

Rating changes (upgrade/downgrade/initiation)

Step 4: Collect Historical Price Data
Use Alpha Vantage to download daily historical price data

Request data using: https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=TICKER&apikey=YOUR_KEY&outputsize=full

Organize:

Daily closing prices

Trading volumes

Date information

Step 5: Merge and Prepare the Data
Align analyst ratings with corresponding price data by date

Create a merged dataset showing:

Each analyst rating change

Stock prices before the rating change

Stock prices after the rating change (1-day, 3-day, 5-day, etc.)

Step 6: Analyze Correlations
Calculate price changes following each analyst rating:

Short-term (1-day, 3-day, 5-day) price movements after upgrades

Short-term price movements after downgrades

Short-term price movements after neutral ratings

Group the data by:

Rating type (Buy, Sell, Hold, etc.)

Direction of change (upgrade vs. downgrade)

Analyst firm (to identify firms with greater market impact)

Step 7: Evaluate Profitability
Calculate average returns following different types of ratings

Determine if there's a statistically significant correlation between ratings and price movements

Create a hypothetical trading strategy:

Buy after upgrades

Sell or short after downgrades

Calculate the theoretical returns of this strategy

Step 8: Prepare Summary Report
Document key findings about the relationship between analyst ratings and price movements

Include visual representations of the correlations

Assess whether "riding analyst sentiment" appears profitable based on your analysis

Note any limitations (limited data, market conditions, etc.)