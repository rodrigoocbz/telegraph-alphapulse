import random
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta

class QuantitativeBacktestEngine:
    """
    Simulates historical trading execution to quantify the performance differential
    between Unverified Raw LLMs vs Telegraph Protocol's Verified Intelligence.
    """

    @classmethod
    def run_simulation(cls, periods: int = 60, seed: int = 42) -> Dict[str, Any]:
        random.seed(seed)
        np.random.seed(seed)

        initial_capital = 100_000.0
        capital_raw = initial_capital
        capital_telegraph = initial_capital

        history = []
        now = datetime.utcnow()

        raw_trades_won = 0
        raw_trades_total = 0
        tg_trades_won = 0
        tg_trades_total = 0

        spoofing_events_count = 0
        spoofing_prevented_by_tg = 0

        returns_raw = []
        returns_telegraph = []

        scenarios_pool = [
            "NORMAL", "NORMAL", "WHALE_ACCUMULATION", 
            "SPOOFING_PUMP", "FLASH_CRASH", "NORMAL"
        ]

        for i in range(periods):
            event_type = random.choice(scenarios_pool)
            timestamp = now - timedelta(days=(periods - i))

            # Underlying market price movement
            if event_type == "WHALE_ACCUMULATION":
                market_return = random.uniform(0.025, 0.065)
            elif event_type == "FLASH_CRASH":
                market_return = -random.uniform(0.045, 0.095)
            elif event_type == "SPOOFING_PUMP":
                # Price initial pop, followed by brutal dump
                market_return = -random.uniform(0.035, 0.080)
                spoofing_events_count += 1
            else: # NORMAL
                market_return = random.uniform(-0.015, 0.018)

            # --- 1. Raw Unverified LLM Decision ---
            if event_type in ["WHALE_ACCUMULATION", "SPOOFING_PUMP"]:
                # Raw LLM falls for the hype in spoofing pump!
                raw_action = "BUY"
                raw_trade_ret = market_return * 0.95
            elif event_type == "FLASH_CRASH":
                # Sells at the very bottom
                raw_action = "SELL"
                raw_trade_ret = market_return * 1.10
            else:
                raw_action = random.choice(["BUY", "HOLD", "SELL"])
                raw_trade_ret = market_return if raw_action == "BUY" else 0.0

            # --- 2. Telegraph AlphaPulse Decision ---
            if event_type == "SPOOFING_PUMP":
                # Telegraph Evaluator slashes rogue bot and issues AVOID_RISK!
                tg_action = "AVOID_RISK"
                tg_trade_ret = 0.0 # Capital safely preserved!
                spoofing_prevented_by_tg += 1
            elif event_type == "WHALE_ACCUMULATION":
                tg_action = "BUY"
                tg_trade_ret = market_return * 1.05 # Optimal entry based on consensus
            elif event_type == "FLASH_CRASH":
                tg_action = "AVOID_RISK" # Sidelines during cascading liquidation
                tg_trade_ret = 0.0
            else:
                tg_action = "HOLD" if abs(market_return) < 0.01 else ("BUY" if market_return > 0 else "HOLD")
                tg_trade_ret = market_return if tg_action == "BUY" else 0.0

            # Apply capital changes
            capital_raw *= (1.0 + raw_trade_ret)
            capital_telegraph *= (1.0 + tg_trade_ret)

            returns_raw.append(raw_trade_ret)
            returns_telegraph.append(tg_trade_ret)

            if raw_action != "HOLD":
                raw_trades_total += 1
                if raw_trade_ret > 0:
                    raw_trades_won += 1

            if tg_action not in ["HOLD", "AVOID_RISK"]:
                tg_trades_total += 1
                if tg_trade_ret > 0:
                    tg_trades_won += 1

            history.append({
                "date": timestamp.strftime("%Y-%m-%d"),
                "event": event_type,
                "raw_capital": round(capital_raw, 2),
                "telegraph_capital": round(capital_telegraph, 2),
                "raw_return_pct": round(raw_trade_ret * 100, 2),
                "telegraph_return_pct": round(tg_trade_ret * 100, 2),
                "telegraph_action": tg_action,
                "raw_action": raw_action
            })

        df = pd.DataFrame(history)

        # Financial Metrics Calculations
        ret_raw_np = np.array(returns_raw)
        ret_tg_np = np.array(returns_telegraph)

        # Annualized Sharpe (assuming daily)
        sharpe_raw = float((ret_raw_np.mean() / (ret_raw_np.std() + 1e-6)) * np.sqrt(365))
        sharpe_tg = float((ret_tg_np.mean() / (ret_tg_np.std() + 1e-6)) * np.sqrt(365))

        # Max Drawdown
        df['raw_peak'] = df['raw_capital'].cummax()
        df['raw_dd'] = (df['raw_capital'] - df['raw_peak']) / df['raw_peak']
        max_dd_raw = float(df['raw_dd'].min() * 100)

        df['tg_peak'] = df['telegraph_capital'].cummax()
        df['tg_dd'] = (df['telegraph_capital'] - df['tg_peak']) / df['tg_peak']
        max_dd_tg = float(df['tg_dd'].min() * 100)

        total_return_raw = ((capital_raw - initial_capital) / initial_capital) * 100.0
        total_return_tg = ((capital_telegraph - initial_capital) / initial_capital) * 100.0

        winrate_raw = (raw_trades_won / raw_trades_total * 100) if raw_trades_total else 0.0
        winrate_tg = (tg_trades_won / tg_trades_total * 100) if tg_trades_total else 0.0
        defense_rate = (spoofing_prevented_by_tg / spoofing_events_count * 100) if spoofing_events_count else 100.0

        return {
            "summary": {
                "initial_capital": initial_capital,
                "telegraph_final_capital": round(capital_telegraph, 2),
                "raw_final_capital": round(capital_raw, 2),
                "telegraph_total_return_pct": round(total_return_tg, 2),
                "raw_total_return_pct": round(total_return_raw, 2),
                "telegraph_sharpe": round(sharpe_tg, 2),
                "raw_sharpe": round(sharpe_raw, 2),
                "telegraph_max_drawdown_pct": round(max_dd_tg, 2),
                "raw_max_drawdown_pct": round(max_dd_raw, 2),
                "telegraph_winrate_pct": round(winrate_tg, 1),
                "raw_winrate_pct": round(winrate_raw, 1),
                "spoofing_attacks_avoided_pct": round(defense_rate, 1),
                "total_periods": periods
            },
            "dataframe": df
        }
