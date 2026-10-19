import asyncio
import json
import threading
import time
from typing import Dict, Any, List, Optional
import websockets

class HighFrequencyWebSocketFeed:
    """
    Connects to live Binance WebSocket streams at 100ms latency,
    providing real-time orderbook micro-depth telemetry and spoofing detection.
    """

    def __init__(self, symbol: str = "btcusdt"):
        self.symbol = symbol.lower()
        self.ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@depth20@100ms"
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        
        # Latest telemetry state
        self.last_update_time = 0.0
        self.bid_depth_usd = 0.0
        self.ask_depth_usd = 0.0
        self.imbalance_ratio = 1.0
        self.top_bid = 0.0
        self.top_ask = 0.0
        self.spoofing_alert = False
        self.updates_received = 0

    async def _stream_handler(self):
        """Asynchronous stream consumer."""
        retry_delay = 2.0
        while self.is_running:
            try:
                async with websockets.connect(self.ws_url, ping_interval=20, ping_timeout=10) as ws:
                    retry_delay = 2.0
                    while self.is_running:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        self._process_depth_packet(data)
            except Exception as e:
                if self.is_running:
                    await asyncio.sleep(retry_delay)
                    retry_delay = min(retry_delay * 1.5, 30.0)

    def _process_depth_packet(self, data: Dict[str, Any]):
        """Processes 100ms depth snapshot."""
        bids = data.get("bids", [])
        asks = data.get("asks", [])
        
        if not bids or not asks:
            return

        top_bid = float(bids[0][0])
        top_ask = float(asks[0][0])

        total_bids_usd = sum(float(price) * float(qty) for price, qty in bids[:15])
        total_asks_usd = sum(float(price) * float(qty) for price, qty in asks[:15])

        ratio = total_bids_usd / (total_asks_usd + 1e-6)
        
        # Spoofing heuristic: bid wall > 2.8x ask depth with rapid appearance
        is_spoofing = ratio > 2.8 and (ratio - self.imbalance_ratio) > 1.2

        self.top_bid = top_bid
        self.top_ask = top_ask
        self.bid_depth_usd = total_bids_usd
        self.ask_depth_usd = total_asks_usd
        self.imbalance_ratio = ratio
        self.spoofing_alert = is_spoofing
        self.last_update_time = time.time()
        self.updates_received += 1

    def start(self):
        """Starts the WebSocket worker in a daemon background thread."""
        if self.is_running:
            return
        self.is_running = True
        
        def run_loop():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self._stream_handler())

        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stops the WebSocket stream cleanly."""
        self.is_running = False
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)

    def get_microstructure_telemetry(self) -> Dict[str, Any]:
        """Returns current high-frequency orderbook metrics."""
        return {
            "symbol": self.symbol.upper(),
            "top_bid": self.top_bid,
            "top_ask": self.top_ask,
            "spread_usd": round(self.top_ask - self.top_bid, 2),
            "bid_depth_15_usd": round(self.bid_depth_usd, 2),
            "ask_depth_15_usd": round(self.ask_depth_usd, 2),
            "orderbook_imbalance_ratio": round(self.imbalance_ratio, 3),
            "microsecond_spoofing_flag": self.spoofing_alert,
            "stream_updates_count": self.updates_received,
            "latency_ms": 100,
            "is_live": (time.time() - self.last_update_time) < 3.0 if self.last_update_time > 0 else False
        }

# Global singleton instance for app-wide sharing
ws_feed = HighFrequencyWebSocketFeed("btcusdt")
