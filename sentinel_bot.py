import os
import sys
import time
import argparse
from datetime import datetime
from typing import Optional, Dict, Any
import httpx
from dotenv import load_dotenv

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.models import MarketAsset, ActionDecision, SignalType
from core.agent import AlphaPulseAgent
from core.telegraph_client import TelegraphClient
from core.swarm import TelegraphSwarmArbiter
from core.database import AlphaVaultDB
from core.market_data import MarketDataProvider

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

class TelegramSentinel:
    """
    Autonomous Telegram Sentinel powered by Telegraph Protocol.
    Polls commands, executes market audits, and sends proactive risk alerts.
    """

    def __init__(self, agent: Optional[AlphaPulseAgent] = None):
        self.agent = agent or AlphaPulseAgent(telegraph_client=TelegraphClient(mode="MOCK"))
        self.arbiter = TelegraphSwarmArbiter(telegraph_client=self.agent.telegraph)
        self.offset = 0

    def send_message(self, chat_id: str, text: str, parse_mode: str = "HTML") -> bool:
        """Sends an HTML formatted alert to a Telegram chat."""
        if not TELEGRAM_TOKEN or TELEGRAM_TOKEN.startswith("your_"):
            print(f"\n[TELEGRAM DEMO NOTIFICATION to {chat_id}]:\n{text}\n")
            return True

        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(
                    f"{BASE_URL}/sendMessage",
                    json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
                )
                return res.status_code == 200
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False

    def format_report_message(self, report, swarm_res=None) -> str:
        """Formats a Verifiable Alpha Report with Swarm synthesis for Telegram."""
        action_emoji = {
            ActionDecision.STRONG_BUY: "🟢🟢 <b>STRONG BUY</b>",
            ActionDecision.BUY: "🟢 <b>BUY</b>",
            ActionDecision.NEUTRAL: "🟡 <b>NEUTRAL / HOLD</b>",
            ActionDecision.SELL: "🔴 <b>SELL</b>",
            ActionDecision.STRONG_SELL: "🔴🔴 <b>STRONG SELL</b>",
            ActionDecision.AVOID_RISK: "🚨 <b>EXTREME WARNING / AVOID RISK</b>"
        }.get(report.action, report.action.value)

        rogue_section = ""
        if report.raw_intelligence.rogue_miners_detected:
            rogue_section = (
                f"\n\n🚫 <b>Telegraph Evaluators Slashed:</b>\n"
                f"• {', '.join(report.raw_intelligence.rogue_miners_detected)} (Blocked for hallucination/spoofing)"
            )

        swarm_section = ""
        if swarm_res and swarm_res.swarm_thoughts:
            swarm_lines = []
            for t in swarm_res.swarm_thoughts:
                emoji = "🚨" if t.detected_anomaly else "🔍"
                swarm_lines.append(f"{emoji} <b>{t.agent_name.split('-')[0]}:</b> <i>{t.key_observation[:90]}...</i>")
            swarm_section = "\n\n🐝 <b>Swarm Sub-Agents Telemetry:</b>\n" + "\n".join(swarm_lines)

        target = report.trade_parameters.get('target_price')
        stop = report.trade_parameters.get('stop_loss')
        trade_bounds = ""
        if target and stop:
            trade_bounds = (
                f"\n🎯 <b>Target:</b> ${target:,.2f}\n"
                f"🛑 <b>Stop Loss:</b> ${stop:,.2f}"
            )

        signer_str = f"\n✍️ <b>EIP-712 Signer:</b> <code>{swarm_res.eip712_attestation['signer_address'][:10]}...</code>" if swarm_res else ""

        msg = (
            f"⚡ <b>TELEGRAPH ALPHAPULSE SWARM ALERT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"<b>Asset:</b> <code>{report.asset.value}</code>\n"
            f"<b>Live Price:</b> ${report.current_price:,.2f}\n"
            f"<b>Recommendation:</b> {action_emoji}\n"
            f"<b>Telegraph Consensus:</b> {int(report.confidence * 100)}%\n"
            f"<b>Top Rated Miner:</b> <code>{report.top_miner_name}</code>\n"
            f"{trade_bounds}"
            f"{swarm_section}\n\n"
            f"📊 <b>Arbiter Narrative:</b>\n"
            f"<i>{swarm_res.execution_narrative if swarm_res else report.raw_intelligence.responses[0].reasoning}</i>"
            f"{rogue_section}\n\n"
            f"🔐 <b>Verifiable Signature:</b>\n"
            f"<code>{report.telegraph_verification_hash[:26]}...</code>"
            f"{signer_str}"
        )
        return msg

    def handle_command(self, chat_id: str, text: str):
        """Processes user commands from Telegram."""
        text = text.strip()
        parts = text.split()
        cmd = parts[0].lower() if parts else ""

        if cmd in ["/start", "/help"]:
            welcome = (
                "⚡ <b>Welcome to Telegraph AlphaPulse Swarm!</b>\n\n"
                "I am your autonomous financial agent powered by <b>Telegraph Protocol</b> & Multi-Agent Swarm.\n\n"
                "<b>Commands:</b>\n"
                "• <code>/audit BTC</code> - Run swarm audit on Bitcoin (Binance Live)\n"
                "• <code>/audit ETH</code> - Run swarm audit on Ethereum\n"
                "• <code>/audit SOL</code> - Run swarm audit on Solana\n"
                "• <code>/simulate spoofing</code> - Test spoofing attack defense\n"
                "• <code>/backtest</code> - View 60-day quant performance summary\n"
                "• <code>/status</code> - Check Telegraph engine status"
            )
            self.send_message(chat_id, welcome)

        elif cmd == "/status":
            status = (
                "🟢 <b>Telegraph Protocol Agent Status: ONLINE</b>\n"
                "• Architecture: Multi-Agent Swarm (Whale + Micro + Macro)\n"
                "• Evaluators: WASM Sandbox Active\n"
                "• Web3 Layer: EIP-712 Typed Data Signatures Ready\n"
                "• Vault DB: SQLite Persistent Logs\n"
                "• Data Feed: Live Binance REST + Fallback Telemetry\n"
                "• Hackathon Track: Apps & Agents"
            )
            self.send_message(chat_id, status)

        elif cmd == "/backtest":
            from core.backtest import QuantitativeBacktestEngine
            bt = QuantitativeBacktestEngine.run_simulation(60)["summary"]
            bt_msg = (
                f"📊 <b>QUANTITATIVE BACKTEST (60 PERIODS)</b>\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"⚡ <b>Telegraph Return:</b> +{bt['telegraph_total_return_pct']}%\n"
                f"❌ <b>Raw LLM Return:</b> {bt['raw_total_return_pct']}%\n"
                f"📈 <b>Sharpe Ratio:</b> {bt['telegraph_sharpe']} (vs {bt['raw_sharpe']})\n"
                f"🛡️ <b>Spoofing Blocked:</b> {bt['spoofing_attacks_avoided_pct']}%\n"
                f"📉 <b>Max Drawdown:</b> {bt['telegraph_max_drawdown_pct']}% (vs {bt['raw_max_drawdown_pct']}%)"
            )
            self.send_message(chat_id, bt_msg)

        elif cmd == "/audit":
            asset_code = parts[1].upper() if len(parts) > 1 else "BTC"
            asset_map = {"BTC": MarketAsset.BTC, "ETH": MarketAsset.ETH, "SOL": MarketAsset.SOL}
            asset = asset_map.get(asset_code, MarketAsset.BTC)

            self.send_message(chat_id, f"🔍 <i>Swarm analyzing on-chain, orderbook, and Telegraph miners for {asset.value}...</i>")
            snapshot = MarketDataProvider.get_market_snapshot(asset, scenario="NORMAL")
            report = self.agent.run_market_audit(asset, scenario="NORMAL")
            swarm_res = self.arbiter.arbitrate(asset, snapshot)
            AlphaVaultDB.log_swarm_consensus(swarm_res, "NORMAL", snapshot["current_price"])

            self.send_message(chat_id, self.format_report_message(report, swarm_res))

        elif cmd == "/simulate":
            scen_code = parts[1].upper() if len(parts) > 1 else "SPOOFING"
            scenario = "SPOOFING_MANIPULATION" if "SPOOF" in scen_code else "FLASH_CRASH_RISK"
            self.send_message(chat_id, f"🚨 <i>Injecting {scenario} to test Telegraph defense...</i>")
            snapshot = MarketDataProvider.get_market_snapshot(MarketAsset.BTC, scenario=scenario)
            report = self.agent.run_market_audit(MarketAsset.BTC, scenario=scenario)
            swarm_res = self.arbiter.arbitrate(MarketAsset.BTC, snapshot)
            AlphaVaultDB.log_swarm_consensus(swarm_res, scenario, snapshot["current_price"])

            self.send_message(chat_id, self.format_report_message(report, swarm_res))

        else:
            self.send_message(chat_id, "Unknown command. Use /help to see available commands.")

    def run_polling(self):
        """Polls Telegram for incoming messages."""
        if not TELEGRAM_TOKEN or TELEGRAM_TOKEN.startswith("your_"):
            print("⚠️ TELEGRAM_BOT_TOKEN is not configured in .env.")
            print("Running in DEMO SIMULATION mode. Run with --test-alert to see an example.")
            return

        print("🤖 Telegram Sentinel is polling for commands (Ctrl+C to stop)...")
        while True:
            try:
                with httpx.Client(timeout=35.0) as client:
                    resp = client.get(
                        f"{BASE_URL}/getUpdates",
                        params={"offset": self.offset, "timeout": 30}
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        for update in data.get("result", []):
                            self.offset = update["update_id"] + 1
                            msg = update.get("message")
                            if msg and "text" in msg:
                                chat_id = str(msg["chat"]["id"])
                                self.handle_command(chat_id, msg["text"])
            except Exception as e:
                print(f"Polling warning: {e}")
                time.sleep(3)

def main():
    parser = argparse.ArgumentParser(description="Run Telegraph Autonomous Telegram Sentinel")
    parser.add_argument("--test-alert", action="store_true", help="Send a test alert to terminal/chat")
    parser.add_argument("--asset", default="BTC", choices=["BTC", "ETH", "SOL"])
    parser.add_argument("--scenario", default="SPOOFING_MANIPULATION", choices=["NORMAL", "SPOOFING_MANIPULATION", "FLASH_CRASH_RISK"])
    args = parser.parse_args()

    sentinel = TelegramSentinel()

    if args.test_alert:
        asset_map = {"BTC": MarketAsset.BTC, "ETH": MarketAsset.ETH, "SOL": MarketAsset.SOL}
        asset = asset_map[args.asset]
        print(f"\n🚀 Simulating autonomous alert for {asset.value} under {args.scenario}...")
        report = sentinel.agent.run_market_audit(asset, scenario=args.scenario)
        msg = sentinel.format_report_message(report)
        sentinel.send_message(TELEGRAM_CHAT_ID or "YOUR_CHAT_ID", msg)
    else:
        sentinel.run_polling()

if __name__ == "__main__":
    main()
