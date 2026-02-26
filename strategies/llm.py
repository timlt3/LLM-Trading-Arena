from openai import OpenAI
import json
import re

from strategies.base import BaseStrategy, MarketData, Decision, Action
import config


class LlamaStrategy(BaseStrategy):
    """Trading strategy powered by Llama 70B."""
    
    def __init__(self):
        super().__init__("Llama-70B")
        self.client = OpenAI(
            base_url=config.LLM_BASE_URL,
            api_key="not-needed"
        )
    
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
                temperature=0.3  # Lower temp for more consistent decisions
            )
            
            return self._parse_response(response.choices[0].message.content, market_data.pair)
        
        except Exception as e:
            print(f"LLM error: {e}")
            return Decision(
                action=Action.HOLD,
                pair=market_data.pair,
                confidence=0.0,
                reasoning=f"Error calling LLM: {e}",
                strategy_name=self.name
            )
    
    def _system_prompt(self) -> str:
        return """You are an FX trading analyst. You analyze market data and news to make trading decisions.

You must respond with valid JSON in this exact format:
{
    "action": "BUY" | "SELL" | "HOLD",
    "confidence": 0.0 to 1.0,
    "reasoning": "Brief explanation of your decision"
}

Be decisive. Consider:
- Price momentum and recent trends
- News sentiment and potential impact
- Mean reversion opportunities
- Risk management (don't overtrade)

Respond ONLY with the JSON object, no other text."""

    def _build_prompt(self, data: MarketData) -> str:
        # Calculate some basic stats
        prices_1h = data.prices_1h
        prices_24h = data.prices_24h
        
        change_1h = ((prices_1h[-1] - prices_1h[0]) / prices_1h[0] * 100) if prices_1h else 0
        change_24h = ((prices_24h[-1] - prices_24h[0]) / prices_24h[0] * 100) if prices_24h else 0
        
        high_24h = max(prices_24h) if prices_24h else data.current_price
        low_24h = min(prices_24h) if prices_24h else data.current_price
        
        news_section = ""
        if data.news_headlines:
            news_section = "\n\nRecent News Headlines:\n" + "\n".join(f"- {h}" for h in data.news_headlines[:5])
        
        return f"""Analyze {data.pair} and decide whether to BUY, SELL, or HOLD.

Current Price: {data.current_price:.5f}
1-Hour Change: {change_1h:+.3f}%
24-Hour Change: {change_24h:+.3f}%
24h High: {high_24h:.5f}
24h Low: {low_24h:.5f}
{news_section}

Current position: {self.positions.get(data.pair, 0)} units

Provide your trading decision as JSON."""

    def _parse_response(self, response: str, pair: str) -> Decision:
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response)
            
            action = Action[data["action"].upper()]
            confidence = float(data.get("confidence", 0.5))
            reasoning = data.get("reasoning", "No reasoning provided")
            
            return Decision(
                action=action,
                pair=pair,
                confidence=confidence,
                reasoning=reasoning,
                strategy_name=self.name
            )
        
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Failed to parse LLM response: {response}")
            return Decision(
                action=Action.HOLD,
                pair=pair,
                confidence=0.0,
                reasoning=f"Failed to parse response: {e}",
                strategy_name=self.name
            )
