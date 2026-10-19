# AlphaPulse Swarm

> Autonomous Verifiable Financial Intelligence Agent for Telegraph Protocol Season II  
> Architecture: Multi-Agent Swarm · WASM Evaluator Arbitration · EIP-712 On-Chain Attestation

[![Tests: Passing](https://img.shields.io/badge/tests-passing-00FFA3.svg?style=flat-square)](https://github.com/rodrigoocbz/telegraph-alphapulse)
[![Python](https://img.shields.io/badge/python-3.9+-0B0F19.svg?style=flat-square)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-0B0F19.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Telegraph Protocol](https://img.shields.io/badge/telegraph-season_ii-0B0F19.svg?style=flat-square)](https://telegraphprotocol.com)
[![Docker](https://img.shields.io/badge/docker-ready-0B0F19.svg?style=flat-square)](https://www.docker.com/)
[![Web3: EIP-712](https://img.shields.io/badge/eip-712-verified-0B0F19.svg?style=flat-square)](https://eips.ethereum.org/EIPS/eip-712)

AlphaPulse Swarm is an autonomous financial risk sentinel and alpha generation engine built for the **Telegraph Protocol Season II Hackathon** (Track: **Apps & Agents**).

In high-stakes financial and decentralized finance (DeFi) environments, relying on unverified single-model LLM predictions or raw unverified API feeds introduces significant systemic risk due to hallucinations, orderbook manipulation, wash trading, and liquidity spoofing. AlphaPulse addresses this vulnerability by coordinating a **specialized multi-agent swarm**, formatting high-dimensional financial intents for **Telegraph's decentralized intelligence marketplace**, and executing trades strictly when competing miners achieve verifiable consensus scored by deterministic **WASM evaluators**, cryptographically attested through **EIP-712 structured data signatures**.

---

## Core Capabilities

- **Multi-Agent Swarm Architecture:** Executes three concurrent specialized sub-agents (`WhaleSentinel`, `MicrostructureAgent`, `MacroVolatilityAgent`) coordinated by an arbitration layer (`TelegraphSwarmArbiter`).
- **High-Frequency WebSocket Telemetry (100ms):** Direct asynchronous stream connection to Binance orderbook depth (`@depth20@100ms`), catching microsecond bid-wall spoofing patterns before they hit candle bars.
- **Deterministic WASM Validation:** Interrogates Telegraph's WebAssembly evaluation sandbox to penalize hallucinated or manipulated miner proposals (applying up to 95% penalty slashes during spoofing attacks).
- **Quantitative Simulation Engine:** Includes a 60-period empirical backtesting framework comparing unverified LLM baselines against Telegraph-validated consensus, evaluating Sharpe ratios, Sortino ratios, and maximum drawdown.
- **EIP-712 Cryptographic Attestation:** Every arbitrated trade recommendation is signed as an EIP-712 typed structured data hash, verifiable on-chain via EVM smart contracts.
- **On-Chain Settlement Verification:** Includes a deployment and verification suite (`scripts/deploy_contract.py`) tested directly against Arbitrum Sepolia RPC.
- **Autonomous Telegram Sentinel:** Long-polling notification daemon supporting interactive mobile audits (`/audit`, `/simulate`, `/backtest`, `/status`).
- **Production-Ready Docker Stack:** Multi-stage `Dockerfile` and `docker-compose.yml` for unified single-command deployment of the terminal and background sentinel daemon.
- **Automated CI/CD Pipeline:** Fully configured GitHub Actions workflow verifying test coverage, syntax, and execution on every commit.

---

## System Architecture

```mermaid
flowchart TD
    subgraph Market ["High-Frequency Market Telemetry"]
        BinanceWS["Binance 100ms WebSocket Stream"]
        BinanceREST["Binance Public REST API"]
        OnChain["On-Chain Wallet Flows"]
    end

    subgraph Swarm ["AlphaPulse Multi-Agent Swarm"]
        Whale["WhaleSentinel Agent"]
        Micro["Microstructure Agent"]
        Macro["MacroVolatility Agent"]
        Arbiter["Telegraph Swarm Arbiter"]
    end

    subgraph Protocol ["Telegraph Protocol Network"]
        Intent["High-Dimensional Intent Payload"]
        Miners["Competing Miner Nodes (Mistral, DeepSeek, LLaMA, Unverified)"]
        WASM["WASM Deterministic Evaluator Sandbox"]
        Consensus["Ranked Verifiable Consensus Output"]
    end

    subgraph Execution ["Execution & Settlement Layer"]
        EIP712["EIP-712 Typed Cryptographic Attestation"]
        DB[("SQLite Audit Vault")]
        Streamlit["Terminal Dashboard"]
        Telegram["Autonomous Telegram Sentinel"]
        SmartContract["Arbitrum Sepolia Smart Contract"]
    end

    Market --> Swarm
    Whale & Micro & Macro --> Arbiter
    Arbiter --> Intent
    Intent --> Miners
    Miners --> WASM
    WASM --> Consensus
    Consensus --> Arbiter
    Arbiter --> EIP712
    Arbiter --> DB
    EIP712 --> Streamlit & Telegram & SmartContract
```

---

## Repository Structure

```
telegraph-alpha-agent/
├── ci/
│   └── ci.yml                # Automated CI test pipeline specification
├── core/
│   ├── models.py             # Pydantic schemas for Intents, Miners, Evaluators, and Reports
│   ├── market_data.py        # Live Binance market data and stress simulation scenarios
│   ├── websocket_feed.py     # Real-time 100ms WebSocket orderbook depth stream
│   ├── telegraph_client.py   # Dual-mode Telegraph Protocol client (MOCK simulation & LIVE Season II)
│   ├── agent.py              # Autonomous Alpha synthesis engine
│   ├── swarm.py              # Multi-Agent Swarm (Whale, Micro, Macro) and Arbiter
│   ├── backtest.py           # Quantitative backtesting simulation engine and metrics
│   ├── crypto_attestation.py # EIP-712 typed data signing and Solidity verification contract
│   └── database.py           # Persistent SQLite audit telemetry and miner leaderboard
├── dashboard/
│   └── app.py                # Streamlit quantitative terminal interface
├── scripts/
│   └── deploy_contract.py    # Arbitrum Sepolia on-chain verification script
├── tests/
│   └── test_agent.py         # Test suite covering Swarm, crypto, and backtest logic
├── sentinel_bot.py           # Autonomous Telegram Sentinel daemon
├── main.py                   # Terminal CLI runner
├── Dockerfile                # Production multi-stage Docker build
├── docker-compose.yml        # Orchestration for Terminal and Sentinel daemon
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
└── README.md
```

---

## Installation & Quick Start

### Option A: Local Virtual Environment

```bash
git clone https://github.com/rodrigoocbz/telegraph-alphapulse.git
cd telegraph-alphapulse
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run test suite:
```bash
python tests/test_agent.py
```

Launch the quantitative terminal:
```bash
streamlit run dashboard/app.py
```

Run on-chain Arbitrum Sepolia verification test:
```bash
python scripts/deploy_contract.py
```

### Option B: Production Docker Deployment

Run the complete multi-container stack (Terminal + Telegram Sentinel Daemon):

```bash
docker compose up -d --build
```

---

## Terminal Features

The interface is accessible at `http://localhost:8501`, featuring:
- **Market Telemetry:** Real-time candlestick series and dynamic target bounds.
- **Swarm Reasoning:** Independent telemetry contributions from concurrent sub-agents.
- **WASM Evaluators:** Multi-miner accuracy, consistency, latency, and penalty rankings.
- **Quantitative Benchmark:** Historical capital growth curves and risk-adjusted metrics.
- **EIP-712 Attestation:** Structured data JSON payload and Solidity smart contract verifier.
- **Audit Ledger:** Historical transaction records and miner win-rate metrics.

---

## Autonomous Telegram Sentinel

Run the sentinel daemon:
```bash
python sentinel_bot.py
```

Supported commands:
- `/audit BTC` - Execute live Swarm and Telegraph evaluation on Bitcoin.
- `/simulate spoofing` - Inject synthetic orderbook spoofing to verify evaluator defense.
- `/backtest` - Retrieve 60-period quantitative benchmark summary.
- `/status` - Check daemon, WASM sandbox, and protocol connectivity.

---

## On-Chain Verification (Solidity)

AlphaPulse outputs standard **EIP-712 typed signatures** verifiable on Ethereum, Arbitrum, or Base:

```solidity
bytes32 digest = _hashTypedDataV4(keccak256(abi.encode(
    REPORT_TYPEHASH,
    keccak256(bytes(reportId)),
    keccak256(bytes(asset)),
    keccak256(bytes(action)),
    currentPriceUsd,
    confidenceBps,
    keccak256(bytes(winningMiner)),
    timestamp,
    keccak256(bytes(proofHash))
)));
address recoveredSigner = ECDSA.recover(digest, signature);
require(recoveredSigner == telegraphAttestor, "INVALID_TELEGRAPH_SIGNATURE");
```

---

## License

This project is licensed under the MIT License. Developed for the Telegraph Protocol Season II Hackathon.
