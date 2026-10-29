# TELEGRAPH PROTOCOL HACKATHON SEASON II - PROJECT HANDOVER
**Project Name:** AlphaPulse Swarm  
**Track:** Apps & Agents  
**Missions:** 03 (Institutional Markets) / 13 (Asset Management) / 14 (Web3 Native & DeFi)  
**Author:** Rodrigo (`rodrigoocbz`)  
**Repo:** https://github.com/rodrigoocbz/telegraph-alphapulse  
**Date of Handover:** October 26, 2026  

---

## 1. Executive Summary & Purpose
AlphaPulse Swarm is an autonomous institutional financial intelligence agent and audit system. It consumes machine intelligence from Telegraph Protocol's decentralized miner network to analyze market microstructure, whale liquidity, and macro volatility across crypto assets (BTC, ETH, SOL, etc.).

Dual-Track Submission:
1. **Apps & Agents Track:** Autonomous financial intelligence multi-agent swarm with EIP-712 on-chain attestation and institutional telemetry dashboard.
2. **Evaluators Track:** Verified contributor to the on-chain evaluation pool (5 admitted preference pairs on `ONCHAIN_TX_LOOKUP_GENERAL`, timestamp 2026-10-29 17:21:46 UTC+1).

Key Value Proposition:
- Solves AI hallucinations in financial decisions by routing Intents to multiple independent miners.
- Uses simulated WASM Evaluators to score miner predictions and slash rogue/inaccurate providers.
- Signs verifiable audit reports using Ethereum standard EIP-712 typed signatures, allowing on-chain smart contracts (Arbitrum/Base) to enforce autonomous actions.
- Provides an institutional Streamlit dashboard (zero emojis, dark theme) and an autonomous Telegram Sentinel bot (`@AlphaPulseSentinel_bot`).

---

## 2. Competition Rules & Dates (Season II)
- **Start Date:** November 1, 2026.
- **Submission Deadline:** December 1, 2026 at 23:59 UTC (December 2, 00:59 Madrid). Recommended delivery: November 30.
- **Prizes:** $10,000 pool for H2 ($3,000 for Apps & Agents: 8 x $225 delivery prizes + $700 / $350 / $150 excellence prizes; $2,000 for Evaluators: 4 x $300 delivery + $500 / $300 excellence).
- **Official Wallet (Registered):** `0xEaEe4a29F32E66C37603DDe482f85da6c56B9953`
- **Minimum Qualifying Score:** 70/100 points (minimum 24/35 in technical quality).
- **Core Requirement:** Must perform a genuine machine-to-machine purchase/operation via Telegraph (testnet supported, e.g., Base Sepolia USDC). External direct API calls without Telegraph are not eligible.

---

## 3. Architecture & Repository Structure
- `core/models.py`: Pydantic models for Intents, Miners, Evaluators, and Audit Reports.
- `core/market_data.py`: Live Binance REST API client + market stress simulation engine.
- `core/telegraph_client.py`: Client for Telegraph network. Currently has MOCK simulation mode and a placeholder `_call_live_telegraph` method ready for Telegraph V2 SDK.
- `core/swarm.py`: Multi-agent swarm (WhaleSentinel, MicrostructureAgent, MacroVolatilityAgent) with `TelegraphSwarmArbiter`.
- `core/backtest.py`: 60-period quantitative backtesting engine (Sharpe, drawdown, win rate).
- `core/crypto_attestation.py`: EIP-712 typed signing engine and Solidity contract (`TelegraphAutonomousExecutor.sol`).
- `core/database.py`: SQLite telemetry audit persistence (`alphapulse_vault.db`).
- `core/websocket_feed.py`: Binance 100ms async depth feed.
- `dashboard/app.py`: Streamlit institutional terminal (6 tabs). Run with: `streamlit run dashboard/app.py`.
- `sentinel_bot.py`: Telegram bot daemon (`/audit`, `/simulate`, `/backtest`, `/status`).
- `main.py`: Interactive CLI runner with Rich console output.
- `tests/test_agent.py`: 6 unit tests (all passing).
- `Dockerfile` & `docker-compose.yml`: Production container setup.
- `LICENSE`: MIT License.

---

## 4. Current Environment & Credentials
- Local path: `/Users/alumnoad/.gemini/antigravity/scratch/telegraph-alpha-agent`
- Virtual environment: `.venv` (Python 3.9+)
- Telegram Bot: `@AlphaPulseSentinel_bot` (Token & chat ID stored in `.env` locally)
- Dependencies installed: `pydantic`, `streamlit`, `web3`, `eth-account`, `httpx`, `python-telegram-bot`, `rich`, `pytest`, `plotly`, `pandas`.

---

## 5. Next Steps for Codex / Future Developer (November 1 Kickoff)
1. Check Telegraph Discord (`#announcements`, `#help`, `#hackathon`) for the official **V2 SDK / REST endpoints** and Base Sepolia testnet faucet (USDC / Gas).
2. Update `core/telegraph_client.py` to replace the `NotImplementedError` in `_call_live_telegraph` with the real Telegraph V2 SDK / HTTP calls using `X-PAYMENT` and `receipt_hash` headers.
3. Verify that receipt hashes and epoch IDs are stored in `alphapulse_vault.db` to serve as verifiable evidence for hackathon judges.
4. Record a 2 to 4 minute demo video following the official rubric:
   - Problem & User definition (30s)
   - Running live input & swarm analysis (45s)
   - Telegraph purchase evidence (Intent, provider, receipt, cost) (60s)
   - Practical output & backtest/attestation results (45s)
   - Graceful failure handling test (timeout / balance) (30s)
5. Submit project via official H2 portal before November 30.
