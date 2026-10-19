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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Minimalist Web3 Styling (Zero Emoji Spam)
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
        background-color: #07090E;
        color: #E2E8F0;
    }
    
    /* Header Area */
    .brand-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 0 18px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 24px;
    }
    .brand-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #FFFFFF;
        margin: 0;
    }
    .brand-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(0, 255, 163, 0.08);
        border: 1px solid rgba(0, 255, 163, 0.3);
        color: #00FFA3;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 3px 10px;
        border-radius: 4px;
        margin-left: 12px;
    }
    .brand-sub {
        color: #64748B;
        font-size: 0.88rem;
        margin-top: 4px;
        font-weight: 500;
    }
    
    /* Status Dots */
    .dot-live {
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #00FFA3;
        box-shadow: 0 0 8px #00FFA3;
        margin-right: 6px;
    }
    .dot-danger {
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #FF3B69;
        box-shadow: 0 0 8px #FF3B69;
        margin-right: 6px;
    }
    .dot-neutral {
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #94A3B8;
        margin-right: 6px;
    }
    
    /* Metric Cards */
    [data-testid="stMetric"] {
        background: #0B0F19;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 16px 18px;
        transition: border-color 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: rgba(0, 255, 163, 0.3);
    }
    [data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    [data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-size: 1.55rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    
    /* Modern Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #0B0F19;
        padding: 4px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.07);
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        color: #94A3B8;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 8px 16px;
        border: none !important;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #F8FAFC;
    }
    .stTabs [aria-selected="true"] {
        background: #131A2B !important;
        color: #00FFA3 !important;
        border: 1px solid rgba(0, 255, 163, 0.3) !important;
    }
    
    /* Clean Containers */
    .panel-card {
        background: #0B0F19;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 14px;
    }
    .panel-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Technical Badges */
    .badge-approved {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.35);
        color: #34D399;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
        letter-spacing: 0.05em;
    }
    .badge-slashed {
        background: rgba(239, 68, 68, 0.12);
        border: 1px solid rgba(239, 68, 68, 0.35);
        color: #F87171;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
        letter-spacing: 0.05em;
    }
    
    /* Custom Sidebar */
    [data-testid="stSidebar"] {
        background-color: #07090E;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    /* Primary Button */
    .stButton > button {
        background: #00FFA3 !important;
        color: #07090E !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 10px 20px !important;
        letter-spacing: 0.02em !important;
        transition: opacity 0.15s ease !important;
    }
    .stButton > button:hover {
        opacity: 0.9 !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("<h4 style='font-size:0.95rem; font-weight:700; color:#F8FAFC; margin-bottom:4px;'>SYSTEM PARAMETERS</h4>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='font-size:0.75rem; color:#64748B; margin-bottom:16px;'>TELEGRAPH PROTOCOL · SEASON II</div>", unsafe_allow_html=True)

asset_label = st.sidebar.selectbox(
    "Target Asset",
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
    "Stress Environment",
    options=["NORMAL", "WHALE_ACCUMULATION", "FLASH_CRASH_RISK", "SPOOFING_MANIPULATION"],
    index=3,
    help="Simulates market stress events to demonstrate how Telegraph's evaluators filter bad signals."
)

mode = st.sidebar.radio(
    "Network Mode",
    options=["MOCK_SIMULATION", "LIVE_SEASON_II_API"],
    index=0,
    help="Season II live connection kicks off on November 1st."
)

run_button = st.sidebar.button("Execute Swarm Audit", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='background:#0B0F19; padding:12px; border-radius:6px; border:1px solid rgba(255,255,255,0.06); font-size:0.78rem;'>
    <div style='color:#00FFA3; font-weight:700; margin-bottom:4px;'>TRACK: APPS & AGENTS</div>
    <div style='color:#94A3B8;'>
    AlphaPulse coordinates 3 deterministic micro-agents with Telegraph WASM scoring to deliver EIP-712 attested financial execution.
    </div>
</div>
""", unsafe_allow_html=True)

# Top Brand Bar (Minimalist)
st.markdown("""
<div class='brand-container'>
    <div>
        <div style='display:flex; align-items:center;'>
            <div class='brand-title'>ALPHAPULSE SWARM</div>
            <span class='brand-pill'>Protocol Season II</span>
        </div>
        <div class='brand-sub'>Autonomous Verifiable Financial Intelligence · Telegraph Protocol Architecture</div>
    </div>
    <div style='text-align:right; font-family:"JetBrains Mono"; font-size:0.78rem; color:#64748B;'>
        NETWORK: <span style='color:#00FFA3;'>TELEGRAPH-DEVNET-02</span><br>
        SIGNER: <span style='color:#00E5FF;'>0x90F8...C9C1</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Run Agent logic
if "report" not in st.session_state or run_button:
    with st.spinner("Dispatching intent, running WASM evaluations & signing EIP-712 payload..."):
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
    source_tag = "Live Feed" if snapshot.get("data_source") == "BINANCE_LIVE" else "Telemetry"
    st.metric(
        label=f"{report.asset.value} ({source_tag})",
        value=f"${report.current_price:,.2f}",
        delta=f"{scenario.replace('_', ' ')}"
    )

with col2:
    st.metric(
        label="Arbitrated Action",
        value=swarm_res.final_arbitrated_action.value,
        delta=f"Risk: {report.trade_parameters.get('risk_level')}"
    )

with col3:
    st.metric(
        label="Telegraph Consensus",
        value=f"{int(swarm_res.final_confidence * 100)}%",
        delta="WASM Validated"
    )

with col4:
    st.metric(
        label="Winning Miner",
        value=report.top_miner_name.split('-')[0],
        delta=f"Model: {report.winning_model.split('-')[0]}"
    )

with col5:
    st.metric(
        label="EIP-712 Attestation",
        value="0x" + swarm_res.eip712_attestation['signer_address'][2:8],
        delta="Attested On-Chain"
    )

st.markdown("<div style='margin-bottom: 18px;'></div>", unsafe_allow_html=True)

# Main Section: Tabs (Clean technical names)
tab_charts, tab_swarm, tab_matrix, tab_backtest, tab_eip712, tab_db = st.tabs([
    "Market Telemetry",
    "Swarm Reasoning",
    "WASM Evaluators",
    "Quantitative Benchmark",
    "EIP-712 Attestation",
    "Audit Ledger"
])

# TAB 1: CHARTS & SIGNALS
with tab_charts:
    col_chart, col_details = st.columns([2.3, 1])
    
    with col_chart:
        st.markdown("<div style='font-size:0.95rem; font-weight:700; color:#F8FAFC; margin-bottom:10px;'>ASSET TELEMETRY & TARGET BOUNDS</div>", unsafe_allow_html=True)
        fig = go.Figure(data=[go.Candlestick(
            x=candles['time'],
            open=candles['open'],
            high=candles['high'],
            low=candles['low'],
            close=candles['close'],
            name=report.asset.value,
            increasing_line_color='#00FFA3',
            decreasing_line_color='#FF3B69',
            increasing_fillcolor='rgba(0, 255, 163, 0.15)',
            decreasing_fillcolor='rgba(255, 59, 105, 0.15)'
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
            paper_bgcolor="#07090E",
            plot_bgcolor="#07090E",
            xaxis_rangeslider_visible=False,
            height=430,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.04)")
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_details:
        st.markdown("""
        <div class='panel-card'>
            <div style='font-size:0.9rem; font-weight:700; color:#F8FAFC; margin-bottom:12px;'>ACTION SYNTHESIS</div>
        """, unsafe_allow_html=True)
        st.markdown(f"**Decision:** `{swarm_res.final_arbitrated_action.value}`")
        st.markdown(f"**Position Sizing:** `{report.trade_parameters.get('recommended_position_sizing')}`")
        st.markdown(f"**Target Price:** `{report.trade_parameters.get('target_price') or 'Preserve Capital'}`")
        st.markdown(f"**Stop Loss:** `{report.trade_parameters.get('stop_loss') or 'Preserve Capital'}`")
        
        st.markdown("<div style='color:#64748B; font-size:0.78rem; font-weight:700; margin-top:14px; text-transform:uppercase;'>Key Drivers</div>", unsafe_allow_html=True)
        for d in report.key_drivers:
            st.markdown(f"<div style='font-size:0.82rem; color:#CBD5E1; margin:4px 0;'>• {d}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# TAB 2: SWARM REASONING
with tab_swarm:
    st.markdown("<div style='font-size:0.95rem; font-weight:700; color:#F8FAFC; margin-bottom:6px;'>MULTI-AGENT SWARM REASONING</div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='color:#64748B; font-size:0.85rem; margin-bottom:14px;'>"
        "Three specialized micro-agents independently analyze orderbooks, on-chain flows, and derivatives leverage before formatting high-dimensional Intents."
        "</div>", unsafe_allow_html=True
    )

    for thought in swarm_res.swarm_thoughts:
        badge_html = "<span class='badge-slashed'>ANOMALY DETECTED</span>" if thought.detected_anomaly else "<span class='badge-approved'>NORMAL</span>"
        st.markdown(f"""
        <div class='panel-card'>
            <div class='panel-header'>
                <div style='display:flex; align-items:center; gap:8px;'>
                    <span style='color:#00FFA3; font-weight:700; font-size:0.92rem;'>{thought.agent_name}</span>
                    <span style='color:#64748B; font-size:0.8rem;'>— {thought.role}</span>
                </div>
                {badge_html}
            </div>
            <div style='color:#E2E8F0; font-size:0.88rem; margin:6px 0 10px 0;'>{thought.key_observation}</div>
            <div style='font-family:"JetBrains Mono"; font-size:0.78rem; color:#94A3B8;'>
                BIAS: <span style='color:#F8FAFC;'>{thought.signal_bias.value}</span> | 
                CONFIDENCE: <span style='color:#00FFA3;'>{int(thought.confidence*100)}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background:rgba(0, 229, 255, 0.05); border:1px solid rgba(0, 229, 255, 0.25); border-radius:6px; padding:14px;'>
        <div style='color:#00E5FF; font-weight:700; font-size:0.82rem; margin-bottom:4px;'>ARBITER SYNTHESIS</div>
        <div style='color:#CBD5E1; font-size:0.88rem;'>{swarm_res.execution_narrative}</div>
    </div>
    """, unsafe_allow_html=True)

# TAB 3: WASM EVALUATORS
with tab_matrix:
    st.markdown("<div style='font-size:0.95rem; font-weight:700; color:#F8FAFC; margin-bottom:6px;'>TELEGRAPH PROTOCOL WASM EVALUATOR MATRIX</div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='color:#64748B; font-size:0.85rem; margin-bottom:14px;'>"
        "Miners compete to serve intents. Deterministic WebAssembly (WASM) scripts evaluate, rank, and slash hallucinating models in real time."
        "</div>", unsafe_allow_html=True
    )

    eval_lookup = {e.miner_id: e for e in report.raw_intelligence.evaluations}
    for miner in report.raw_intelligence.responses:
        ev = eval_lookup.get(miner.miner_id)
        is_approved = ev.passed_benchmark if ev else False
        badge = (
            "<span class='badge-approved'>APPROVED</span>" 
            if is_approved else 
            "<span class='badge-slashed'>REJECTED / SLASHED</span>"
        )
        status_dot = "<span class='dot-live'></span>" if is_approved else "<span class='dot-danger'></span>"
        
        with st.expander(f"{miner.miner_name} · {miner.signal.value} ({int(miner.confidence*100)}% conf) — {miner.latency_ms}ms", expanded=not is_approved):
            st.markdown(f"**Model Family:** `{miner.model_family}` | **Evaluator Verdict:** {badge}", unsafe_allow_html=True)
            st.markdown(f"**Miner Reasoning:** *\"{miner.reasoning}\"*")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Accuracy", f"{ev.accuracy_score:.2f}" if ev else "-")
            c2.metric("Consistency", f"{ev.consistency_score:.2f}" if ev else "-")
            c3.metric("Hallucination Penalty", f"-{ev.hallucination_penalty:.2f}" if ev else "-")
            c4.metric("Rank Score", f"{ev.final_rank_score:.3f}" if ev else "-")
            
            if ev and ev.notes:
                st.markdown("<div style='color:#64748B; font-size:0.75rem; font-weight:700; margin-top:8px;'>WASM AUDIT LOGS:</div>", unsafe_allow_html=True)
                for note in ev.notes:
                    st.markdown(f"<div style='font-family:\"JetBrains Mono\"; font-size:0.78rem; color:#F87171;'>• {note}</div>", unsafe_allow_html=True)

# TAB 4: QUANTITATIVE BACKTESTING
with tab_backtest:
    st.markdown("<div style='font-size:0.95rem; font-weight:700; color:#F8FAFC; margin-bottom:6px;'>60-DAY QUANTITATIVE BENCHMARK: RAW LLM VS TELEGRAPH SWARM</div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='color:#64748B; font-size:0.85rem; margin-bottom:14px;'>"
        "Statistical simulation across 60 market periods with whale flows, liquidation cascades, and spoofing attacks."
        "</div>", unsafe_allow_html=True
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
        name='Telegraph AlphaPulse Swarm',
        line=dict(color='#00FFA3', width=2.5)
    ))
    fig_backtest.add_trace(go.Scatter(
        x=bdf['date'],
        y=bdf['raw_capital'],
        mode='lines',
        name='Raw Unverified LLM',
        line=dict(color='#FF3B69', width=1.8, dash='dot')
    ))
    fig_backtest.update_layout(
        title="Portfolio Equity Curve ($100,000 USD Base)",
        template="plotly_dark",
        paper_bgcolor="#07090E",
        plot_bgcolor="#07090E",
        height=380,
        margin=dict(l=20, r=20, t=50, b=20),
        yaxis_title="Portfolio Value ($ USD)",
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)")
    )
    st.plotly_chart(fig_backtest, use_container_width=True)

# TAB 5: EIP-712 ON-CHAIN ATTESTATION
with tab_eip712:
    st.markdown("<div style='font-size:0.95rem; font-weight:700; color:#F8FAFC; margin-bottom:6px;'>EIP-712 TYPED DATA CRYPTOGRAPHIC ATTESTATION</div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='color:#64748B; font-size:0.85rem; margin-bottom:14px;'>"
        "Every signal produced by AlphaPulse generates a cryptographically signed payload compatible with Ethereum, Arbitrum, and Base smart contracts."
        "</div>", unsafe_allow_html=True
    )

    st.code(json.dumps(swarm_res.eip712_attestation, indent=2), language="json")

    st.markdown("<div style='font-size:0.9rem; font-weight:700; color:#F8FAFC; margin:16px 0 8px 0;'>SOLIDITY ON-CHAIN VERIFIER CONTRACT</div>", unsafe_allow_html=True)
    solidity_code = CryptoAttestationService.generate_solidity_verifier_snippet()
    st.code(solidity_code, language="solidity")

# TAB 6: VAULT DATABASE & LEADERBOARD
with tab_db:
    st.markdown("<div style='font-size:0.95rem; font-weight:700; color:#F8FAFC; margin-bottom:6px;'>PERSISTENT VAULT TELEMETRY DATABASE (SQLITE)</div>", unsafe_allow_html=True)
    
    col_hist, col_leader = st.columns([2, 1])
    
    with col_hist:
        st.markdown("<div style='color:#64748B; font-size:0.78rem; font-weight:700; margin-bottom:8px;'>RECENT AUDIT LOGS</div>", unsafe_allow_html=True)
        recent_audits = AlphaVaultDB.get_recent_audits(10)
        if recent_audits:
            st.dataframe(
                pd.DataFrame(recent_audits)[['intent_id', 'asset', 'scenario', 'action', 'confidence', 'winning_miner', 'timestamp']],
                use_container_width=True
            )
        else:
            st.info("No audit logs recorded yet.")

    with col_leader:
        st.markdown("<div style='color:#64748B; font-size:0.78rem; font-weight:700; margin-bottom:8px;'>MINER PERFORMANCE RANKING</div>", unsafe_allow_html=True)
        leaderboard = AlphaVaultDB.get_miner_leaderboard()
        if leaderboard:
            st.dataframe(pd.DataFrame(leaderboard), use_container_width=True)
        else:
            st.info("Leaderboard will populate as audits execute.")
