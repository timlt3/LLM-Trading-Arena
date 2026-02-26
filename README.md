# 🤖 LLM Trading Arena

**Can an LLM beat classic trading strategies?**

A live paper trading competition pitting **Llama 70B** against baseline strategies on US equities.

## 🏆 The Competitors

| Strategy | Trades | Description |
|----------|--------|-------------|
| **Llama 70B** | AAPL, MSFT, GOOGL, AMZN, NVDA... | AI stock picker - analyzes price action + news to select individual stocks |
| **Buy & Hold SPY** | SPY | The Boglehead benchmark - buy the index, hold forever |
| **Mean Reversion** | SPY | RSI-based - buy when oversold (<30), sell when overbought (>70) |
| **Trend Following** | SPY | SMA crossover - long when SMA(10) > SMA(50) |

## 🛠️ Tech Stack

- **LLM Inference**: Llama 3.1 70B on AMD MI300X via vLLM
- **Broker**: Interactive Brokers paper trading API
- **Data**: Yahoo Finance (prices), yfinance news
- **UI**: Gradio leaderboard

## 🚀 Quick Start

### Prerequisites

1. **IBKR Account** with paper trading enabled
2. **TWS or IB Gateway** running locally with API enabled (port 7497)
3. **AMD GPU Droplet** running vLLM with Llama 70B (or any OpenAI-compatible endpoint)

### Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/llm-trading-arena
cd llm-trading-arena

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure
# Edit config.py - set your droplet IP in LLM_BASE_URL
```

### Run the Arena

```bash
python main.py
```

### Run the Leaderboard UI (optional)

```bash
python ui.py
# Opens at http://localhost:7860
```

## 📊 How It Works

Every 15 minutes during market hours:

1. **Baseline strategies** (Buy & Hold, Mean Reversion, Trend Following) analyze SPY
2. **Llama 70B** analyzes the top 5 stocks from a 20-stock universe
3. Decisions are made: **BUY**, **SELL**, or **HOLD**
4. Trades execute on IBKR paper trading
5. P&L is tracked per strategy

## 🧠 The LLM Prompt

Llama receives structured market data:

```
=== PRICE DATA ===
Current Price: $185.42
Recent Change (10 periods): +0.85%
5-Day Change: +2.31%
RSI(14): 58.3
SMA(10): $183.20, SMA(50): $179.85 (bullish)

=== YOUR POSITION ===
Current holding: 50 shares ($9,271)

=== Recent News ===
• Apple announces new AI features for iPhone...
```

And responds with:

```json
{
    "action": "HOLD",
    "confidence": 0.7,
    "reasoning": "Position is profitable, momentum remains positive, waiting for clearer signal"
}
```

## 📁 Project Structure

```
llm-trading-arena/
├── main.py              # Main trading loop
├── config.py            # Configuration (droplet IP, symbols, etc.)
├── broker.py            # IBKR integration
├── data.py              # Price/news fetching + technical indicators
├── tracker.py           # P&L tracking per strategy
├── ui.py                # Gradio leaderboard
├── requirements.txt
└── strategies/
    ├── base.py          # Strategy interface
    ├── llm.py           # Llama 70B stock picker
    ├── buy_hold.py      # Buy & Hold SPY
    ├── mean_reversion.py # RSI-based mean reversion
    └── trend_following.py # SMA crossover
```

## ⚙️ Configuration

Edit `config.py`:

```python
# Your vLLM endpoint
LLM_BASE_URL = "http://YOUR_DROPLET_IP:8000/v1"
LLM_MODEL = "meta-llama/Llama-3.1-70B-Instruct"

# IBKR
IBKR_PORT = 7497  # Paper trading

# Stock universe for Llama to pick from
LLM_UNIVERSE = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", ...]

# Trading parameters
DECISION_INTERVAL_MINUTES = 15
POSITION_SIZE_USD = 10000
```

## 📈 Results

*Results will be updated after running the competition*

| Strategy | Total P&L | Trades | Win Rate |
|----------|-----------|--------|----------|
| TBD | TBD | TBD | TBD |

## ⚠️ Disclaimer

This is for educational and entertainment purposes only. Not financial advice. Paper trading only - no real money at risk.

## 📝 License

MIT
