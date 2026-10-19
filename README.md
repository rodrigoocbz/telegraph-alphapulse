# ⚡ AlphaPulse: Autonomous Verifiable Financial Intelligence Agent
> Built for **Telegraph Hackathon Season II** · Track: **Apps & Agents**

AlphaPulse is an autonomous financial risk sentinel and alpha generation agent powered by **Telegraph Protocol**. 

In high-stakes financial and Web3 environments, trusting a single LLM or unverified API endpoint leads to catastrophic losses caused by hallucinations, spoofed volume, and manipulation. AlphaPulse solves this by connecting directly to **live Binance market telemetry**, formulating market intents, submitting them to Telegraph's decentralized intelligence marketplace, and executing only when competing miners reach verified consensus scored by deterministic WASM evaluators.

---

## 🏆 Why this project fits the Telegraph Season II Track:
1. **Direct Protocol Alignment:** Showcases Telegraph's multi-miner competition (Quant, On-Chain, Technical models) and demonstrates how **Telegraph WASM Evaluators** detect and slash rogue/hallucinating miners.
2. **Real-world Commercial Mission:** Financial risk mitigation, fraud detection, and alpha scoring.
3. **Live Market Data:** Integrates real-time Binance crypto pricing and 1-hour candlestick history.
4. **Autonomous Telegram Sentinel:** Push notification bot that proactively alerts traders and funds on their phones when Telegraph flags high-risk anomalies.
5. **Interactive Streamlit Dashboard:** Professional financial UI with candlestick charts, real-time evaluator matrix, and cryptographic audit proofs.

---

## 📁 Project Structure

```
telegraph-alpha-agent/
├── core/
│   ├── models.py             # Pydantic schemas for Intents, Miner Bids, Evaluator Scores & Reports
│   ├── market_data.py        # Live Binance market data + stress scenarios (Spoofing, Flash Crash, Whales)
│   ├── telegraph_client.py   # Dual-mode Telegraph Protocol client (MOCK & LIVE Season II)
│   └── agent.py              # Autonomous Alpha agent synthesis & verification hasher
├── dashboard/
│   └── app.py                # Streamlit dark financial dashboard with interactive evaluator breakdown
├── tests/
│   └── test_agent.py         # Test suite verifying agent consensus and rogue miner filtering
├── sentinel_bot.py           # Autonomous Telegram Bot for push alerts & mobile audits
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

### 3. Launch the Interactive Web Dashboard
Run the Streamlit web app:
```bash
streamlit run dashboard/app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

### 4. Run the Autonomous Telegram Sentinel Bot
Test simulated Telegram alert in terminal:
```bash
python sentinel_bot.py --test-alert --asset BTC --scenario SPOOFING_MANIPULATION
```

To connect to your real Telegram account:
1. Message `@BotFather` on Telegram to create a bot in 30 seconds and get your token.
2. Copy `.env.example` to `.env` and fill in `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
3. Start the bot polling:
```bash
python sentinel_bot.py
```
Now send `/audit BTC` or `/simulate spoofing` from your phone!

---

## 🛡️ How Telegraph Protocol Protects Against Rogue Miners

When running the **`SPOOFING_MANIPULATION`** scenario:
1. **Unverified-Degan-Bot** attempts to trigger an aggressive long position with 99% confidence and unbacked hype.
2. **LLaMA-3.3-ChartMaster** falls for the fake volume breakout based purely on technical indicators.
3. **Telegraph Evaluators (`telegraph-eval-wasm-01`)** cross-audit the claims against live on-chain net flow and orderbook telemetry.
4. The rogue miner is penalized **-95%**, the naive technical signal is rejected, and the consensus agent triggers **`AVOID_RISK`**, protecting capital.
