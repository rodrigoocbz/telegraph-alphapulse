import sqlite3
import json
import os
from typing import Dict, Any, List
from datetime import datetime

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "alphapulse_vault.db"))

class AlphaVaultDB:
    """Thread-safe SQLite persistent telemetry store for Telegraph AlphaPulse."""

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def init_db(cls):
        """Initializes tables for audits, miner performances, and cryptographic attestations."""
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intent_id TEXT UNIQUE,
                asset TEXT,
                scenario TEXT,
                price REAL,
                action TEXT,
                confidence REAL,
                winning_miner TEXT,
                verifiable_signature TEXT,
                signer_address TEXT,
                execution_narrative TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS miner_evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intent_id TEXT,
                miner_name TEXT,
                model_family TEXT,
                signal TEXT,
                latency_ms INTEGER,
                evaluator_score REAL,
                passed_benchmark BOOLEAN,
                notes TEXT,
                FOREIGN KEY (intent_id) REFERENCES audit_logs (intent_id)
            )
            """)
            conn.commit()

    @classmethod
    def log_swarm_consensus(cls, consensus_result, scenario: str, price: float):
        cls.init_db()
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT OR REPLACE INTO audit_logs 
            (intent_id, asset, scenario, price, action, confidence, winning_miner, verifiable_signature, signer_address, execution_narrative)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                consensus_result.intent_id,
                consensus_result.asset.value,
                scenario,
                price,
                consensus_result.final_arbitrated_action.value,
                consensus_result.final_confidence,
                consensus_result.telegraph_winning_miner,
                consensus_result.verifiable_hash,
                consensus_result.eip712_attestation.get("signer_address"),
                consensus_result.execution_narrative
            ))
            conn.commit()

    @classmethod
    def get_recent_audits(cls, limit: int = 15) -> List[Dict[str, Any]]:
        cls.init_db()
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    @classmethod
    def get_miner_leaderboard(cls) -> List[Dict[str, Any]]:
        """Returns leaderboard statistics aggregated across all audits."""
        cls.init_db()
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT 
                winning_miner,
                COUNT(*) as win_count,
                ROUND(AVG(confidence) * 100, 1) as avg_confidence_pct
            FROM audit_logs
            GROUP BY winning_miner
            ORDER BY win_count DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
