import uuid
from typing import Dict, Any, List
from datetime import datetime

from core.models import (
    MarketAsset,
    IntentType,
    SignalType,
    ActionDecision,
    TelegraphIntent,
    VerifiableAlphaReport,
    RankedIntelligence,
)
from core.market_data import MarketDataProvider
from core.telegraph_client import TelegraphClient

class AlphaPulseAgent:
    """
    Autonomous Financial Intelligence Agent powered by Telegraph Protocol.
    Transforms raw market data into verified, evaluated alpha recommendations.
    """

    def __init__(self, telegraph_client: TelegraphClient = None):
        self.telegraph = telegraph_client or TelegraphClient()

    def run_market_audit(self, asset: MarketAsset, scenario: str = "NORMAL") -> VerifiableAlphaReport:
        """
        Executes a full audit cycle:
        1. Reads live market telemetry & on-chain data.
        2. Dispatches an analysis intent to Telegraph Protocol.
        3. Obtains scored and ranked intelligence.
        4. Synthesizes risk-adjusted actionable plan with verifiable audit hash.
        """
        # Step 1: Collect market snapshot
        snapshot = MarketDataProvider.get_market_snapshot(asset, scenario)
        current_price = snapshot["current_price"]

        # Step 2: Formulate Telegraph Intent
        intent_id = f"intent-alpha-{uuid.uuid4().hex[:8]}"
        intent = TelegraphIntent(
            intent_id=intent_id,
            asset=asset,
            intent_type=IntentType.LIQUIDITY_RISK if scenario == "SPOOFING_MANIPULATION" else IntentType.TECHNICAL_BREAKOUT,
            context=snapshot
        )

        # Step 3: Query Telegraph Network for Ranked Intelligence
        intel = self.telegraph.submit_intent(intent)

        # Step 4: Find top evaluated miner
        miner_map = {m.miner_id: m for m in intel.responses}
        winning_miner = miner_map.get(intel.winning_miner_id, intel.responses[0])

        # Step 5: Synthesize Final Decision
        if intel.consensus_signal == SignalType.HIGH_RISK_ANOMALY:
            action = ActionDecision.AVOID_RISK
            target_price = None
            stop_loss = None
            risk_level = "EXTREME_WARNING"
        elif intel.consensus_signal == SignalType.BULLISH:
            action = ActionDecision.STRONG_BUY if intel.consensus_confidence >= 0.85 else ActionDecision.BUY
            target_price = winning_miner.target_price
            stop_loss = winning_miner.stop_loss
            risk_level = "MODERATE"
        elif intel.consensus_signal == SignalType.BEARISH:
            action = ActionDecision.STRONG_SELL if intel.consensus_confidence >= 0.85 else ActionDecision.SELL
            target_price = winning_miner.target_price
            stop_loss = winning_miner.stop_loss
            risk_level = "HIGH"
        else:
            action = ActionDecision.NEUTRAL
            target_price = None
            stop_loss = None
            risk_level = "LOW"

        # Step 6: Extract key drivers and evaluation notes
        key_drivers = [
            f"Consensus Signal: {intel.consensus_signal.value} ({int(intel.consensus_confidence * 100)}% verified agreement)",
            f"Top Rated Model: {winning_miner.miner_name} ({winning_miner.model_family})",
            f"Reasoning: {winning_miner.reasoning}",
            f"24h Price Change: {snapshot['change_24h_pct']:+}% | RSI(14): {snapshot['rsi_14']}"
        ]

        if intel.rogue_miners_detected:
            key_drivers.append(
                f"🚨 Telegraph Evaluator Blocked: {', '.join(intel.rogue_miners_detected)} (slashed for hallucination/spoofing)"
            )

        # Step 7: Generate Verifiable Hash
        verif_hash = VerifiableAlphaReport.generate_hash(
            asset.value, action.value, intel.consensus_confidence, winning_miner.miner_name
        )

        eval_summary = (
            f"Telegraph Protocol evaluated {len(intel.responses)} miners. "
            f"Leader: {winning_miner.miner_name} with latency {winning_miner.latency_ms}ms. "
            f"Consensus Confidence: {int(intel.consensus_confidence * 100)}%."
        )

        return VerifiableAlphaReport(
            report_id=f"rep-{uuid.uuid4().hex[:10]}",
            asset=asset,
            current_price=current_price,
            action=action,
            confidence=intel.consensus_confidence,
            top_miner_name=winning_miner.miner_name,
            winning_model=winning_miner.model_family,
            key_drivers=key_drivers,
            trade_parameters={
                "target_price": target_price,
                "stop_loss": stop_loss,
                "risk_level": risk_level,
                "recommended_position_sizing": "4%" if action in [ActionDecision.BUY, ActionDecision.STRONG_BUY] else "0%"
            },
            telegraph_verification_hash=verif_hash,
            evaluation_summary=eval_summary,
            raw_intelligence=intel
        )
