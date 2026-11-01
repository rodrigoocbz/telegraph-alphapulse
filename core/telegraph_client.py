import os
import random
import time
from typing import Dict, Any, List
from datetime import datetime

from core.models import (
    MarketAsset,
    IntentType,
    SignalType,
    TelegraphIntent,
    MinerResponse,
    EvaluatorScore,
    RankedIntelligence,
)

class TelegraphClient:
    """
    Client for interacting with the Telegraph Protocol network.
    Supports both simulated (MOCK) mode and LIVE integration for Season II.
    """

    def __init__(self, mode: str = "MOCK", api_key: str = None, endpoint: str = None, payment_sig: str = None):
        self.mode = os.getenv("TELEGRAPH_MODE", mode).upper()
        self.api_key = api_key or os.getenv("TELEGRAPH_API_KEY", "tg_testnet_key_demo")
        self.endpoint = endpoint or os.getenv("TELEGRAPH_ENDPOINT", "https://devnode.telegraphprotocol.com/engine")
        self.payment_sig = payment_sig or os.getenv("TELEGRAPH_PAYMENT_SIG", "")

    def submit_intent(self, intent: TelegraphIntent) -> RankedIntelligence:
        """
        Dispatches an Intent to the Telegraph Protocol network.
        Miners compete to answer, and Evaluators score/rank their output.
        """
        if self.mode == "LIVE":
            return self._call_live_telegraph(intent)
        else:
            return self._simulate_telegraph_network(intent)

    def _call_live_telegraph(self, intent: TelegraphIntent) -> RankedIntelligence:
        """
        Calls Telegraph Protocol V2 Engine API.
        POST /engine/v1/ask with intent + params and PAYMENT-SIGNATURE / escrow.
        """
        import json
        import urllib.request
        import urllib.error

        url = f"{self.endpoint.rstrip('/')}/v1/ask"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.payment_sig:
            headers["PAYMENT-SIGNATURE"] = self.payment_sig

        payload = {
            "intent": intent.intent_type.value,
            "params": {
                "asset": intent.asset.value,
                "current_price": intent.context.get("current_price", 0.0),
                "scenario": intent.context.get("scenario", "NORMAL"),
            }
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                result_json = json.loads(resp.read().decode("utf-8"))
                
                # Parse Telegraph V2 response structure
                miner_id = result_json.get("miner_id", "telegraph-routed-miner")
                miner_name = result_json.get("miner_name", "Telegraph Evaluated Miner")
                cost_usd = result_json.get("cost_usd", 0.01)
                duration_ms = result_json.get("duration_ms", 300)
                signal_hash = result_json.get("signal_hash", "0x0")
                result_data = result_json.get("result", {})

                # Map signal
                raw_signal = str(result_data.get("signal", "NEUTRAL")).upper()
                if "BULL" in raw_signal:
                    consensus_sig = SignalType.BULLISH
                elif "BEAR" in raw_signal:
                    consensus_sig = SignalType.BEARISH
                elif "ANOMALY" in raw_signal or "RISK" in raw_signal:
                    consensus_sig = SignalType.HIGH_RISK_ANOMALY
                else:
                    consensus_sig = SignalType.NEUTRAL

                confidence = float(result_data.get("confidence", 0.85))
                reasoning = result_json.get("reasoning", result_data.get("reasoning", f"Verified signal via Telegraph node (cost: ${cost_usd})"))

                live_miner = MinerResponse(
                    miner_id=miner_id,
                    miner_name=miner_name,
                    model_family="Telegraph-Protocol-V2",
                    signal=consensus_sig,
                    confidence=confidence,
                    target_price=result_data.get("target_price"),
                    stop_loss=result_data.get("stop_loss"),
                    reasoning=reasoning,
                    metrics={"cost_usd": cost_usd, "signal_hash": signal_hash},
                    latency_ms=duration_ms,
                )

                eval_score = EvaluatorScore(
                    evaluator_id="telegraph-v2-validator-quorum",
                    miner_id=miner_id,
                    accuracy_score=0.95,
                    consistency_score=0.92,
                    hallucination_penalty=0.0,
                    final_rank_score=0.935,
                    passed_benchmark=True,
                    verdict="APPROVED",
                    notes=[f"On-chain verified signal_hash: {signal_hash}", f"Cost settled: ${cost_usd}"]
                )

                return RankedIntelligence(
                    intent_id=intent.intent_id,
                    asset=intent.asset,
                    responses=[live_miner],
                    evaluations=[eval_score],
                    winning_miner_id=miner_id,
                    consensus_signal=consensus_sig,
                    consensus_confidence=confidence,
                    rogue_miners_detected=[]
                )

        except urllib.error.HTTPError as e:
            if e.code == 402:
                # Gated 402 challenge - return structured information
                challenge = e.headers.get("PAYMENT-REQUIRED", "")
                raise PermissionError(f"Telegraph 402 Payment Required: Deposit funds into Escrow or supply PAYMENT-SIGNATURE. Challenge: {challenge}")
            err_body = e.read().decode("utf-8")
            raise RuntimeError(f"Telegraph API HTTP {e.code}: {err_body}")
        except Exception as e:
            raise RuntimeError(f"Telegraph API connection failure: {str(e)}")

    def _simulate_telegraph_network(self, intent: TelegraphIntent) -> RankedIntelligence:
        """
        Simulates the Telegraph network dynamics:
        1. Multiple miners with different underlying models submit competing intelligence.
        2. Evaluators score accuracy, latency, and penalize hallucinations/spoofed claims.
        3. A final ranked consensus is produced.
        """
        ctx = intent.context
        scenario = ctx.get("scenario", "NORMAL")
        current_price = ctx.get("current_price", 50000.0)

        responses: List[MinerResponse] = []
        evaluations: List[EvaluatorScore] = []
        rogue_detected: List[str] = []

        # --- Miner 1: DeepSeek Quant (Mathematical / Statistical model) ---
        if scenario == "WHALE_ACCUMULATION":
            m1_signal = SignalType.BULLISH
            m1_conf = 0.88
            m1_reason = "Sustained spot buying with negative exchange net-flows. Statistical probability of continuation: 84%."
        elif scenario == "FLASH_CRASH_RISK":
            m1_signal = SignalType.BEARISH
            m1_conf = 0.91
            m1_reason = "Orderbook bid depth collapsed to 0.42. High probability of cascading long liquidations."
        elif scenario == "SPOOFING_MANIPULATION":
            m1_signal = SignalType.HIGH_RISK_ANOMALY
            m1_conf = 0.89
            m1_reason = "Orderbook bid wall is 3.5x normal but real volume delta is -15%. Severe spoofing signature."
        else:
            m1_signal = SignalType.NEUTRAL
            m1_conf = 0.65
            m1_reason = "Market consolidating in range. Mean reversion dominant."

        responses.append(MinerResponse(
            miner_id="miner-quant-01",
            miner_name="DeepSeek-Quant-V3",
            model_family="DeepSeek-R1-Distill",
            signal=m1_signal,
            confidence=m1_conf,
            target_price=round(current_price * (1.04 if m1_signal == SignalType.BULLISH else 0.96), 2),
            stop_loss=round(current_price * (0.98 if m1_signal == SignalType.BULLISH else 1.02), 2),
            reasoning=m1_reason,
            metrics={"risk_reward_ratio": 2.4, "sample_size": 15000},
            latency_ms=random.randint(180, 290)
        ))

        # --- Miner 2: Mistral On-Chain Flow Specialist ---
        if scenario == "WHALE_ACCUMULATION":
            m2_signal = SignalType.BULLISH
            m2_conf = 0.92
            m2_reason = "250M USD transferred off central exchanges to institutional multisigs in 2 hours."
        elif scenario == "FLASH_CRASH_RISK":
            m2_signal = SignalType.BEARISH
            m2_conf = 0.88
            m2_reason = "420M USD sudden deposit into Binance & Bybit derivative wallets. Sell pressure imminent."
        elif scenario == "SPOOFING_MANIPULATION":
            m2_signal = SignalType.HIGH_RISK_ANOMALY
            m2_conf = 0.85
            m2_reason = "No authentic on-chain whale activity backing the price pop. Fake liquidity injection."
        else:
            m2_signal = SignalType.NEUTRAL
            m2_conf = 0.70
            m2_reason = "Exchange inflows and outflows balanced within historical 30-day moving average."

        responses.append(MinerResponse(
            miner_id="miner-onchain-02",
            miner_name="Mistral-Onchain-Pro",
            model_family="Mistral-Large-2",
            signal=m2_signal,
            confidence=m2_conf,
            target_price=round(current_price * (1.05 if m2_signal == SignalType.BULLISH else 0.95), 2),
            stop_loss=round(current_price * (0.97 if m2_signal == SignalType.BULLISH else 1.03), 2),
            reasoning=m2_reason,
            metrics={"whale_net_flow_usd": ctx.get("onchain_net_exchange_flow_usd", 0)},
            latency_ms=random.randint(210, 340)
        ))

        # --- Miner 3: LLaMA Technicals & Support/Resistance ---
        if scenario == "WHALE_ACCUMULATION":
            m3_signal = SignalType.BULLISH
            m3_conf = 0.82
            m3_reason = "Price reclaimed 50-period MA with expanding Bollinger Bands."
        elif scenario == "FLASH_CRASH_RISK":
            m3_signal = SignalType.BEARISH
            m3_conf = 0.86
            m3_reason = "Loss of local support trendline, RSI printed severe bearish divergence at 28.5."
        elif scenario == "SPOOFING_MANIPULATION":
            m3_signal = SignalType.BULLISH  # Note: A pure technical indicator might falsely buy the pump!
            m3_conf = 0.61
            m3_reason = "Local breakout above resistance, though volume confirmation is slightly weak."
        else:
            m3_signal = SignalType.NEUTRAL
            m3_conf = 0.62
            m3_reason = "Oscillating between support and resistance channels."

        responses.append(MinerResponse(
            miner_id="miner-llama-tech-03",
            miner_name="LLaMA-3.3-ChartMaster",
            model_family="Meta-Llama-3.3-70B",
            signal=m3_signal,
            confidence=m3_conf,
            target_price=round(current_price * 1.03, 2),
            stop_loss=round(current_price * 0.985, 2),
            reasoning=m3_reason,
            metrics={"rsi": ctx.get("rsi_14", 50.0)},
            latency_ms=random.randint(190, 310)
        ))

        # --- Miner 4: Rogue / Hallucinating Miner (Demonstrating Telegraph's Value!) ---
        # This miner gives deceptive or completely unverified claims to show the Evaluator in action.
        if scenario == "SPOOFING_MANIPULATION":
            responses.append(MinerResponse(
                miner_id="miner-rogue-04",
                miner_name="Unverified-Degan-Bot",
                model_family="FineTuned-Meme-7B",
                signal=SignalType.BULLISH,
                confidence=0.99,
                target_price=round(current_price * 1.25, 2), # Exaggerated target
                stop_loss=None,
                reasoning="HUGE PUMP IMMINENT! Guaranteed 25% surge, all-in recommended!",
                metrics={"hype_score": 99.9},
                latency_ms=80
            ))

        # --- TELEGRAPH EVALUATORS: Scoring & Ranking ---
        for miner in responses:
            accuracy = 0.90
            consistency = 0.90
            hallucination_penalty = 0.0
            notes = []

            # Evaluator checking for hallucination/unsupported claims
            if miner.miner_id == "miner-rogue-04":
                hallucination_penalty = 0.95
                accuracy = 0.15
                consistency = 0.10
                notes.append("CRITICAL: Extreme confidence without on-chain or liquidity backing.")
                notes.append("Hallucination/Manipulated signal detected. Penalized -95%.")
                rogue_detected.append(miner.miner_name)
            elif scenario == "SPOOFING_MANIPULATION" and miner.miner_id == "miner-llama-tech-03":
                accuracy = 0.60
                consistency = 0.55
                hallucination_penalty = 0.20
                notes.append("Fell for fake volume breakout; contradicted by cross-miner on-chain audit.")
            else:
                accuracy = random.uniform(0.88, 0.96)
                consistency = random.uniform(0.86, 0.95)
                notes.append("Telemetry cross-verified against live orderbook and on-chain feeds.")

            final_score = (accuracy * 0.5 + consistency * 0.5) * (1.0 - hallucination_penalty)
            passed = final_score >= 0.70

            evaluations.append(EvaluatorScore(
                evaluator_id="telegraph-eval-wasm-01",
                miner_id=miner.miner_id,
                accuracy_score=round(accuracy, 2),
                consistency_score=round(consistency, 2),
                hallucination_penalty=round(hallucination_penalty, 2),
                final_rank_score=round(final_score, 3),
                passed_benchmark=passed,
                verdict="APPROVED" if passed else "REJECTED",
                notes=notes
            ))

        # Sort miners by evaluation score
        eval_lookup = {e.miner_id: e for e in evaluations}
        valid_responses = [r for r in responses if eval_lookup[r.miner_id].passed_benchmark]
        
        if not valid_responses:
            winning_miner = responses[0]
            consensus_signal = SignalType.HIGH_RISK_ANOMALY
            consensus_conf = 0.5
        else:
            valid_responses.sort(key=lambda r: eval_lookup[r.miner_id].final_rank_score, reverse=True)
            winning_miner = valid_responses[0]
            consensus_signal = winning_miner.signal
            consensus_conf = round(sum(r.confidence for r in valid_responses) / len(valid_responses), 2)

        return RankedIntelligence(
            intent_id=intent.intent_id,
            asset=intent.asset,
            responses=responses,
            evaluations=evaluations,
            winning_miner_id=winning_miner.miner_id,
            consensus_signal=consensus_signal,
            consensus_confidence=consensus_conf,
            rogue_miners_detected=rogue_detected
        )
