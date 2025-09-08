# 🚀 Quantastic — Intelligent Stock Scanner & Alert System

Quantastic is a robust stock analysis and alerting system designed to provide actionable insights into Indian stocks. It leverages **technical indicators** and **fundamental analysis** to generate a comprehensive score for each stock, helping users make informed decisions.

---

## ✨ Key Features

- **Quantastic Score**: A weighted score (0–100) combining:
  - **Technical Indicators**: SMA, RSI, Volume spikes, MACD, ADX, Stochastic Oscillator.
  - **Fundamentals**: Revenue growth, profit growth, ROE, Debt/Equity, and PE ratio.
- **Daily Alerts**: Sends HTML-formatted Telegram alerts with top stock recommendations.
- **Configurable**: Fully customizable scoring weights, thresholds, and stock universe.
- **TEST Mode**: Run the script without sending Telegram messages for testing purposes.
- **Docker Support**: Easily containerize and deploy the project using Docker.
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
  - **Validation Retries**: Adjust the number of retries for symbol validation in the `validation` section:

    ```json
    "validation": {
      "retries": 3
    }
    ```

- **Credentials Variables**: Add sensitive data like Telegram bot token and chat IDs to credentials.json.

### 3. Extract NSE Stock Symbols

Run the `extract_symbols.py` script to fetch the latest NSE stock symbols and save them to `data/symbols.csv`:

```bash
python src/extract_symbols.py
```

---

## 🧐 How Quantastic Works

Quantastic evaluates stocks using two complementary approaches:

### 1️⃣ Technical Score (How the stock is moving 📈)

- **SMA (Simple Moving Average)**: Detects trend direction.
- **RSI (Relative Strength Index)**: Identifies overbought or oversold conditions.
- **Volume spikes**: Highlights unusually high trading activity.
- **MACD (Moving Average Convergence Divergence)**: Confirms trend strength and direction.
- **ADX (Average Directional Index)**: Indicates trend strength.
- **Stochastic Oscillator**: Identifies overbought or oversold conditions.

> Think of this as “Is the stock **hot right now**?” 🔥

### 2️⃣ Fundamental Score (How the company is doing 💰)

- **Revenue growth** 📊: Did the company earn more than last quarter?
- **Profit growth** 💵: Net income growth compared to prior quarter.
- **ROE (Return on Equity)** 💪: Efficiency in generating returns.
- **Debt/Equity ratio** ⚖️: Financial stability measure.
- **PE ratio** ⚖️: Valuation — lower PE = higher score, higher PE = lower score.

> Think of this as “Is the **business healthy**?” 💼

### 3️⃣ Final Score

- Combines Technical + Fundamental scores (normalized 0–100)
- **High score → Buy/Watch** 🟢
- **Medium score → Hold** 🟡
- **Low score → Avoid/Sell** 🔴

---

## 📊 Scoring Details

### 1️⃣ Technical Score (tech_score)

- Each component (SMA signal, RSI, volume, MACD, ADX, Stochastic) is normalized between 0 and 1.
- Weighted average is computed using the configured weights in `config.json`.
- **Range**: 0 (worst technical setup) → 1 (best technical setup)
- **Displayed as**: 0–100 after `round(tech_score * 100)`

---

### 2️⃣ Fundamental Score (fund_score)

- Components include:
  - **P/E ratio** (scaled 0–1)
  - **ROE** (normalized 0–1)
  - **Debt/Equity** (inverted 0–1)
  - **Revenue growth** (via tanh)
  - **Net income growth** (via tanh)
- Average of all components, clamped to 0–1.
- **Range**: 0 (poor fundamentals) → 1 (excellent fundamentals)
- **Displayed as**: 0–100 after `round(fund_score * 100)`

---

### 3️⃣ Final Score (final_score)

- Calculated as the average of technical + fundamental scores:
  \[
  \text{final_score} = \text{clamp}(\text{mean}(tech_score, fund_score))
  \]
- **Range**: 0 → 1 before scaling.
- **Displayed as**: 0–100 after `round(final_score * 100)`

---

### 4️⃣ Example

Suppose for a stock:

#### Technical Metrics

| Metric          | Normalized Value (0–1) |
|------------------|-------------------------|
| SMA signal       | 1                       |
| RSI signal       | 0.7                     |
| Volume signal    | 0.8                     |
| MACD signal      | 1                       |
| ADX signal       | 0.6                     |
| Stochastic signal| 0.5                     |
| **Technical score** | **0.7667**             |

#### Fundamental Metrics

| Metric          | Normalized Value (0–1) |
|------------------|-------------------------|
| PE ratio         | 0.5                     |
| ROE              | 0.7                     |
| Debt/Equity      | 0.8                     |
| Revenue growth   | 0.2                     |
| Net income growth| 0.3                     |
| **Fundamental score** | **0.5**             |

#### Final Score

\[
\text{final_score} = \text{mean}(0.7667, 0.5) = 0.63335 \approx 63
\]

✅ **Recommendation**: Hold (medium score)

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

For any inquiries or support, feel free to reach out via LinkedIn: [Adnan Karol](https://www.linkedin.com/in/your-profile)
