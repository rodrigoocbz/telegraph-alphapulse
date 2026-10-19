import json
from typing import Dict, Any, Tuple
from eth_account import Account
from eth_account.messages import encode_typed_data
import hashlib
import os

# Deterministic or configured private key for the Telegraph Evaluator Attestation Signer
ATTESTOR_PRIVATE_KEY = os.getenv(
    "TELEGRAPH_ATTESTOR_PRIVATE_KEY", 
    "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
)

EIP712_DOMAIN = {
    "name": "TelegraphProtocolVerifiableAlpha",
    "version": "2.0.0",
    "chainId": 1, # Ethereum Mainnet / Arbitrum
    "verifyingContract": "0x1111111254fb6c44bac0bed2854e76f90643097d"
}

EIP712_TYPES = {
    "EIP712Domain": [
        {"name": "name", "type": "string"},
        {"name": "version", "type": "string"},
        {"name": "chainId", "type": "uint256"},
        {"name": "verifyingContract", "type": "address"},
    ],
    "VerifiableAlphaReport": [
        {"name": "reportId", "type": "string"},
        {"name": "asset", "type": "string"},
        {"name": "action", "type": "string"},
        {"name": "currentPriceUsd", "type": "uint256"},
        {"name": "confidenceBps", "type": "uint256"}, # Basis points (e.g. 8700 = 87%)
        {"name": "winningMiner", "type": "string"},
        {"name": "timestamp", "type": "uint256"},
        {"name": "proofHash", "type": "string"}
    ]
}

class CryptoAttestationService:
    """
    Produces verifiable EIP-712 cryptographic signatures for Telegraph Reports,
    allowing on-chain Smart Contracts to execute trades trustlessly.
    """

    @classmethod
    def get_attestor_address(cls) -> str:
        acct = Account.from_key(ATTESTOR_PRIVATE_KEY)
        return acct.address

    @classmethod
    def sign_alpha_report(
        cls, 
        report_id: str,
        asset: str,
        action: str,
        current_price: float,
        confidence: float,
        winning_miner: str,
        timestamp_unix: int,
        proof_hash: str
    ) -> Dict[str, Any]:
        """Signs the structured report data according to EIP-712 standard."""
        price_uint = int(current_price * 100) # Cent precision
        confidence_bps = int(confidence * 10000)

        message_data = {
            "reportId": report_id,
            "asset": asset,
            "action": action,
            "currentPriceUsd": price_uint,
            "confidenceBps": confidence_bps,
            "winningMiner": winning_miner,
            "timestamp": timestamp_unix,
            "proofHash": proof_hash
        }

        structured_data = {
            "types": EIP712_TYPES,
            "primaryType": "VerifiableAlphaReport",
            "domain": EIP712_DOMAIN,
            "message": message_data
        }

        signable_message = encode_typed_data(full_message=structured_data)
        signed = Account.sign_message(signable_message, private_key=ATTESTOR_PRIVATE_KEY)

        return {
            "signer_address": cls.get_attestor_address(),
            "signature": signed.signature.hex(),
            "r": hex(signed.r),
            "s": hex(signed.s),
            "v": signed.v,
            "domain": EIP712_DOMAIN,
            "message_payload": message_data
        }

    @classmethod
    def generate_solidity_verifier_snippet(cls) -> str:
        """Generates Solidity contract code demonstrating on-chain execution."""
        return """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";

contract TelegraphAutonomousExecutor is EIP712 {
    using ECDSA for bytes32;

    address public immutable telegraphAttestor;
    bytes32 private constant REPORT_TYPEHASH = keccak256(
        "VerifiableAlphaReport(string reportId,string asset,string action,uint256 currentPriceUsd,uint256 confidenceBps,string winningMiner,uint256 timestamp,string proofHash)"
    );

    event AlphaTradeExecuted(string indexed asset, string action, uint256 price, uint256 confidence);

    constructor(address _attestor) EIP712("TelegraphProtocolVerifiableAlpha", "2.0.0") {
        telegraphAttestor = _attestor;
    }

    function executeVerifiableOrder(
        string calldata reportId,
        string calldata asset,
        string calldata action,
        uint256 currentPriceUsd,
        uint256 confidenceBps,
        string calldata winningMiner,
        uint256 timestamp,
        string calldata proofHash,
        bytes calldata signature
    ) external {
        require(block.timestamp - timestamp <= 300, "EXPIRED_TELEGRAPH_REPORT");
        require(confidenceBps >= 7500, "INSUFFICIENT_TELEGRAPH_CONFIDENCE");

        bytes32 structHash = keccak256(abi.encode(
            REPORT_TYPEHASH,
            keccak256(bytes(reportId)),
            keccak256(bytes(asset)),
            keccak256(bytes(action)),
            currentPriceUsd,
            confidenceBps,
            keccak256(bytes(winningMiner)),
            timestamp,
            keccak256(bytes(proofHash))
        ));

        bytes32 digest = _hashTypedDataV4(structHash);
        address recoveredSigner = ECDSA.recover(digest, signature);
        require(recoveredSigner == telegraphAttestor, "INVALID_TELEGRAPH_SIGNATURE");

        emit AlphaTradeExecuted(asset, action, currentPriceUsd, confidenceBps);
    }
}
"""
