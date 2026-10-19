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

    def format_report_message(self, report) -> str:
        """Formats a Verifiable Alpha Report for Telegram."""
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

        target = report.trade_parameters.get('target_price')
        stop = report.trade_parameters.get('stop_loss')
        trade_bounds = ""
        if target and stop:
            trade_bounds = (
                f"\n🎯 <b>Target:</b> ${target:,.2f}\n"
                f"🛑 <b>Stop Loss:</b> ${stop:,.2f}"
            )

        msg = (
            f"⚡ <b>TELEGRAPH ALPHAPULSE ALERT</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"<b>Asset:</b> <code>{report.asset.value}</code>\n"
            f"<b>Live Price:</b> ${report.current_price:,.2f}\n"
            f"<b>Recommendation:</b> {action_emoji}\n"
            f"<b>Telegraph Consensus:</b> {int(report.confidence * 100)}%\n"
            f"<b>Top Rated Miner:</b> <code>{report.top_miner_name}</code>\n"
            f"{trade_bounds}\n\n"
            f"📊 <b>Evaluation Rationale:</b>\n"
            f"<i>{report.raw_intelligence.responses[0].reasoning}</i>"
            f"{rogue_section}\n\n"
            f"🔐 <b>Verifiable Hash:</b>\n"
            f"<code>{report.telegraph_verification_hash[:24]}...</code>"
        )
        return msg

    def handle_command(self, chat_id: str, text: str):
        """Processes user commands from Telegram."""
        text = text.strip()
        parts = text.split()
        cmd = parts[0].lower() if parts else ""

        if cmd in ["/start", "/help"]:
            welcome = (
                "⚡ <b>Welcome to Telegraph AlphaPulse Sentinel!</b>\n\n"
                "I am your autonomous financial agent powered by the <b>Telegraph Protocol</b>.\n\n"
                "<b>Commands:</b>\n"
                "• <code>/audit BTC</code> - Run verifiable audit on Bitcoin\n"
                "• <code>/audit ETH</code> - Run verifiable audit on Ethereum\n"
                "• <code>/audit SOL</code> - Run verifiable audit on Solana\n"
                "• <code>/simulate spoofing</code> - Test spoofing attack defense\n"
                "• <code>/status</code> - Check Telegraph engine status"
            )
            self.send_message(chat_id, welcome)

        elif cmd == "/status":
            status = (
                "🟢 <b>Telegraph Protocol Agent Status: ONLINE</b>\n"
                "• Engine: Season II Engine Ready\n"
                "• Evaluators: WASM Sandbox Active\n"
                "• Data Feed: Live Binance REST + Fallback Telemetry\n"
                "• Hackathon Track: Apps & Agents"
            )
            self.send_message(chat_id, status)

        elif cmd == "/audit":
            asset_code = parts[1].upper() if len(parts) > 1 else "BTC"
            asset_map = {"BTC": MarketAsset.BTC, "ETH": MarketAsset.ETH, "SOL": MarketAsset.SOL}
            asset = asset_map.get(asset_code, MarketAsset.BTC)

            self.send_message(chat_id, f"🔍 <i>Querying Telegraph miners & evaluators for {asset.value}...</i>")
            report = self.agent.run_market_audit(asset, scenario="NORMAL")
            self.send_message(chat_id, self.format_report_message(report))

        elif cmd == "/simulate":
            scen_code = parts[1].upper() if len(parts) > 1 else "SPOOFING"
            scenario = "SPOOFING_MANIPULATION" if "SPOOF" in scen_code else "FLASH_CRASH_RISK"
            self.send_message(chat_id, f"🚨 <i>Injecting {scenario} into market stream to test Telegraph defense...</i>")
            report = self.agent.run_market_audit(MarketAsset.BTC, scenario=scenario)
            self.send_message(chat_id, self.format_report_message(report))

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
