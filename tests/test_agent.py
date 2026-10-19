import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.models import MarketAsset, ActionDecision, SignalType
from core.market_data import MarketDataProvider
from core.telegraph_client import TelegraphClient
from core.agent import AlphaPulseAgent
from core.swarm import TelegraphSwarmArbiter
from core.crypto_attestation import CryptoAttestationService
from core.database import AlphaVaultDB
from core.backtest import QuantitativeBacktestEngine

class TestAlphaPulseSuite(unittest.TestCase):

    def test_market_snapshot(self):
        snapshot = MarketDataProvider.get_market_snapshot(MarketAsset.BTC, "NORMAL")
        self.assertEqual(snapshot["asset"], "BTC/USDT")
        self.assertIn("current_price", snapshot)
        self.assertIn("rsi_14", snapshot)

    def test_telegraph_agent_normal(self):
        client = TelegraphClient(mode="MOCK")
        agent = AlphaPulseAgent(telegraph_client=client)
        report = agent.run_market_audit(MarketAsset.BTC, scenario="NORMAL")
        self.assertEqual(report.asset, MarketAsset.BTC)
        self.assertIn(report.action, [ActionDecision.NEUTRAL, ActionDecision.BUY, ActionDecision.SELL])
        self.assertEqual(len(report.telegraph_verification_hash), 64)
        self.assertGreaterEqual(len(report.raw_intelligence.responses), 3)

    def test_telegraph_agent_spoofing_detects_rogue(self):
        client = TelegraphClient(mode="MOCK")
        agent = AlphaPulseAgent(telegraph_client=client)
        report = agent.run_market_audit(MarketAsset.BTC, scenario="SPOOFING_MANIPULATION")
        self.assertEqual(report.action, ActionDecision.AVOID_RISK)
        self.assertIn("Unverified-Degan-Bot", report.raw_intelligence.rogue_miners_detected)

    def test_swarm_arbiter_and_crypto(self):
        snapshot = MarketDataProvider.get_market_snapshot(MarketAsset.BTC, scenario="SPOOFING_MANIPULATION")
        arbiter = TelegraphSwarmArbiter()
        res = arbiter.arbitrate(MarketAsset.BTC, snapshot)
        
        self.assertEqual(res.final_arbitrated_action, ActionDecision.AVOID_RISK)
        self.assertEqual(len(res.swarm_thoughts), 3)
        self.assertTrue(res.eip712_attestation["signer_address"].startswith("0x"))
        self.assertTrue(len(res.eip712_attestation["signature"]) > 50)

    def test_database_logging(self):
        snapshot = MarketDataProvider.get_market_snapshot(MarketAsset.ETH, scenario="NORMAL")
        arbiter = TelegraphSwarmArbiter()
        res = arbiter.arbitrate(MarketAsset.ETH, snapshot)
        AlphaVaultDB.log_swarm_consensus(res, "NORMAL", snapshot["current_price"])
        
        audits = AlphaVaultDB.get_recent_audits(5)
        self.assertGreater(len(audits), 0)

    def test_quantitative_backtest(self):
        bt = QuantitativeBacktestEngine.run_simulation(30)
        summ = bt["summary"]
        self.assertIn("telegraph_total_return_pct", summ)
        self.assertIn("raw_total_return_pct", summ)
        self.assertGreaterEqual(summ["spoofing_attacks_avoided_pct"], 90.0)

if __name__ == "__main__":
    unittest.main()
