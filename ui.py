import gradio as gr
from datetime import datetime
import json

from tracker import Tracker
from data import get_market_data
import config


def get_current_prices() -> dict[str, float]:
    """Fetch current prices for all pairs."""
    prices = {}
    for pair in config.TRADING_PAIRS:
        try:
            data = get_market_data(pair)
            prices[pair] = data.current_price
        except:
            prices[pair] = 0.0
    return prices


def get_leaderboard_data():
    """Get formatted leaderboard data for display."""
    tracker = Tracker()
    prices = get_current_prices()
    leaderboard = tracker.get_leaderboard(prices)
    
    # Format as markdown table
    md = f"# 🏆 LLM Trading Arena Leaderboard\n\n"
    md += f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    md += f"Trading pairs: {', '.join(config.TRADING_PAIRS)}\n\n"
    
    md += "| Rank | Strategy | Total P&L | Realized | Unrealized | Trades |\n"
    md += "|------|----------|-----------|----------|------------|--------|\n"
    
    for i, entry in enumerate(leaderboard, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        total = f"${entry['total_pnl']:+,.2f}"
        realized = f"${entry['realized_pnl']:+,.2f}"
        unrealized = f"${entry['unrealized_pnl']:+,.2f}"
        
        md += f"| {medal} | **{entry['strategy']}** | {total} | {realized} | {unrealized} | {entry['trades']} |\n"
    
    return md


def get_recent_trades():
    """Get recent trades formatted for display."""
    tracker = Tracker()
    
    md = "# 📊 Recent Trades\n\n"
    
    # Get last 20 trades
    recent = tracker.trades[-20:][::-1]  # Reverse for newest first
    
    if not recent:
        return md + "*No trades yet*"
    
    md += "| Time | Strategy | Pair | Action | Size | Price | P&L |\n"
    md += "|------|----------|------|--------|------|-------|-----|\n"
    
    for trade in recent:
        time_str = trade.timestamp.split("T")[1][:8] if "T" in trade.timestamp else trade.timestamp
        pnl = f"${trade.pnl:+,.2f}" if trade.pnl else "-"
        action_emoji = "🟢" if trade.action == "BUY" else "🔴"
        
        md += f"| {time_str} | {trade.strategy} | {trade.pair} | {action_emoji} {trade.action} | {trade.size:,.0f} | {trade.price:.5f} | {pnl} |\n"
    
    return md


def get_positions():
    """Get current positions for all strategies."""
    tracker = Tracker()
    prices = get_current_prices()
    
    md = "# 📈 Current Positions\n\n"
    
    for strategy in tracker.positions:
        positions = tracker.positions[strategy]
        if any(p != 0 for p in positions.values()):
            md += f"### {strategy}\n"
            for pair, size in positions.items():
                if size != 0:
                    direction = "LONG" if size > 0 else "SHORT"
                    current = prices.get(pair, 0)
                    entry = tracker.entry_prices.get(strategy, {}).get(pair, 0)
                    if size > 0:
                        pnl = size * (current - entry)
                    else:
                        pnl = abs(size) * (entry - current)
                    md += f"- {pair}: {direction} {abs(size):,.0f} @ {entry:.5f} (P&L: ${pnl:+,.2f})\n"
            md += "\n"
    
    if not any(tracker.positions.values()):
        md += "*No open positions*"
    
    return md


def refresh_all():
    """Refresh all displays."""
    return get_leaderboard_data(), get_recent_trades(), get_positions()


# Create Gradio interface
with gr.Blocks(title="LLM Trading Arena") as demo:
    gr.Markdown("# 🤖 LLM Trading Arena")
    gr.Markdown("**Llama 70B vs Classic Strategies** - Live FX Paper Trading Competition")
    
    with gr.Row():
        with gr.Column(scale=2):
            leaderboard = gr.Markdown(get_leaderboard_data())
        with gr.Column(scale=1):
            positions = gr.Markdown(get_positions())
    
    trades = gr.Markdown(get_recent_trades())
    
    refresh_btn = gr.Button("🔄 Refresh", variant="primary")
    refresh_btn.click(
        fn=refresh_all,
        outputs=[leaderboard, trades, positions]
    )
    
    # Auto-refresh every 30 seconds
    demo.load(
        fn=refresh_all,
        outputs=[leaderboard, trades, positions],
        every=30
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
