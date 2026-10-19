import random
from typing import Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd
from core.models import MarketAsset

BASE_PRICES = {
    MarketAsset.BTC: 68450.0,
    MarketAsset.ETH: 2640.0,
    MarketAsset.SOL: 158.0,
    MarketAsset.NVDA: 138.5,
    MarketAsset.GOLD: 2720.0,
}

class MarketDataProvider:
    """Provides market telemetry, technical metrics, and scenario simulations."""

    @staticmethod
    def get_market_snapshot(asset: MarketAsset, scenario: str = "NORMAL") -> Dict[str, Any]:
        base = BASE_PRICES.get(asset, 50000.0)
        
        # Scenario adjustments
        if scenario == "WHALE_ACCUMULATION":
            price = base * (1 + random.uniform(0.015, 0.035))
            volume_24h_delta = +48.5
            funding_rate = +0.012
            orderbook_bid_depth = 1.85 # heavy buy side
            rsi = 62.0
            onchain_inflow_usd = -250_000_000 # Outflows to cold storage
        elif scenario == "FLASH_CRASH_RISK":
            price = base * (1 - random.uniform(0.025, 0.055))
            volume_24h_delta = +112.0
            funding_rate = -0.025
            orderbook_bid_depth = 0.42 # paper thin bids
            rsi = 28.5
            onchain_inflow_usd = +420_000_000 # Massive exchange dumping
        elif scenario == "SPOOFING_MANIPULATION":
            price = base * (1 + random.uniform(0.005, 0.015))
            volume_24h_delta = -15.0 # Fake rally on low real volume
            funding_rate = +0.045 # Overleveraged longs
            orderbook_bid_depth = 3.5 # Huge fake bid walls
            rsi = 74.0
            onchain_inflow_usd = +15_000_000
        else: # NORMAL
            price = base * (1 + random.uniform(-0.008, 0.008))
            volume_24h_delta = random.uniform(-5.0, 5.0)
            funding_rate = 0.008
            orderbook_bid_depth = 1.05
            rsi = random.uniform(46.0, 54.0)
            onchain_inflow_usd = random.uniform(-10_000_000, 10_000_000)

        change_24h = ((price - base) / base) * 100.0

        return {
            "asset": asset.value,
            "scenario": scenario,
            "current_price": round(price, 2),
            "base_price": base,
            "change_24h_pct": round(change_24h, 2),
            "volume_24h_delta_pct": round(volume_24h_delta, 1),
            "rsi_14": round(rsi, 1),
            "funding_rate_pct": round(funding_rate, 4),
            "orderbook_bid_ask_ratio": round(orderbook_bid_depth, 2),
            "onchain_net_exchange_flow_usd": onchain_inflow_usd,
            "ma_20": round(price * 0.992, 2),
            "ma_50": round(price * 0.978, 2),
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def get_historical_candles(asset: MarketAsset, periods: int = 40) -> pd.DataFrame:
        """Generates historical OHLCV data for charts."""
        base = BASE_PRICES.get(asset, 50000.0)
        now = datetime.utcnow()
        candles = []
        
        curr = base * 0.95
        for i in range(periods):
            t = now - timedelta(hours=(periods - i))
            delta = random.uniform(-0.015, 0.02) * curr
            open_p = curr
            close_p = curr + delta
            high_p = max(open_p, close_p) + abs(random.uniform(0.001, 0.008) * curr)
            low_p = min(open_p, close_p) - abs(random.uniform(0.001, 0.008) * curr)
            vol = random.uniform(500, 3500) * (base / 1000)
            
            candles.append({
                "time": t,
                "open": round(open_p, 2),
                "high": round(high_p, 2),
                "low": round(low_p, 2),
                "close": round(close_p, 2),
                "volume": round(vol, 0)
            })
            curr = close_p
            
        return pd.DataFrame(candles)
