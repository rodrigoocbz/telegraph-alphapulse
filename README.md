# ⚡ AlphaPulse: Autonomous Verifiable Financial Intelligence Agent
> Built for **Telegraph Hackathon Season II** · Track: **Apps & Agents**

AlphaPulse is an autonomous financial risk sentinel and alpha generation agent powered by **Telegraph Protocol**. 

In high-stakes financial and Web3 environments, trusting a single LLM or unverified API endpoint leads to catastrophic losses caused by hallucinations, spoofed volume, and manipulation. AlphaPulse solves this by formulating market intents, submitting them to Telegraph's decentralized intelligence marketplace, and executing only when competing miners reach verified consensus scored by deterministic WASM evaluators.

---

## 🏆 Why this project fits the Telegraph Season II Track:
1. **Direct Protocol Alignment:** Showcases Telegraph's multi-miner competition (Quant, On-Chain, Technical models) and demonstrates how **Telegraph WASM Evaluators** detect and slash rogue/hallucinating miners.
2. **Real-world Commercial Mission:** Financial risk mitigation, fraud detection, and alpha scoring.
3. **Dual Mode (Pre-Season & Live):** Includes a high-fidelity simulation engine for pre-hackathon testing, with zero-friction migration to Telegraph's live Season II API/SDK on November 1st.
4. **Interactive Streamlit Dashboard:** Professional financial UI with candlestick charts, real-time evaluator matrix, and cryptographic audit proofs.

---

## 📁 Project Structure

```
telegraph-alpha-agent/
├── core/
│   ├── models.py             # Pydantic schemas for Intents, Miner Bids, Evaluator Scores & Reports
│   ├── market_data.py        # Multi-asset telemetry and stress scenario generator (Spoofing, Flash Crash, Whales)
│   ├── telegraph_client.py   # Dual-mode Telegraph Protocol client (MOCK & LIVE Season II)
│   └── agent.py              # Autonomous Alpha agent synthesis & verification hasher
├── dashboard/
│   └── app.py                # Streamlit dark financial dashboard with interactive evaluator breakdown
├── tests/
│   └── test_agent.py         # Test suite verifying agent consensus and rogue miner filtering
├── main.py                   # Terminal CLI runner with colored matrix output
├── requirements.txt          # Python dependencies
├── .env.example              # Configuration variables
└── README.md
```

---

## 🚀 Quick Start

### 1. Activate Environment
```bash
cd /Users/alumnoad/.gemini/antigravity/scratch/telegraph-alpha-agent
source .venv/bin/activate
```

### 2. Run CLI Market Audit
Test the agent directly in your terminal under a market spoofing attack:
```bash
python main.py --asset BTC --scenario SPOOFING_MANIPULATION
```

You can test other market conditions:
* `NORMAL`: Steady range-bound market.
* `WHALE_ACCUMULATION`: Strong on-chain outflows and institutional spot buying.
* `FLASH_CRASH_RISK`: Orderbook collapse with cascading liquidation risks.
* `SPOOFING_MANIPULATION`: Fake bid walls and hype bot shills (watch Telegraph Evaluators slash them!).

### 3. Launch the Interactive Dashboard
Run the Streamlit web app:
```bash
streamlit run dashboard/app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🛡️ How Telegraph Protocol Protects Against Rogue Miners

When running the **`SPOOFING_MANIPULATION`** scenario:
1. **Unverified-Degan-Bot** attempts to trigger an aggressive long position with 99% confidence and unbacked hype.
2. **LLaMA-3.3-ChartMaster** falls for the fake volume breakout based purely on technical indicators.
3. **Telegraph Evaluators (`telegraph-eval-wasm-01`)** cross-audit the claims against live on-chain net flow and orderbook telemetry.
4. The rogue miner is penalized **-95%**, the naive technical signal is rejected, and the consensus agent triggers **`AVOID_RISK`**, protecting capital.
