import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.models import MarketAsset, ActionDecision, SignalType
from core.market_data import MarketDataProvider
from core.telegraph_client import TelegraphClient
from core.agent import AlphaPulseAgent

def test_market_snapshot():
    snapshot = MarketDataProvider.get_market_snapshot(MarketAsset.BTC, "NORMAL")
    assert snapshot["asset"] == "BTC/USDT"
    assert "current_price" in snapshot
    assert "rsi_14" in snapshot

def test_telegraph_agent_normal():
    client = TelegraphClient(mode="MOCK")
    agent = AlphaPulseAgent(telegraph_client=client)
    report = agent.run_market_audit(MarketAsset.BTC, scenario="NORMAL")
    
    assert report.asset == MarketAsset.BTC
    assert report.action in [ActionDecision.NEUTRAL, ActionDecision.BUY, ActionDecision.SELL]
    assert len(report.telegraph_verification_hash) == 64
    assert len(report.raw_intelligence.responses) >= 3

def test_telegraph_agent_spoofing_detects_rogue():
    client = TelegraphClient(mode="MOCK")
    agent = AlphaPulseAgent(telegraph_client=client)
    report = agent.run_market_audit(MarketAsset.BTC, scenario="SPOOFING_MANIPULATION")
    
    assert report.action == ActionDecision.AVOID_RISK
    assert "Unverified-Degan-Bot" in report.raw_intelligence.rogue_miners_detected

if __name__ == "__main__":
    test_market_snapshot()
    test_telegraph_agent_normal()
    test_telegraph_agent_spoofing_detects_rogue()
    print("All tests passed successfully!")
