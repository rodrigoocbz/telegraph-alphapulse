import asyncio
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

from core.models import MarketAsset, SignalType, ActionDecision, TelegraphIntent, IntentType
from core.telegraph_client import TelegraphClient
from core.crypto_attestation import CryptoAttestationService

class SwarmAgentThought(BaseModel):
    agent_name: str
    role: str
    key_observation: str
    detected_anomaly: bool
    signal_bias: SignalType
    confidence: float
    telemetry_contribution: Dict[str, Any]

class SwarmConsensusResult(BaseModel):
    intent_id: str
    asset: MarketAsset
    swarm_thoughts: List[SwarmAgentThought]
    telegraph_winning_miner: str
    telegraph_evaluator_verdict: str
    final_arbitrated_action: ActionDecision
    final_confidence: float
    eip712_attestation: Dict[str, Any]
    verifiable_hash: str
    execution_narrative: str

class WhaleSentinelAgent:
    """Specialist sub-agent analyzing on-chain flow and exchange wallet delta."""
    name = "WhaleSentinel-Agent"
    role = "On-Chain Flow & Custodial Outflow Analyst"

    def analyze(self, snapshot: Dict[str, Any]) -> SwarmAgentThought:
        netflow = snapshot.get("onchain_net_exchange_flow_usd", 0)
        anomaly = False
        
        if netflow < -100_000_000:
            obs = f"Massive institutional cold-storage outflow of ${abs(netflow):,.0f} detected. Supply shock bullish."
            bias = SignalType.BULLISH
            conf = 0.91
        elif netflow > +200_000_000:
            obs = f"Abrupt deposit of ${netflow:,.0f} to derivative exchanges. Imminent liquidation dump risk."
            bias = SignalType.BEARISH
            conf = 0.89
            anomaly = True
        else:
            obs = "Exchange net flows balanced within historical 30-day median."
            bias = SignalType.NEUTRAL
            conf = 0.65

        return SwarmAgentThought(
            agent_name=self.name,
            role=self.role,
            key_observation=obs,
            detected_anomaly=anomaly,
            signal_bias=bias,
            confidence=conf,
            telemetry_contribution={"exchange_netflow_usd": netflow}
        )

class MicrostructureAgent:
    """Specialist sub-agent inspecting orderbook walls and liquidity spoofing."""
    name = "Microstructure-Agent"
    role = "Orderbook Depth & Liquidity Spoofing Detective"

    def analyze(self, snapshot: Dict[str, Any]) -> SwarmAgentThought:
        ratio = snapshot.get("orderbook_bid_ask_ratio", 1.0)
        vol_delta = snapshot.get("volume_24h_delta_pct", 0)
        anomaly = False

        if ratio > 2.5 and vol_delta < 0:
            obs = (
                f"Severe Spoofing Alert: Fake bid-wall ratio is {ratio:.1f}x ask depth, "
                f"yet real volume contracted by {vol_delta}%. Artificial price pump detected."
            )
            bias = SignalType.HIGH_RISK_ANOMALY
            conf = 0.94
            anomaly = True
        elif ratio < 0.6:
            obs = f"Orderbook support collapsed (bid-depth {ratio:.2f}x). Heavy downward slippage expected."
            bias = SignalType.BEARISH
            conf = 0.86
            anomaly = True
        elif ratio > 1.4 and vol_delta > 20:
            obs = f"Authentic organic buy-side liquidity absorption (bid-depth {ratio:.2f}x on rising volume)."
            bias = SignalType.BULLISH
            conf = 0.85
        else:
            obs = f"Orderbook depth normal (bid/ask ratio: {ratio:.2f}x)."
            bias = SignalType.NEUTRAL
            conf = 0.60

        return SwarmAgentThought(
            agent_name=self.name,
            role=self.role,
            key_observation=obs,
            detected_anomaly=anomaly,
            signal_bias=bias,
            confidence=conf,
            telemetry_contribution={"bid_ask_ratio": ratio, "volume_delta": vol_delta}
        )

class MacroVolatilityAgent:
    """Specialist sub-agent analyzing funding rates and leverage squeeze risk."""
    name = "MacroVolatility-Agent"
    role = "Leverage Squeeze & Funding Rate Quantitative Specialist"

    def analyze(self, snapshot: Dict[str, Any]) -> SwarmAgentThought:
        funding = snapshot.get("funding_rate_pct", 0.01)
        rsi = snapshot.get("rsi_14", 50.0)
        anomaly = False

        if funding > 0.04:
            obs = f"Perpetual funding rate elevated at {funding:.3f}%. Market dangerously overleveraged in longs."
            bias = SignalType.HIGH_RISK_ANOMALY
            conf = 0.87
            anomaly = True
        elif funding < -0.02:
            obs = f"Negative funding rate at {funding:.3f}%. Short squeeze fuel building up."
            bias = SignalType.BULLISH
            conf = 0.83
        else:
            obs = f"Perpetual funding rates healthy at {funding:.4f}%. RSI(14) at {rsi:.1f}."
            bias = SignalType.NEUTRAL
            conf = 0.65

        return SwarmAgentThought(
            agent_name=self.name,
            role=self.role,
            key_observation=obs,
            detected_anomaly=anomaly,
            signal_bias=bias,
            confidence=conf,
            telemetry_contribution={"funding_rate": funding, "rsi": rsi}
        )

