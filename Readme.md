# 🚀 Quantastic — Intelligent Stock Scanner & Alert System

Quantastic is a robust stock analysis and alerting system designed to provide actionable insights into Indian stocks. It leverages **technical indicators** and **fundamental analysis** to generate a comprehensive score for each stock, helping users make informed decisions.

---

## ✨ Key Features

- **Quantastic Score**: A weighted score (−100 to +100) combining:
  - **Technical Indicators**: SMA, RSI, Volume spikes.
  - **Fundamentals**: Revenue growth, profit growth, and PE ratio.
- **Daily Alerts**: Sends HTML-formatted Telegram alerts with top stock recommendations.
- **Configurable**: Fully customizable scoring weights, thresholds, and stock universe.
- **Automation**: Supports scheduling via cron jobs for daily execution.
- **Extensible**: Modular design for easy integration of additional indicators or data sources.

---

## 📂 Project Structure

```
Quantastic/
├── configs/          # Configuration files
│   ├── config.json   # Main configuration file
│   ├── credentials.json # Telegram bot credentials
├── data/             # Data files (e.g., symbols.csv)
├── logs/             # Log files (optional)
├── src/              # Source code
│   ├── main.py       # Main entry point
│   ├── extract_symbols.py # Script to scrape NSE symbols
│   ├── utils/        # Utility modules
│       ├── logging.py
│       ├── config.py
│       ├── scoring.py
│       ├── messaging.py
├── tests/            # Unit tests
│   ├── test_scoring.py
├── set_env.sh        # Environment setup script
└── Readme.md         # Project documentation
```

---

## ⚙️ Setup

### 1. Set Up the Environment

Run the `set_env.sh` script to create a Conda virtual environment and install dependencies:

```bash
bash ./set_env.sh
```

Activate the environment:

```bash
conda activate quantastic
```

### 2. Configure the Project

- **`configs/config.json`**: Update the configuration file to match your requirements.
- **`configs/credentials.json`**: Add your Telegram bot token and chat IDs.

### 3. Extract NSE Stock Symbols

Run the `extract_symbols.py` script to fetch the latest NSE stock symbols and save them to `data/symbols.csv`:

```bash
python src/extract_symbols.py
```

---

## 🧐 How Quantastic Works

Quantastic looks at each stock from **two angles**:

### 1️⃣ Technical Score (How the stock is moving 📈)

- **Price trend (SMA 20)**: Is it trending up or down?
- **Momentum (RSI)**: Oversold → potential buy; Overbought → caution
- **Volume spike**: Big jump in trading volume → could be interesting

> Think of this as “Is the stock **hot right now**?” 🔥

### 2️⃣ Fundamental Score (How the company is doing 💰)

- **Revenue growth** 📊: Did the company earn more than last quarter?
- **Profit growth** 💵: Did it make more profit than last quarter?
- **PE ratio** ⚖️: Price vs earnings — cheap → + points, expensive → - points

> Think of this as “Is the **business healthy**?” 💪

### 3️⃣ Final Score

- Combines Technical + Fundamental scores
- **High score → Buy/Watch** 🟢
- **Medium score → Hold** 🟡
- **Low score → Avoid/Sell** 🔴

---

## 📊 Example Telegram Alert

```
<b>🚀 Quantastic — Market Open Alert</b> (04 Sep 2025, 09:15 IST)
📊 Scanned <b>10</b> stocks. Showing top <b>5</b> picks:

<b>🔥 Watchlist (Potential Buys)</b>
🏷️ TCS — <b>78</b> (Tech: 80, Fund: 75)
💰 Last Price: ₹3,300.00
📉 1M Range: ₹3,200.00 → ₹3,350.00
📈 3M Range: ₹3,000.00 → ₹3,400.00
📊 RSI: 60.1 | PE: 35.0
✅ Recommendation: 🟢 <b>Buy</b>
```

---

## 🕒 Automating with Cron Jobs

### What is a Cron Job?

A **cron job** is a scheduled task that runs automatically at specified times or intervals. It is ideal for automating repetitive tasks like running the `main.py` script daily to fetch stock data, compute scores, and send Telegram alerts.

#### How to Set Up a Cron Job?

1. **Open the Crontab Editor**:

   ```bash
   crontab -e
   ```

2. **Add the Cron Job**:
   Add the following line to schedule the script to run daily at **10:00 AM IST**:

   ```cron
   0 10 * * 1-5 /Users/adnankarol/miniconda3/envs/quantastic/bin/python /Users/adnankarol/Desktop/Quantastic/src/main.py >> /Users/adnankarol/Desktop/Quantastic/logs/alerts.log 2>&1
   ```

   - **Explanation**:
     - `0 10`: Runs at 10:00 AM.
     - `* *`: Every day of the month and every month.
     - `1-5`: Monday to Friday (weekdays only).
     - `/Users/adnankarol/miniconda3/envs/quantastic/bin/python`: Path to the Python interpreter in your virtual environment.
     - `/Users/adnankarol/Desktop/Quantastic/src/main.py`: Path to the `main.py` script.
     - `>> /Users/adnankarol/Desktop/Quantastic/logs/alerts.log`: Appends the output to a log file.
     - `2>&1`: Redirects errors to the same log file.

3. **Save and Exit**:
   - If using `nano`, press `Ctrl + O`, then `Enter`, and `Ctrl + X`.
   - If using `vim`, type `:wq` and press `Enter`.

4. **Verify the Cron Job**:
   List all scheduled cron jobs:

   ```bash
   crontab -l
   ```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix:

   ```bash
   git checkout -b feature-name
   ```

3. Commit your changes:

   ```bash
   git commit -m "Add feature-name"
   ```

4. Push to your branch:

   ```bash
   git push origin feature-name
   ```

5. Submit a pull request.

---

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## 📞 Contact

For any inquiries or support, feel free to reach out via LinkedIn:

- [Your LinkedIn Profile](https://www.linkedin.com/in/your-profile)
