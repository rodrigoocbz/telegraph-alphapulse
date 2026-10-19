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
    page_title="AlphaPulse Terminal · Telegraph Protocol",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Web3 / Bloomberg Terminal Styling
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

<style>
    /* Global Base */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }
    .stApp {
        background-color: #060913;
        color: #E2E8F0;
    }
    
    /* Header Area */
    .brand-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 0 20px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 24px;
    }
    .brand-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #FFFFFF 20%, #94A3B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .brand-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(0, 255, 163, 0.1);
        border: 1px solid rgba(0, 255, 163, 0.35);
        color: #00FFA3;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 4px 12px;
        border-radius: 9999px;
        vertical-align: middle;
        margin-left: 10px;
    }
    .brand-sub {
        color: #64748B;
        font-size: 0.95rem;
        margin-top: 4px;
        font-weight: 500;
    }
    
    /* Custom Metric Cards */
    [data-testid="stMetric"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.8) 0%, rgba(10, 15, 29, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: rgba(0, 255, 163, 0.3);
        transform: translateY(-2px);
    }
    [data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    
    /* Modern Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0B1120;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 600;
        font-size: 0.9rem;
        padding: 8px 18px;
        border: none !important;
        background: transparent;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #F8FAFC;
        background: rgba(255, 255, 255, 0.03);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 255, 163, 0.15), rgba(0, 229, 255, 0.15)) !important;
        color: #00FFA3 !important;
        border: 1px solid rgba(0, 255, 163, 0.4) !important;
        box-shadow: 0 0 15px rgba(0, 255, 163, 0.1);
    }
    
    /* Glassmorphism Containers */
    .glass-card {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.6) 0%, rgba(11, 17, 32, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        backdrop-filter: blur(12px);
    }
    .glass-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
    }
    
    /* Status Pills */
    .badge-approved {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34D399;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-slashed {
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.4);
        color: #F87171;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-neutral {
        background: rgba(148, 163, 184, 0.1);
        border: 1px solid rgba(148, 163, 184, 0.3);
        color: #94A3B8;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 6px;
    }
    
    /* Streamlit Expander Overrides */
    .streamlit-expanderHeader {
        background: #0B1120 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        color: #E2E8F0 !important;
        font-weight: 600 !important;
    }
    .streamlit-expanderContent {
        background: #070B14 !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-top: none !important;
        border-bottom-left-radius: 10px !important;
        border-bottom-right-radius: 10px !important;
    }
    
    /* Custom Sidebar */
    [data-testid="stSidebar"] {
        background-color: #070B14;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    /* Primary Button */
    .stButton > button {
        background: linear-gradient(135deg, #00FFA3 0%, #00B8FF 100%) !important;
        color: #060913 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 15px rgba(0, 255, 163, 0.25) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    .stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 6px 22px rgba(0, 255, 163, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("### 🎛️ Control Panel")
st.sidebar.markdown("<small style='color:#64748B;'>TELEGRAPH PROTOCOL · SEASON II</small>", unsafe_allow_html=True)

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

run_button = st.sidebar.button("⚡ Run Telegraph Swarm Audit", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='background:#0B1120; padding:14px; border-radius:10px; border:1px solid rgba(255,255,255,0.06); font-size:0.82rem;'>
    <b style='color:#00FFA3;'>🏆 Hackathon Track: Apps & Agents</b><br>
    <span style='color:#94A3B8;'>
    AlphaPulse unites 3 autonomous agents with Telegraph's WASM scoring engine to produce trustless, EIP-712 verifiable trading decisions.
    </span>
</div>
""", unsafe_allow_html=True)

# Top Brand Bar
st.markdown("""
<div class='brand-container'>
    <div>
        <div style='display:flex; align-items:center;'>
            <h1 class='brand-title'>⚡ AlphaPulse Swarm</h1>
            <span class='brand-pill'>Season II Ready</span>
        </div>
        <div class='brand-sub'>Autonomous Verifiable Financial Intelligence · Telegraph Protocol Architecture</div>
    </div>
    <div style='text-align:right; font-family:"JetBrains Mono"; font-size:0.8rem; color:#64748B;'>
        NETWORK: <span style='color:#00FFA3;'>TELEGRAPH-DEVNET-02</span><br>
        ATTESTOR: <span style='color:#00E5FF;'>0x90F8...C9C1</span>
    </div>
</div>
""", unsafe_allow_html=True)

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

# Top KPI Row
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
        label="EIP-712 Signer",
        value="0x" + swarm_res.eip712_attestation['signer_address'][2:8] + "...",
        delta="Verified On-Chain"
    )

st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# Main Section: Tabs
tab_charts, tab_swarm, tab_matrix, tab_backtest, tab_eip712, tab_db = st.tabs([
    "📈 Price & Signals",
    "🐝 Swarm Reasoning",
    "🔍 WASM Evaluator Matrix",
    "📊 Backtest vs Raw LLM",
    "🔐 Web3 EIP-712 Proof",
    "🗄️ Vault Database"
])

# TAB 1: CHARTS & SIGNALS
with tab_charts:
    col_chart, col_details = st.columns([2.3, 1])
    
    with col_chart:
        st.markdown("<h4 style='font-size:1.1rem; color:#F8FAFC; margin-bottom:12px;'>Real-Time Telemetry & Target Bounds</h4>", unsafe_allow_html=True)
        fig = go.Figure(data=[go.Candlestick(
            x=candles['time'],
            open=candles['open'],
            high=candles['high'],
            low=candles['low'],
            close=candles['close'],
            name=report.asset.value,
            increasing_line_color='#00FFA3',
            decreasing_line_color='#FF3B69',
            increasing_fillcolor='rgba(0, 255, 163, 0.2)',
            decreasing_fillcolor='rgba(255, 59, 105, 0.2)'
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
                line_color="#FF3B69",
                annotation_text=f"Stop: ${report.trade_parameters['stop_loss']:,.2f}",
                annotation_position="bottom right"
            )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#070B14",
            plot_bgcolor="#070B14",
            xaxis_rangeslider_visible=False,
            height=430,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_details:
        st.markdown("""
        <div class='glass-card'>
            <h4 style='font-size:1.05rem; margin-top:0; color:#F8FAFC;'>🎯 Action Synthesis</h4>
        """, unsafe_allow_html=True)
        st.markdown(f"**Decision:** `{swarm_res.final_arbitrated_action.value}`")
        st.markdown(f"**Position Sizing:** `{report.trade_parameters.get('recommended_position_sizing')}`")
        st.markdown(f"**Target Price:** `{report.trade_parameters.get('target_price') or 'Preserve Capital'}`")
        st.markdown(f"**Stop Loss:** `{report.trade_parameters.get('stop_loss') or 'Preserve Capital'}`")
        
        st.markdown("<b style='color:#94A3B8; font-size:0.85rem;'>KEY DRIVERS:</b>", unsafe_allow_html=True)
        for d in report.key_drivers:
            st.markdown(f"<span style='font-size:0.85rem;'>• {d}</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# TAB 2: SWARM REASONING
with tab_swarm:
    st.markdown("<h4 style='font-size:1.1rem; color:#F8FAFC; margin-bottom:12px;'>🐝 Multi-Agent Swarm Concurrency Breakdown</h4>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#94A3B8; font-size:0.9rem;'>"
        "Three specialized sub-agents independently interrogate orderbooks, on-chain flows, and derivatives leverage. "
        "Their telemetry feeds into the <b>Telegraph Arbiter</b> to format high-dimensional Intents."
        "</p>", unsafe_allow_html=True
    )

    for thought in swarm_res.swarm_thoughts:
        badge_html = "<span class='badge-slashed'>🚨 ANOMALY DETECTED</span>" if thought.detected_anomaly else "<span class='badge-approved'>✓ NORMAL</span>"
        st.markdown(f"""
        <div class='glass-card'>
            <div class='glass-card-header'>
                <div style='display:flex; align-items:center; gap:8px;'>
                    <b style='color:#00FFA3; font-size:1rem;'>🤖 {thought.agent_name}</b>
                    <span style='color:#64748B; font-size:0.85rem;'>· {thought.role}</span>
                </div>
                {badge_html}
            </div>
            <p style='color:#E2E8F0; font-size:0.92rem; margin:8px 0;'>{thought.key_observation}</p>
            <div style='font-family:"JetBrains Mono"; font-size:0.8rem; color:#94A3B8;'>
                BIAS: <span style='color:#F8FAFC;'>{thought.signal_bias.value}</span> | 
                CONFIDENCE: <span style='color:#00E5FF;'>{int(thought.confidence*100)}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background:rgba(0, 229, 255, 0.08); border:1px solid rgba(0, 229, 255, 0.3); border-radius:12px; padding:16px;'>
        <b style='color:#00E5FF;'>⚖️ Arbiter Cross-Examination Synthesis:</b><br>
        <span style='color:#E2E8F0; font-size:0.92rem;'>{swarm_res.execution_narrative}</span>
    </div>
    """, unsafe_allow_html=True)

# TAB 3: TELEGRAPH WASM MATRIX
with tab_matrix:
    st.markdown("<h4 style='font-size:1.1rem; color:#F8FAFC; margin-bottom:12px;'>🔍 Telegraph Protocol WASM Evaluator Matrix</h4>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#94A3B8; font-size:0.9rem;'>"
        "Miners compete to serve intents. Deterministic WebAssembly (WASM) scripts evaluate, rank, and slash hallucinating models in real time."
        "</p>", unsafe_allow_html=True
    )

    eval_lookup = {e.miner_id: e for e in report.raw_intelligence.evaluations}
    for miner in report.raw_intelligence.responses:
        ev = eval_lookup.get(miner.miner_id)
        is_approved = ev.passed_benchmark if ev else False
        badge = (
            "<span class='badge-approved'>✓ APPROVED</span>" 
            if is_approved else 
            "<span class='badge-slashed'>✗ REJECTED / SLASHED</span>"
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
                st.markdown("<b style='color:#94A3B8; font-size:0.85rem;'>WASM AUDIT LOGS:</b>", unsafe_allow_html=True)
                for note in ev.notes:
                    st.markdown(f"<span style='font-family:\"JetBrains Mono\"; font-size:0.8rem; color:#F87171;'>• {note}</span>", unsafe_allow_html=True)

# TAB 4: QUANTITATIVE BACKTESTING
with tab_backtest:
    st.markdown("<h4 style='font-size:1.1rem; color:#F8FAFC; margin-bottom:12px;'>📊 60-Day Quantitative Backtest: Raw LLMs vs Telegraph Swarm</h4>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#94A3B8; font-size:0.9rem;'>"
        "Empirical mathematical comparison over 60 simulated market periods with whale flows, liquidation cascades, and spoofing attacks."
        "</p>", unsafe_allow_html=True
    )

    backtest_data = QuantitativeBacktestEngine.run_simulation(periods=60)
    summ = backtest_data["summary"]
    bdf = backtest_data["dataframe"]

    # Metric Row
    bcol1, bcol2, bcol3, bcol4 = st.columns(4)
    with bcol1:
        st.metric(
            "Telegraph Alpha Return",
            f"+{summ['telegraph_total_return_pct']}%",
            delta=f"Capital: ${summ['telegraph_final_capital']:,.0f}"
        )
    with bcol2:
        st.metric(
            "Raw Unverified LLM",
            f"{summ['raw_total_return_pct']}%",
            delta=f"Capital: ${summ['raw_final_capital']:,.0f}",
            delta_color="inverse"
        )
    with bcol3:
        st.metric(
            "Sharpe Ratio (TG vs Raw)",
            f"{summ['telegraph_sharpe']} vs {summ['raw_sharpe']}",
            delta="Annualized Risk-Adjusted"
        )
    with bcol4:
        st.metric(
            "Spoofing Attacks Avoided",
            f"{summ['spoofing_attacks_avoided_pct']}%",
            delta=f"Max DD: {summ['telegraph_max_drawdown_pct']}%"
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
        line=dict(color='#FF3B69', width=2, dash='dot')
    ))
    fig_backtest.update_layout(
        title="Portfolio Equity Curve ($100,000 USD Base)",
        template="plotly_dark",
        paper_bgcolor="#070B14",
        plot_bgcolor="#070B14",
        height=380,
        margin=dict(l=20, r=20, t=50, b=20),
        yaxis_title="Portfolio Value ($ USD)",
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
    )
    st.plotly_chart(fig_backtest, use_container_width=True)

# TAB 5: EIP-712 ON-CHAIN ATTESTATION
with tab_eip712:
    st.markdown("<h4 style='font-size:1.1rem; color:#F8FAFC; margin-bottom:12px;'>🔐 EIP-712 Typed Data Cryptographic Attestation</h4>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#94A3B8; font-size:0.9rem;'>"
        "Every signal produced by AlphaPulse generates a cryptographically signed payload compatible with Ethereum, Arbitrum, and Base smart contracts."
        "</p>", unsafe_allow_html=True
    )

    st.code(json.dumps(swarm_res.eip712_attestation, indent=2), language="json")

    st.markdown("<h5 style='font-size:1rem; color:#F8FAFC; margin-top:20px;'>📜 Ready-to-Deploy Solidity Verifier Contract</h5>", unsafe_allow_html=True)
    solidity_code = CryptoAttestationService.generate_solidity_verifier_snippet()
    st.code(solidity_code, language="solidity")

# TAB 6: VAULT DATABASE & LEADERBOARD
with tab_db:
    st.markdown("<h4 style='font-size:1.1rem; color:#F8FAFC; margin-bottom:12px;'>🗄️ Persistent Vault Telemetry Database (SQLite)</h4>", unsafe_allow_html=True)
    
    col_hist, col_leader = st.columns([2, 1])
    
    with col_hist:
        st.markdown("<b style='color:#94A3B8;'>RECENT AUDIT LOGS:</b>", unsafe_allow_html=True)
        recent_audits = AlphaVaultDB.get_recent_audits(10)
        if recent_audits:
            st.dataframe(
                pd.DataFrame(recent_audits)[['intent_id', 'asset', 'scenario', 'action', 'confidence', 'winning_miner', 'timestamp']],
                use_container_width=True
            )
        else:
            st.info("No audit logs recorded yet.")

    with col_leader:
        st.markdown("<b style='color:#94A3B8;'>MINER WIN-RATE LEADERBOARD:</b>", unsafe_allow_html=True)
        leaderboard = AlphaVaultDB.get_miner_leaderboard()
        if leaderboard:
            st.dataframe(pd.DataFrame(leaderboard), use_container_width=True)
        else:
            st.info("Leaderboard will populate as audits execute.")
