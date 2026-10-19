from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import json

class MarketAsset(str, Enum):
    BTC = "BTC/USDT"
    ETH = "ETH/USDT"
    SOL = "SOL/USDT"
    NVDA = "NVDA"
    GOLD = "XAU/USD"

class IntentType(str, Enum):
    TECHNICAL_BREAKOUT = "TECHNICAL_BREAKOUT"
    ONCHAIN_ANOMALY = "ONCHAIN_ANOMALY"
    LIQUIDITY_RISK = "LIQUIDITY_RISK"
    MACRO_EVENT = "MACRO_EVENT"

class SignalType(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    HIGH_RISK_ANOMALY = "HIGH_RISK_ANOMALY"

class ActionDecision(str, Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    NEUTRAL = "NEUTRAL"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"
    AVOID_RISK = "AVOID_RISK"

class TelegraphIntent(BaseModel):
    intent_id: str
    asset: MarketAsset
    intent_type: IntentType
    context: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MinerResponse(BaseModel):
    miner_id: str
    miner_name: str
    model_family: str
    signal: SignalType
    confidence: float
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    reasoning: str
    metrics: Dict[str, Any] = Field(default_factory=dict)
    latency_ms: int

class EvaluatorScore(BaseModel):
    evaluator_id: str
    miner_id: str
    accuracy_score: float # 0.0 to 1.0
    consistency_score: float # 0.0 to 1.0
    hallucination_penalty: float # 0.0 to 1.0
    final_rank_score: float # Combined weighted score
    passed_benchmark: bool
    verdict: str
    notes: List[str] = Field(default_factory=list)

class RankedIntelligence(BaseModel):
    intent_id: str
    asset: MarketAsset
    responses: List[MinerResponse]
    evaluations: List[EvaluatorScore]
    winning_miner_id: str
    consensus_signal: SignalType
    consensus_confidence: float
    rogue_miners_detected: List[str] = Field(default_factory=list)

class VerifiableAlphaReport(BaseModel):
    report_id: str
    asset: MarketAsset
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    current_price: float
    action: ActionDecision
    confidence: float
    top_miner_name: str
    winning_model: str
    key_drivers: List[str]
    trade_parameters: Dict[str, Any]
    telegraph_verification_hash: str
    evaluation_summary: str
    raw_intelligence: RankedIntelligence

    @classmethod
    def generate_hash(cls, asset: str, action: str, confidence: float, winning_miner: str) -> str:
        payload = f"{asset}:{action}:{confidence:.4f}:{winning_miner}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(payload.encode()).hexdigest()
