# 🤖 LLM Trading Arena

**Can an LLM beat classic trading strategies?**

A live paper trading competition pitting **Llama 70B** against baseline strategies on FX markets.

![Arena Screenshot](screenshot.png)

## 🏆 The Competitors

| Strategy | Description |
|----------|-------------|
| **Llama 70B** | Meta's large language model analyzing price action + news to make trading decisions |
| **Buy & Hold** | Simple baseline - buy once and hold |
| **Random** | Coin flip decisions (sanity check) |
| **Mean Reversion** | Classic quant strategy - buy below SMA, sell above |

## 🛠️ Tech Stack

- **LLM Inference**: vLLM on AMD MI300X (192GB VRAM)
- **Broker**: Interactive Brokers paper trading
- **Data**: Yahoo Finance (prices) + NewsAPI (headlines)
- **UI**: Gradio leaderboard

## 🚀 Quick Start

### Prerequisites

1. **IBKR Account** with paper trading enabled
2. **TWS or IB Gateway** running locally with API enabled
3. **AMD GPU Droplet** (or any vLLM-compatible inference server)

### Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/llm-trading-arena
cd llm-trading-arena

# Install dependencies
pip install -r requirements.txt

# Configure (edit config.py)
# - Set your droplet IP in LLM_BASE_URL
# - Optionally add NEWS_API_KEY for headlines

# Start the arena
python main.py
```

### Run the Leaderboard UI

```bash
python ui.py
# Opens at http://localhost:7860
```

## 📊 How It Works

1. Every 15 minutes, each strategy receives market data:
   - Current price
   - 1-hour and 24-hour price history  
   - Recent news headlines (if configured)

2. Each strategy decides: **BUY**, **SELL**, or **HOLD**

3. Trades execute on IBKR paper trading

4. P&L is tracked per strategy with attribution

## 🧠 The LLM Prompt

Llama receives structured market data and must respond with JSON:

```json
{
    "action": "BUY",
    "confidence": 0.75,
    "reasoning": "EUR showing strength against USD following hawkish ECB commentary..."
}
```

## 📁 Project Structure

```
llm-trading-arena/
├── main.py              # Main trading loop
├── config.py            # Configuration
├── broker.py            # IBKR integration
├── data.py              # Market data fetching
├── tracker.py           # P&L tracking
├── ui.py                # Gradio leaderboard
└── strategies/
    ├── base.py          # Strategy interface
    ├── llm.py           # Llama 70B strategy
    ├── buy_hold.py      # Buy & hold baseline
    ├── random_strat.py  # Random baseline
    └── mean_reversion.py # Mean reversion baseline
```

## ⚠️ Disclaimer

This is for educational/entertainment purposes only. Not financial advice. Paper trading only - no real money at risk.

## 📈 Results

*Results will be posted after 48-hour competition run*

| Strategy | Final P&L | Win Rate | Total Trades |
|----------|-----------|----------|--------------|
| TBD | TBD | TBD | TBD |

## 🔧 Configuration

Edit `config.py`:

```python
# Your droplet IP
LLM_BASE_URL = "http://YOUR_DROPLET_IP:8000/v1"

# Trading pairs to compete on
TRADING_PAIRS = ["EUR/USD", "GBP/USD"]

# Decision frequency (minutes)
DECISION_INTERVAL_MINUTES = 15

# Position size per trade
POSITION_SIZE = 10000
```

## 📝 License

MIT
