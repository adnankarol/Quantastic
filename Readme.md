# 🚀 Quantastic — Intelligent Stock Scanner & Alert System

Quantastic is a robust stock analysis and alerting system designed to provide actionable insights into Indian stocks. It leverages technical indicators and fundamental analysis to generate a comprehensive score for each stock, helping users make informed decisions.

## ✨ Key Features

- Quantastic Score: A weighted score (0–100) combining:

  - Technical Indicators: SMA, RSI, Volume spikes, MACD, ADX, Stochastic Oscillator.
  - Fundamentals: Revenue growth, profit growth, ROE, Debt/Equity, and PE ratio.
- Daily Alerts: Sends Telegram alerts in a structured message format with top stock recommendations.
- Configurable: Fully customizable scoring weights, thresholds, and stock universe.
- TEST Mode: Run the script without sending Telegram messages for testing purposes.
- Docker Support: Easily containerize and deploy the project using Docker.
- Automation: Supports scheduling via cron jobs for daily execution.
- Extensible: Modular design for easy integration of additional indicators or data sources.

## 📂 Project Structure

      Quantastic/
      ├── configs/             # Configuration files
      │   ├── config.json      # Main configuration file
      │   ├── credentials.json # Telegram bot credentials
      ├── data/                # Data files (e.g., symbols.csv)
      ├── logs/                # Log files (optional)
      ├── src/                 # Source code
      │   ├── main.py          # Main entry point
      │   ├── extract_symbols.py # Script to scrape NSE symbols
      │   ├── utils/           # Utility modules
      │       ├── logging.py
      │       ├── config.py
      │       ├── scoring.py
      │       ├── messaging.py
      ├── tests/               # Unit tests
      │   ├── test_scoring.py
      ├── set_env.sh           # Environment setup script
      └── Readme.md            # Project documentation

⸻

## ⚙️ Setup

1. Set Up the Environment

Run the set_env.sh script to create a Conda virtual environment and install dependencies:

      bash ./set_env.sh

Activate the environment:

      conda activate quantastic

2. Configure the Project:

- configs/config.json: Update to match your requirements.
- credentials.json: Add sensitive data like Telegram bot token and chat IDs.

3. Extract NSE Stock Symbols: Fetch the latest NSE stock symbols and save them to data/symbols.csv

         python src/extract_symbols.py

4. To run the main script in test mode, and in PROD mode without the mode parameter.

         python main.py --mode TEST
         python main.py

## 🧐 How Quantastic Works

Quantastic evaluates stocks using two complementary approaches:

1. Technical Score (How the stock is moving 📈):Think of this as “Is the stock hot right now?” 🔥 using SMA, RSI, Volume spikes, MACD, ADX, Stochastic Oscillator.

2. Fundamental Score (How the company is doing 💰): Think of this as “Is the business healthy?” 💼 using Revenue growth, Profit growth, ROE, Debt/Equity ratio, PE ratio.

3. Final Score: Combines Technical + Fundamental scores (normalized 0–100).

📊 Scoring Details

- Technical Score: Weighted average of indicators, scaled 0–100.
- Fundamental Score: Average of fundamentals, clamped 0–100.
- Final Score: Mean of tech + fund, displayed as 0–100.

## 📲 Example Telegram Alert

      <b>🚀 Quantastic — Stock Analysis Results</b>

      📊 Processed <b>493</b> stocks from NSE.

      <b>🎯 Quantastic Recommends to check Stocks: </b>

      🏷️ <b>EMBASSY</b>
         • 🏆 Final Score: <b>68.7</b>
         • 📈 Tech Score: 74.1
         • 💼 Fund Score: 63.3
         • 💰 Last Close: ₹391.4
         • 📊 Avg Price (30d): ₹387.2

      🏷️ <b>SUNDARMHLD</b>
         • 🏆 Final Score: <b>67.6</b>
         • 📈 Tech Score: 74.1
         • 💼 Fund Score: 61.1
         • 💰 Last Close: ₹546.7
         • 📊 Avg Price (30d): ₹483.5

      • 🏆 Final Score (0–100): Average of Technical and Fundamental scores (higher is better).
      • 📈 Technical Score (0–100): Evaluates stock movement.
      • 💼 Fundamental Score (0–100): Assesses company health.

## 🕒 Automating with Cron Jobs

- Use cron jobs to run the scanner automatically at market open.
Example: Run every weekday at 10:00 AM IST.

      0 10 * * 1-5 /Users/adnankarol/Desktop/Quantastic/run_main.sh

- Make script executable and fix errors if any as per output

      chmod +x /Users/adnankarol/Desktop/Quantastic/run_main.sh

- Edit your crontab (Mac):

      crontab -e

- Add the line:

      0 10 ** 1-5 /Users/adnankarol/Desktop/Quantastic/run_main.sh

- Ensure the logs directory exists:

      mkdir -p /Users/adnankarol/Desktop/Quantastic/logs

- Check that cron jobs are registered:

      crontab -l

- Logs will be appended with timestamps in:

      /Users/adnankarol/Desktop/Quantastic/logs/alerts.log

## 📜 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 📞 Contact

For any inquiries or support, feel free to reach out via LinkedIn: [Adnan Karol](https://www.linkedin.com/in/your-profile)
