import argparse
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from core.models import MarketAsset
from core.agent import AlphaPulseAgent
from core.telegraph_client import TelegraphClient

console = Console()

def run_cli(asset_str: str, scenario: str, mode: str):
    console.print(Panel.fit(
        "[bold cyan]⚡ AlphaPulse - Verifiable Financial Agent[/bold cyan]\n"
        "[italic magenta]Powered by Telegraph Protocol (Season II Engine)[/italic magenta]",
        border_style="cyan"
    ))

    # Match asset
    asset_map = {
        "BTC": MarketAsset.BTC,
        "ETH": MarketAsset.ETH,
        "SOL": MarketAsset.SOL,
        "NVDA": MarketAsset.NVDA,
        "GOLD": MarketAsset.GOLD,
    }
    asset = asset_map.get(asset_str.upper(), MarketAsset.BTC)

    client = TelegraphClient(mode=mode)
    agent = AlphaPulseAgent(telegraph_client=client)

    console.print(f"[bold yellow]→ Inspecting {asset.value} under scenario: [green]{scenario}[/green][/bold yellow]")
    with console.status("[bold green]Querying Telegraph Protocol Miners & Evaluators..."):
        report = agent.run_market_audit(asset, scenario=scenario)

    # 1. Action Summary Table
    action_color = "green" if "BUY" in report.action.value else ("red" if "SELL" in report.action.value or "AVOID" in report.action.value else "yellow")
    console.print(Panel(
        f"[bold]Action Recommendation:[/bold] [{action_color}]{report.action.value}[/{action_color}]\n"
        f"[bold]Current Price:[/bold] ${report.current_price:,.2f}\n"
        f"[bold]Telegraph Confidence:[/bold] {report.confidence * 100:.1f}%\n"
        f"[bold]Target Price:[/bold] {report.trade_parameters.get('target_price') or 'N/A'}\n"
        f"[bold]Stop Loss:[/bold] {report.trade_parameters.get('stop_loss') or 'N/A'}\n"
        f"[bold]Verification Hash:[/bold] [dim]{report.telegraph_verification_hash}[/dim]",
        title=f"🎯 Alpha Decision: {asset.value}",
        border_style=action_color
    ))

    # 2. Miners & Evaluator Breakdown Table
    table = Table(title="🔍 Telegraph Protocol Multi-Miner Evaluation Matrix")
    table.add_column("Miner", style="cyan")
    table.add_column("Model", style="magenta")
    table.add_column("Signal", style="bold")
    table.add_column("Latency", justify="right")
    table.add_column("Evaluator Score", justify="right")
    table.add_column("Verdict", justify="center")

    eval_map = {e.miner_id: e for e in report.raw_intelligence.evaluations}
    for miner in report.raw_intelligence.responses:
        ev = eval_map.get(miner.miner_id)
        score_str = f"{ev.final_rank_score:.2f}" if ev else "-"
        verdict_color = "green" if ev and ev.passed_benchmark else "red"
        verdict_str = f"[{verdict_color}]{ev.verdict}[/{verdict_color}]" if ev else "-"
        table.add_row(
            miner.miner_name,
            miner.model_family,
            miner.signal.value,
            f"{miner.latency_ms}ms",
            score_str,
            verdict_str
        )
    console.print(table)

    # 3. Key Drivers
    console.print("\n[bold]📌 Key Drivers & Audit Notes:[/bold]")
    for driver in report.key_drivers:
        console.print(f" • {driver}")

    if report.raw_intelligence.rogue_miners_detected:
        console.print(f"\n[bold red]⚠️ Rogue/Manipulated Signals Blocked by Evaluator:[/bold red] {', '.join(report.raw_intelligence.rogue_miners_detected)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Telegraph AlphaPulse Agent")
    parser.add_argument("--asset", default="BTC", choices=["BTC", "ETH", "SOL", "NVDA", "GOLD"])
    parser.add_argument("--scenario", default="NORMAL", choices=["NORMAL", "WHALE_ACCUMULATION", "FLASH_CRASH_RISK", "SPOOFING_MANIPULATION"])
    parser.add_argument("--mode", default="MOCK", choices=["MOCK", "LIVE"])
    args = parser.parse_args()

    run_cli(args.asset, args.scenario, args.mode)
