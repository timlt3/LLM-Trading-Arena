from openai import OpenAI
import json
import re

from strategies.base import BaseStrategy, MarketData, Decision, Action
import config


class LlamaStrategy(BaseStrategy):
    """Trading strategy powered by Llama 70B - picks stocks from S&P 500 universe."""
    
    def __init__(self):
        super().__init__("Llama-70B")
        self.client = OpenAI(
            base_url=config.LLM_BASE_URL,
            api_key="not-needed"
        )
        self.portfolio_value = config.POSITION_SIZE_USD * 5  # Can hold up to 5 positions
    
    def decide(self, market_data: MarketData) -> Decision:
        prompt = self._build_prompt(market_data)
        
        try:
            response = self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": self._system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return self._parse_response(response.choices[0].message.content, market_data)
        
        except Exception as e:
            print(f"LLM error: {e}")
            return Decision(
                action=Action.HOLD,
                symbol=market_data.symbol,
                confidence=0.0,
                reasoning=f"Error calling LLM: {e}",
                strategy_name=self.name
            )
    
    def _system_prompt(self) -> str:
        return """You are an AI stock trader managing a portfolio. You analyze price data and news to make trading decisions on individual stocks.

You must respond with valid JSON in this exact format:
{
    "action": "BUY" | "SELL" | "HOLD",
    "confidence": 0.0 to 1.0,
    "reasoning": "Brief explanation of your decision (1-2 sentences)"
}

Consider:
- Recent price momentum and trends
- News sentiment and catalysts
- Technical levels (RSI, moving averages)
- Risk management - don't chase, cut losers
- Your current position in this stock

Be decisive but prudent. Respond ONLY with the JSON object."""

    def _build_prompt(self, data: MarketData) -> str:
        # Calculate stats
        prices = data.prices_5d if data.prices_5d else data.prices_1d
        
        if len(prices) >= 2:
            change_recent = ((prices[-1] - prices[-10]) / prices[-10] * 100) if len(prices) >= 10 else 0
            change_5d = ((prices[-1] - prices[0]) / prices[0] * 100)
        else:
            change_recent = 0
            change_5d = 0
        
        high_5d = max(prices) if prices else data.current_price
        low_5d = min(prices) if prices else data.current_price
        
        # News section
        news_section = ""
        if data.news_headlines:
            news_section = "\n\nRecent News:\n" + "\n".join(f"• {h}" for h in data.news_headlines[:5])
        
        # Current position
        current_pos = self.get_position(data.symbol)
        position_str = f"{current_pos} shares (${current_pos * data.current_price:,.0f})" if current_pos else "None"
        
        # Technical indicators
        tech_section = ""
        if data.rsi_14:
            tech_section += f"\nRSI(14): {data.rsi_14:.1f}"
        if data.sma_10 and data.sma_50:
            tech_section += f"\nSMA(10): ${data.sma_10:.2f}, SMA(50): ${data.sma_50:.2f}"
            if data.sma_10 > data.sma_50:
                tech_section += " (bullish)"
            else:
                tech_section += " (bearish)"
        
        return f"""Analyze {data.symbol} and decide whether to BUY, SELL, or HOLD.

=== PRICE DATA ===
Current Price: ${data.current_price:.2f}
Recent Change (10 periods): {change_recent:+.2f}%
5-Day Change: {change_5d:+.2f}%
5-Day High: ${high_5d:.2f}
5-Day Low: ${low_5d:.2f}
{tech_section}

=== YOUR POSITION ===
Current holding: {position_str}
{news_section}

Make your trading decision as JSON."""

    def _parse_response(self, response: str, market_data: MarketData) -> Decision:
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response)
            
            action = Action[data["action"].upper()]
            confidence = float(data.get("confidence", 0.5))
            reasoning = data.get("reasoning", "No reasoning provided")
            
            # Calculate quantity
            quantity = None
            if action == Action.BUY:
                quantity = int(config.POSITION_SIZE_USD / market_data.current_price)
            elif action == Action.SELL:
                quantity = self.get_position(market_data.symbol)
            
            return Decision(
                action=action,
                symbol=market_data.symbol,
                confidence=confidence,
                reasoning=reasoning,
                strategy_name=self.name,
                quantity=quantity
            )
        
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Failed to parse LLM response: {response[:200]}")
            return Decision(
                action=Action.HOLD,
                symbol=market_data.symbol,
                confidence=0.0,
                reasoning=f"Failed to parse response: {e}",
                strategy_name=self.name
            )
