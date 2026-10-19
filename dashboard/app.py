import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import json
from datetime import datetime

import sys
import os
# Ensure root directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.models import MarketAsset, ActionDecision, SignalType
from core.agent import AlphaPulseAgent
from core.telegraph_client import TelegraphClient
from core.market_data import MarketDataProvider
from core.swarm import TelegraphSwarmArbiter
from core.backtest import QuantitativeBacktestEngine
from core.database import AlphaVaultDB
from core.crypto_attestation import CryptoAttestationService

st.set_page_config(
    page_title="AlphaPulse Swarm | Telegraph Protocol",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00FFA3, #00B8FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-bottom: 1.2rem;
    }
    .swarm-card {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .status-badge-approved {
        background-color: #064E3B;
        color: #34D399;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .status-badge-rejected {
        background-color: #7F1D1D;
        color: #F87171;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("### ⚙️ Protocol Parameters")
st.sidebar.markdown("**Telegraph Season II Swarm Engine**")

asset_label = st.sidebar.selectbox(
    "Asset to Audit",
    options=["BTC/USDT", "ETH/USDT", "SOL/USDT", "NVDA", "XAU/USD"],
    index=0
)
asset_enum_map = {
    "BTC/USDT": MarketAsset.BTC,
    "ETH/USDT": MarketAsset.ETH,
    "SOL/USDT": MarketAsset.SOL,
    "NVDA": MarketAsset.NVDA,
    "XAU/USD": MarketAsset.GOLD,
}
selected_asset = asset_enum_map[asset_label]

scenario = st.sidebar.selectbox(
    "Market Scenario Simulation",
    options=["NORMAL", "WHALE_ACCUMULATION", "FLASH_CRASH_RISK", "SPOOFING_MANIPULATION"],
    index=3,
    help="Simulates market stress events to demonstrate how Telegraph's evaluators filter bad signals."
)

mode = st.sidebar.radio(
    "Telegraph Network Mode",
    options=["MOCK_SIMULATION", "LIVE_SEASON_II_API"],
    index=0,
    help="Season II live connection kicks off on November 1st."
)

run_button = st.sidebar.button("🚀 Trigger Swarm & Telegraph Audit", type="primary", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info(
    "🏆 **Telegraph Hackathon Season II**\n\n"
    "Track: **Apps & Agents**\n\n"
    "**Architecture:** Multi-Agent Swarm + Telegraph WASM Evaluators + EIP-712 Smart Contract Verifier."
)

# Header
st.markdown("<div class='main-title'>⚡ Telegraph AlphaPulse Swarm</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Autonomous Verifiable Financial Intelligence Agent · Swarm Architecture & EIP-712 On-Chain Attestation</div>", unsafe_allow_html=True)

# Run Agent logic
if "report" not in st.session_state or run_button:
    with st.spinner("Executing Swarm reasoning, dispatching to Telegraph Protocol & generating EIP-712 signature..."):
        client = TelegraphClient(mode="MOCK")
        agent = AlphaPulseAgent(telegraph_client=client)
        arbiter = TelegraphSwarmArbiter(telegraph_client=client)
        
        snapshot = MarketDataProvider.get_market_snapshot(selected_asset, scenario=scenario)
        report = agent.run_market_audit(selected_asset, scenario=scenario)
        swarm_result = arbiter.arbitrate(selected_asset, snapshot)
        
        # Log to SQLite DB
        AlphaVaultDB.log_swarm_consensus(swarm_result, scenario, snapshot["current_price"])

        st.session_state.snapshot = snapshot
        st.session_state.report = report
        st.session_state.swarm_result = swarm_result
        st.session_state.candles = MarketDataProvider.get_historical_candles(selected_asset)

report = st.session_state.report
swarm_res = st.session_state.swarm_result
candles = st.session_state.candles
snapshot = st.session_state.snapshot

# Top Metrics Row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    source_tag = "🟢 Live" if snapshot.get("data_source") == "BINANCE_LIVE" else "⚪ Fallback"
    st.metric(
        label=f"{report.asset.value} ({source_tag})",
        value=f"${report.current_price:,.2f}",
        delta=f"{scenario.replace('_', ' ')}"
    )

with col2:
    action_color = "🟢" if "BUY" in report.action.value else ("🔴" if "SELL" in report.action.value or "AVOID" in report.action.value else "🟡")
    st.metric(
        label="Swarm Arbitrated Action",
        value=f"{action_color} {swarm_res.final_arbitrated_action.value}",
        delta=f"Risk: {report.trade_parameters.get('risk_level')}"
    )

with col3:
    st.metric(
        label="Telegraph Consensus",
        value=f"{int(swarm_res.final_confidence * 100)}%",
        delta="WASM Evaluated"
    )

with col4:
    st.metric(
        label="Top Evaluated Miner",
        value=report.top_miner_name.split('-')[0] + "...",
        delta=f"Model: {report.winning_model.split('-')[0]}"
    )

with col5:
    st.metric(
        label="EIP-712 Attestation",
        value="0x" + swarm_res.eip712_attestation['signer_address'][2:8] + "...",
        delta="Verified On-Chain"
    )

st.markdown("---")

# Main Section: Tabs
tab_charts, tab_swarm, tab_matrix, tab_backtest, tab_eip712, tab_db = st.tabs([
    "📈 Price & Verifiable Signals",
    "🐝 Swarm Reasoning",
    "🔍 Telegraph WASM Matrix",
    "📊 Backtest vs Raw LLMs",
    "🔐 Web3 EIP-712 Proof",
    "🗄️ Vault Database & Leaderboard"
])

# TAB 1: CHARTS & SIGNALS
with tab_charts:
    col_chart, col_details = st.columns([2.2, 1])
    
    with col_chart:
        st.subheader("Asset Telemetry & Target Bounds")
        fig = go.Figure(data=[go.Candlestick(
            x=candles['time'],
            open=candles['open'],
            high=candles['high'],
            low=candles['low'],
            close=candles['close'],
            name=report.asset.value
        )])
        
        if report.trade_parameters.get('target_price'):
            fig.add_hline(
                y=report.trade_parameters['target_price'],
                line_dash="dash",
                line_color="#00FFA3",
                annotation_text=f"Target: ${report.trade_parameters['target_price']:,.2f}",
                annotation_position="top right"
            )
        if report.trade_parameters.get('stop_loss'):
            fig.add_hline(
                y=report.trade_parameters['stop_loss'],
                line_dash="dash",
                line_color="#FF4B4B",
                annotation_text=f"Stop Loss: ${report.trade_parameters['stop_loss']:,.2f}",
                annotation_position="bottom right"
            )

        fig.update_layout(
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            height=420,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_details:
        st.subheader("🎯 Agent Synthesis")
        st.markdown(f"**Primary Decision:** `{swarm_res.final_arbitrated_action.value}`")
        st.markdown(f"**Recommended Sizing:** `{report.trade_parameters.get('recommended_position_sizing')}`")
        st.markdown(f"**Target Price:** `{report.trade_parameters.get('target_price') or 'None (Preserve Capital)'}`")
        st.markdown(f"**Stop Loss:** `{report.trade_parameters.get('stop_loss') or 'None'}`")
        
        st.markdown("**Key Drivers:**")
        for d in report.key_drivers:
            st.markdown(f"- {d}")

# TAB 2: SWARM REASONING
with tab_swarm:
    st.subheader("🐝 Multi-Agent Swarm Concurrency Breakdown")
    st.markdown(
        "AlphaPulse runs three specialized sub-agents concurrently. Their granular telemetry feeds "
        "into the **Telegraph Swarm Arbiter**, which packages them into high-dimensional Intents."
    )

    for thought in swarm_res.swarm_thoughts:
        with st.container():
            st.markdown(f"""
            <div class='swarm-card'>
                <h4 style='margin-top:0px; color:#00FFA3;'>🤖 {thought.agent_name} <span style='color:#94A3B8; font-size:0.9rem;'>({thought.role})</span></h4>
                <p><b>Observation:</b> {thought.key_observation}</p>
                <p><b>Signal Bias:</b> <code>{thought.signal_bias.value}</code> | <b>Confidence:</b> {int(thought.confidence*100)}% | <b>Anomaly Detected:</b> {'🚨 YES' if thought.detected_anomaly else '✅ NO'}</p>
            </div>
            """, unsafe_allow_html=True)

    st.info(f"**Arbiter Synthesis Narrative:**\n\n{swarm_res.execution_narrative}")

# TAB 3: TELEGRAPH WASM MATRIX
with tab_matrix:
    st.subheader("Telegraph Protocol WASM Evaluator Matrix")
    st.markdown(
        "Here you can inspect how competing miners responded to the Intent and how "
        "Telegraph's Evaluators scored accuracy, consistency, and slashed hallucinating/rogue miners."
    )

    eval_lookup = {e.miner_id: e for e in report.raw_intelligence.evaluations}
    for miner in report.raw_intelligence.responses:
        ev = eval_lookup.get(miner.miner_id)
        is_approved = ev.passed_benchmark if ev else False
        badge = (
            "<span class='status-badge-approved'>✓ APPROVED</span>" 
            if is_approved else 
            "<span class='status-badge-rejected'>✗ REJECTED / SLASHED</span>"
        )
        
        with st.expander(f"{'🟢' if is_approved else '🔴'} {miner.miner_name} · {miner.signal.value} ({int(miner.confidence*100)}% conf) — Latency: {miner.latency_ms}ms", expanded=not is_approved):
            st.markdown(f"**Model Family:** `{miner.model_family}` | **Evaluator Verdict:** {badge}", unsafe_allow_html=True)
            st.markdown(f"**Miner Proposed Reasoning:** *\"{miner.reasoning}\"*")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Accuracy Score", f"{ev.accuracy_score:.2f}" if ev else "-")
            c2.metric("Consistency Score", f"{ev.consistency_score:.2f}" if ev else "-")
            c3.metric("Hallucination Penalty", f"-{ev.hallucination_penalty:.2f}" if ev else "-")
            c4.metric("Final Rank Score", f"{ev.final_rank_score:.3f}" if ev else "-")
            
            if ev and ev.notes:
                st.markdown("**Evaluator Audit Notes:**")
                for note in ev.notes:
                    st.markdown(f"- `{note}`")

# TAB 4: QUANTITATIVE BACKTESTING
with tab_backtest:
    st.subheader("📊 60-Day Quantitative Backtest: Raw LLM vs Telegraph Swarm")
    st.markdown(
        "This quantitative simulation stress-tests both strategies across 60 market periods "
        "including whale accumulations, flash crashes, and liquidity spoofing attacks."
    )

    backtest_data = QuantitativeBacktestEngine.run_simulation(periods=60)
    summ = backtest_data["summary"]
    bdf = backtest_data["dataframe"]

    # Metric Row
    bcol1, bcol2, bcol3, bcol4 = st.columns(4)
    with bcol1:
        st.metric(
            "Telegraph Cumulative Return",
            f"+{summ['telegraph_total_return_pct']}%",
            delta=f"Final: ${summ['telegraph_final_capital']:,.0f}"
        )
    with bcol2:
        st.metric(
            "Raw LLM Return (Unverified)",
            f"{summ['raw_total_return_pct']}%",
            delta=f"Final: ${summ['raw_final_capital']:,.0f}",
            delta_color="inverse"
        )
    with bcol3:
        st.metric(
            "Sharpe Ratio (Telegraph vs Raw)",
            f"{summ['telegraph_sharpe']} vs {summ['raw_sharpe']}",
            delta="Risk-Adjusted Performance"
        )
    with bcol4:
        st.metric(
            "Spoofing Attacks Avoided",
            f"{summ['spoofing_attacks_avoided_pct']}%",
            delta=f"Max DD: {summ['telegraph_max_drawdown_pct']}% vs {summ['raw_max_drawdown_pct']}%"
        )

    # Plot Equity Curve
    fig_backtest = go.Figure()
    fig_backtest.add_trace(go.Scatter(
        x=bdf['date'],
        y=bdf['telegraph_capital'],
        mode='lines',
        name='⚡ Telegraph AlphaPulse Swarm',
        line=dict(color='#00FFA3', width=3)
    ))
    fig_backtest.add_trace(go.Scatter(
        x=bdf['date'],
        y=bdf['raw_capital'],
        mode='lines',
        name='❌ Raw Unverified LLM',
        line=dict(color='#FF4B4B', width=2, dash='dot')
    ))
    fig_backtest.update_layout(
        title="Equity Curve Comparison ($100k Starting Capital)",
        template="plotly_dark",
        height=380,
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis_title="Portfolio Capital ($ USD)"
    )
    st.plotly_chart(fig_backtest, use_container_width=True)

# TAB 5: EIP-712 ON-CHAIN ATTESTATION
with tab_eip712:
    st.subheader("🔐 EIP-712 Typed Data Cryptographic Attestation")
    st.markdown(
        "Every decision produced by AlphaPulse is signed using **EIP-712 Typed Data**, "
        "allowing smart contracts on Ethereum / Arbitrum / Base to verify the signature on-chain before executing swaps."
    )

    st.code(json.dumps(swarm_res.eip712_attestation, indent=2), language="json")

    st.markdown("#### 📜 Ready-to-Deploy Solidity Verifier Contract")
    solidity_code = CryptoAttestationService.generate_solidity_verifier_snippet()
    st.code(solidity_code, language="solidity")

# TAB 6: VAULT DATABASE & LEADERBOARD
with tab_db:
    st.subheader("🗄️ Persistent Vault Database (SQLite Telemetry)")
    
    col_hist, col_leader = st.columns([2, 1])
    
    with col_hist:
        st.markdown("#### Recent Cryptographic Audit Logs")
        recent_audits = AlphaVaultDB.get_recent_audits(10)
        if recent_audits:
            st.dataframe(pd.DataFrame(recent_audits)[['intent_id', 'asset', 'scenario', 'action', 'confidence', 'winning_miner', 'timestamp']], use_container_width=True)
        else:
            st.info("No audit logs recorded yet.")

    with col_leader:
        st.markdown("#### Miner Win-Rate Leaderboard")
        leaderboard = AlphaVaultDB.get_miner_leaderboard()
        if leaderboard:
            st.dataframe(pd.DataFrame(leaderboard), use_container_width=True)
        else:
            st.info("Leaderboard will populate as audits execute.")