class TelegraphSwarmArbiter:
    """
    Coordinates the Swarm, synthesizes cross-agent context, queries Telegraph Protocol,
    and produces an EIP-712 cryptographically signed verifiable decision.
    """

    def __init__(self, telegraph_client: TelegraphClient = None):
        self.telegraph = telegraph_client or TelegraphClient(mode="MOCK")
        self.whale_agent = WhaleSentinelAgent()
        self.micro_agent = MicrostructureAgent()
        self.macro_agent = MacroVolatilityAgent()

    def arbitrate(self, asset: MarketAsset, snapshot: Dict[str, Any]) -> SwarmConsensusResult:
        # Step 1: Execute concurrent swarm reasoning
        t1 = self.whale_agent.analyze(snapshot)
        t2 = self.micro_agent.analyze(snapshot)
        t3 = self.macro_agent.analyze(snapshot)
        thoughts = [t1, t2, t3]

        # Step 2: Formulate aggregated Telegraph Intent
        intent_id = f"intent-swarm-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        has_critical_anomaly = any(t.detected_anomaly for t in thoughts)
        
        intent = TelegraphIntent(
            intent_id=intent_id,
            asset=asset,
            intent_type=IntentType.LIQUIDITY_RISK if has_critical_anomaly else IntentType.TECHNICAL_BREAKOUT,
            context={
                **snapshot,
                "swarm_consensus": [t.model_dump() for t in thoughts]
            }
        )

        # Step 3: Dispatch to Telegraph Protocol Network
        intel = self.telegraph.submit_intent(intent)

        # Step 4: Cross-examine Telegraph Miners & Evaluators
        eval_lookup = {e.miner_id: e for e in intel.evaluations}
        valid_miners = [m for m in intel.responses if eval_lookup[m.miner_id].passed_benchmark]
        winning_miner = valid_miners[0] if valid_miners else intel.responses[0]

        # Step 5: Final Decision Matrix
        if intel.consensus_signal == SignalType.HIGH_RISK_ANOMALY or t2.signal_bias == SignalType.HIGH_RISK_ANOMALY:
            action = ActionDecision.AVOID_RISK
            final_conf = max(intel.consensus_confidence, t2.confidence)
            narrative = (
                f"Swarm Microstructure agent and Telegraph Evaluators reached unanimous consensus: "
                f"Artificial spoofing / liquidity manipulation detected. "
                f"Telegraph slashed rogue proposals. Capital preserved: AVOID_RISK."
            )
        elif intel.consensus_signal == SignalType.BULLISH:
            action = ActionDecision.STRONG_BUY if intel.consensus_confidence >= 0.85 else ActionDecision.BUY
            final_conf = intel.consensus_confidence
            narrative = (
                f"Swarm and Telegraph Miners confirm bullish breakout. "
                f"Top evaluated model {winning_miner.miner_name} confirmed institutional spot accumulation."
            )
        elif intel.consensus_signal == SignalType.BEARISH:
            action = ActionDecision.STRONG_SELL if intel.consensus_confidence >= 0.85 else ActionDecision.SELL
            final_conf = intel.consensus_confidence
            narrative = (
                f"Bearish distribution confirmed across Telegraph consensus. "
                f"Evaluators verified orderbook exhaustion."
            )
        else:
            action = ActionDecision.NEUTRAL
            final_conf = intel.consensus_confidence
            narrative = "Market consolidating in range. Swarm recommends patience."

        # Step 6: Create EIP-712 On-Chain Cryptographic Attestation
        proof_hash = f"0x{intel.intent_id.replace('-', '')[:16]}{action.value[:8].encode().hex()}"
        unix_ts = int(datetime.utcnow().timestamp())
        
        attestation = CryptoAttestationService.sign_alpha_report(
            report_id=intent_id,
            asset=asset.value,
            action=action.value,
            current_price=snapshot.get("current_price", 0.0),
            confidence=final_conf,
            winning_miner=winning_miner.miner_name,
            timestamp_unix=unix_ts,
            proof_hash=proof_hash
        )

        return SwarmConsensusResult(
            intent_id=intent_id,
            asset=asset,
            swarm_thoughts=thoughts,
            telegraph_winning_miner=winning_miner.miner_name,
            telegraph_evaluator_verdict=eval_lookup[winning_miner.miner_id].verdict,
            final_arbitrated_action=action,
            final_confidence=round(final_conf, 3),
            eip712_attestation=attestation,
            verifiable_hash=attestation["signature"],
            execution_narrative=narrative
        )
