"""
RapidVerify Smart Contract Deployment Script
Deploys the verification contract to Polygon Amoy (or any EVM chain)
"""
import os
import json
import time
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from eth_account import Account
from dotenv import load_dotenv

load_dotenv()

# Configuration
RPC_URL = os.getenv('BLOCKCHAIN_RPC_URL', 'https://rpc-amoy.polygon.technology')
PRIVATE_KEY = os.getenv('BLOCKCHAIN_PRIVATE_KEY')

# Minimal Contract Source (Solidity)
# We compile this on the fly or use pre-compiled bytecode
CONTRACT_SOURCE = '''
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract RapidVerify {
    struct Verification {
        bytes32 claimHash;
        uint256 score;
        string status;
        string verdict;
        uint256 timestamp;
        address verifier;
    }

    mapping(bytes32 => Verification) public verifications;
    mapping(bytes32 => bytes32) public claimToRecordId;

    event VerificationRecorded(
        bytes32 indexed recordId,
        bytes32 indexed claimHash,
        uint256 score,
        string status,
        uint256 timestamp
    );

    function recordVerification(
        bytes32 _claimHash,
        uint256 _score,
        string memory _status,
        string memory _verdict
    ) public returns (bytes32) {
        uint256 timestamp = block.timestamp;
        
        // Create unique record ID based on claim + timestamp
        bytes32 recordId = keccak256(abi.encodePacked(_claimHash, timestamp, msg.sender));
        
        verifications[recordId] = Verification({
            claimHash: _claimHash,
            score: _score,
            status: _status,
            verdict: _verdict,
            timestamp: timestamp,
            verifier: msg.sender
        });
        
        claimToRecordId[_claimHash] = recordId;
        
        emit VerificationRecorded(recordId, _claimHash, _score, _status, timestamp);
        
        return recordId;
    }

    function getVerification(bytes32 _recordId) public view returns (
        bytes32 claimHash,
        uint256 score,
        string memory status,
        string memory verdict,
        uint256 timestamp,
        address verifier
    ) {
        Verification memory v = verifications[_recordId];
        return (v.claimHash, v.score, v.status, v.verdict, v.timestamp, v.verifier);
    }

    function getVerificationByClaimHash(bytes32 _claimHash) public view returns (
        bytes32 recordId,
        uint256 score,
        string memory status,
        string memory verdict,
        uint256 timestamp,
        address verifier
    ) {
        recordId = claimToRecordId[_claimHash];
        Verification memory v = verifications[recordId];
        return (recordId, v.score, v.status, v.verdict, v.timestamp, v.verifier);
    }
}
'''

def deploy():
    print("🚀 Starting RapidVerify Contract Deployment...")
    
    if not PRIVATE_KEY:
        print("❌ Error: BLOCKCHAIN_PRIVATE_KEY not found in .env")
        return

    # Connect to Web3
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    
    if not w3.is_connected():
        print(f"❌ Error: Could not connect to RPC {RPC_URL}")
        return

    account = Account.from_key(PRIVATE_KEY)
    print(f"✅ Connected to network. Deploying from: {account.address}")
    
    balance = w3.eth.get_balance(account.address)
    print(f"💰 Balance: {w3.from_wei(balance, 'ether')} MATIC/ETH")
    
    if balance == 0:
        print("❌ Error: Insufficient funds for deployment")
        return

    # Compile Contract (using py-solc-x)
    try:
        from solcx import compile_source, install_solc
        print("🔨 Compiling contract...")
        install_solc('0.8.0')
        compiled_sol = compile_source(CONTRACT_SOURCE, output_values=['abi', 'bin'])
        contract_id, contract_interface = next(iter(compiled_sol.items()))
        
        bytecode = contract_interface['bin']
        abi = contract_interface['abi']
        
        # Deploy
        print("Tx: Creating contract...")
        RapidVerify = w3.eth.contract(abi=abi, bytecode=bytecode)
        
        # Build transaction
        construct_txn = RapidVerify.constructor().build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price
        })
        
        # Sign
        signed = w3.eth.account.sign_transaction(construct_txn, private_key=PRIVATE_KEY)
        
        # Send
        print("Tx: Broadcasting...")
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"⏳ Waiting for confirmation... (Tx: {tx_hash.hex()})")
        
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        contract_address = tx_receipt.contractAddress
        print(f"\n🎉 Contract Deployed Successfully!")
        print(f"📍 Address: {contract_address}")
        print(f"\n👉 Add this to your .env file:")
        print(f"BLOCKCHAIN_CONTRACT_ADDRESS={contract_address}")
        
    except ImportError:
        print("❌ Error: py-solc-x not installed. Run: pip install py-solc-x")
    except Exception as e:
        print(f"❌ Deployment failed: {e}")

if __name__ == "__main__":
    deploy()
