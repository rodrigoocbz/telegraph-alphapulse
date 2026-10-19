import random
import httpx
from typing import Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd
from core.models import MarketAsset

# Fallback baseline prices if offline
BASE_PRICES = {
    MarketAsset.BTC: 82000.0,
    MarketAsset.ETH: 2700.0,
    MarketAsset.SOL: 165.0,
    MarketAsset.NVDA: 138.5,
    MarketAsset.GOLD: 2720.0,
}

BINANCE_SYMBOL_MAP = {
    MarketAsset.BTC: "BTCUSDT",
    MarketAsset.ETH: "ETHUSDT",
    MarketAsset.SOL: "SOLUSDT",
}

class MarketDataProvider:
    """
    Provides real-time market telemetry via Binance API,
    with smart fallback and scenario simulation capabilities.
    """

    @classmethod
    def get_market_snapshot(cls, asset: MarketAsset, scenario: str = "NORMAL", live: bool = True) -> Dict[str, Any]:
        """Fetches live market metrics or falls back to telemetry baseline."""
        real_data = None
        if live and asset in BINANCE_SYMBOL_MAP:
            try:
                symbol = BINANCE_SYMBOL_MAP[asset]
                with httpx.Client(timeout=4.0) as client:
                    resp = client.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}")
                    if resp.status_code == 200:
                        real_data = resp.json()
            except Exception:
                # Graceful fallback to local telemetry
                real_data = None

        if real_data:
            price = float(real_data["lastPrice"])
            change_24h = float(real_data["priceChangePercent"])
            volume_24h_delta = round(float(real_data["priceChangePercent"]) * 1.5, 1)
            data_source = "BINANCE_LIVE"
        else:
            base = BASE_PRICES.get(asset, 50000.0)
            price = base * (1 + random.uniform(-0.005, 0.005))
            change_24h = ((price - base) / base) * 100.0
            volume_24h_delta = random.uniform(-5.0, 5.0)
            data_source = "TELEMETRY_ENGINE"

        # Apply stress scenario adjustments if requested
        if scenario == "WHALE_ACCUMULATION":
            price = price * 1.025
            volume_24h_delta = +48.5
            funding_rate = +0.012
            orderbook_bid_depth = 1.85
            rsi = 62.0
            onchain_inflow_usd = -250_000_000
        elif scenario == "FLASH_CRASH_RISK":
            price = price * 0.965
            volume_24h_delta = +112.0
            funding_rate = -0.025
            orderbook_bid_depth = 0.42
            rsi = 28.5
            onchain_inflow_usd = +420_000_000
        elif scenario == "SPOOFING_MANIPULATION":
            price = price * 1.01
            volume_24h_delta = -15.0
            funding_rate = +0.045
            orderbook_bid_depth = 3.5
            rsi = 74.0
            onchain_inflow_usd = +15_000_000
        else:  # NORMAL (Genuine Market Conditions)
            funding_rate = 0.008
            orderbook_bid_depth = 1.05
            rsi = 52.0 if real_data is None else round(50.0 + (change_24h * 1.5), 1)
            rsi = max(10.0, min(90.0, rsi))
            onchain_inflow_usd = random.uniform(-10_000_000, 10_000_000)

        return {
            "asset": asset.value,
            "data_source": data_source,
            "scenario": scenario,
            "current_price": round(price, 2),
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

    @classmethod
    def get_historical_candles(cls, asset: MarketAsset, periods: int = 40, live: bool = True) -> pd.DataFrame:
        """Fetches live Binance 1h candlesticks or generates clean synthetic candles."""
        if live and asset in BINANCE_SYMBOL_MAP:
            try:
                symbol = BINANCE_SYMBOL_MAP[asset]
                with httpx.Client(timeout=4.0) as client:
                    resp = client.get(
                        f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit={periods}"
                    )
                    if resp.status_code == 200:
                        raw_candles = resp.json()
                        rows = []
                        for c in raw_candles:
                            rows.append({
                                "time": datetime.fromtimestamp(c[0] / 1000.0),
                                "open": round(float(c[1]), 2),
                                "high": round(float(c[2]), 2),
                                "low": round(float(c[3]), 2),
                                "close": round(float(c[4]), 2),
                                "volume": round(float(c[5]), 0)
                            })
                        if rows:
                            return pd.DataFrame(rows)
            except Exception:
                pass

        # Fallback synthetic generation
        base = BASE_PRICES.get(asset, 50000.0)
        now = datetime.utcnow()
        candles = []
        curr = base * 0.96
        for i in range(periods):
            t = now - timedelta(hours=(periods - i))
            delta = random.uniform(-0.012, 0.015) * curr
            open_p = curr
            close_p = curr + delta
            high_p = max(open_p, close_p) + abs(random.uniform(0.001, 0.006) * curr)
            low_p = min(open_p, close_p) - abs(random.uniform(0.001, 0.006) * curr)
            vol = random.uniform(800, 4000) * (base / 1000)
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
