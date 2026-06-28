# NZD Exchange rate tracker
A Python script that tracks NZD exchange rates (USD, AUD, KRW) every 4 hours and logs them to a Google Sheet. It runs entirely in the cloud via GitHub Actions, so it doesn't need a local machine running 24/7.

## What It Does
Every 4 hours(excluding weekends), the automation:
1. Hits a live exchange rate API to grab the latest NZD rates for USD, AUD, and KRW.
2. Appends a new timestamped row to a Google Sheet.
3. Runs automatically 24/7 in the cloud.
Over time, this builds a clean history of exchange rate data that can be used for charts, trends, or analysis.

## Tech Stack
**Python**: Core scripting language.

**gspread & Google Auth**: For securely connecting to and writing data into Google Sheets.

**ExchangeRate-API**: Provides the live currency data.

**GitHub Actions**: Handles the automation and runs the script on a schedule.

## Data Sample
[Add image later]

## Future Plans: Power BI Integration
I am currently working on connecting this live Google Sheet dataset directly to **Power BI** to build an automated tracking dashboard. 

### Planned Dashboard Features:
**Interactive Historical Trends:** Visualising rate fluctuations over days, weeks, and months with line charts.

**Moving Averages:** Calculating 7-day and 30-day moving averages to smooth out minor daily volatility and show true direction.

**Daily High/Low Callouts:** Cards displaying the highest and lowest exchange rates recorded in the current month.

**Currency Comparison Matrix:** A quick-glance view comparing the percentage change of USD, AUD, and KRW against the NZD over the same period.
