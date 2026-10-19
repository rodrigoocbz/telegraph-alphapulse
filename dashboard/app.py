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

st.set_page_config(
    page_title="AlphaPulse | Telegraph Protocol Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00FFA3, #00B8FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #8E9BAE;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
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
st.sidebar.markdown("**Telegraph Season II Engine**")

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

run_button = st.sidebar.button("🚀 Run Telegraph Verifiable Audit", type="primary", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Telegraph Hackathon Track: Apps & Agents**\n\n"
    "AlphaPulse acts as an autonomous financial risk & intelligence sentinel, "
    "evaluating multi-miner machine consensus before issuing high-stakes decisions."
)

# Header
st.markdown("<div class='main-title'>⚡ Telegraph AlphaPulse</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Autonomous Verifiable Financial Intelligence Agent · Telegraph Protocol Season II</div>", unsafe_allow_html=True)

# Run Agent logic
if "report" not in st.session_state or run_button:
    with st.spinner("Dispatching Intent to Telegraph Protocol network & running WASM evaluators..."):
        client = TelegraphClient(mode="MOCK")
        agent = AlphaPulseAgent(telegraph_client=client)
        st.session_state.report = agent.run_market_audit(selected_asset, scenario=scenario)
        st.session_state.candles = MarketDataProvider.get_historical_candles(selected_asset)

report = st.session_state.report
candles = st.session_state.candles

# Top Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label=f"{report.asset.value} Price",
        value=f"${report.current_price:,.2f}",
        delta=f"{scenario.replace('_', ' ')}"
    )

with col2:
    action_color = "🟢" if "BUY" in report.action.value else ("🔴" if "SELL" in report.action.value or "AVOID" in report.action.value else "🟡")
    st.metric(
        label="Alpha Action Decision",
        value=f"{action_color} {report.action.value}",
        delta=f"Risk: {report.trade_parameters.get('risk_level')}"
    )

with col3:
    st.metric(
        label="Telegraph Consensus",
        value=f"{int(report.confidence * 100)}%",
        delta="Verified by WASM Evaluators"
    )

with col4:
    st.metric(
        label="Top Rated Miner",
        value=report.top_miner_name.split('-')[0] + "...",
        delta=f"Model: {report.winning_model.split('-')[0]}"
    )

st.markdown("---")

# Main Section: Tabs
tab_charts, tab_matrix, tab_audit = st.tabs([
    "📈 Price & Verifiable Signals",
    "🔍 Telegraph Multi-Miner Matrix",
    "📜 Cryptographic Audit Trail"
])

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
        
        # Add target / stop-loss lines if applicable
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
        st.markdown(f"**Primary Decision:** `{report.action.value}`")
        st.markdown(f"**Recommended Sizing:** `{report.trade_parameters.get('recommended_position_sizing')}`")
        st.markdown(f"**Target Price:** `{report.trade_parameters.get('target_price') or 'None (Preserve Capital)'}`")
        st.markdown(f"**Stop Loss:** `{report.trade_parameters.get('stop_loss') or 'None'}`")
        
        st.markdown("**Key Drivers:**")
        for d in report.key_drivers:
            st.markdown(f"- {d}")

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

with tab_audit:
    st.subheader("Verifiable Intelligence Cryptographic Attestation")
    st.markdown(
        "Every decision made by AlphaPulse produces a cryptographic proof linking "
        "the market intent, participating miners, and evaluator scoring."
    )
    
    st.code(f"TELEGRAPH_PROOF_HASH: {report.telegraph_verification_hash}", language="bash")
    
    report_dict = report.model_dump(mode="json")
    st.download_button(
        label="📥 Download Verifiable Alpha Report (JSON)",
        data=json.dumps(report_dict, indent=2),
        file_name=f"alphapulse_{report.asset.value.replace('/', '_')}_{report.report_id}.json",
        mime="application/json"
    )
    
    st.json(report_dict)
