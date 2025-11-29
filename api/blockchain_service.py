"""
RapidVerify Blockchain Service
Handles blockchain integration for tamper-proof verification records on Polygon/Ethereum
"""
import os
import json
import hashlib
import time
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

load_dotenv()

# Try importing web3, handle gracefully if not installed
try:
    from web3 import Web3
    from web3.middleware import ExtraDataToPOAMiddleware
    from eth_account import Account
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    print("⚠️ web3 not installed. Run: pip install web3")


@dataclass
class VerificationRecord:
    """Data structure for a verification record to be stored on blockchain"""
    claim_hash: str           # SHA-256 hash of the original claim
    verification_score: float # 0.0 to 1.0
    status: str              # verified, debunked, investigating
    verdict: str             # Human-readable verdict
    timestamp: int           # Unix timestamp
    verifier_id: str         # Identifier for the verification agent
    
    def to_bytes(self) -> bytes:
        """Convert record to bytes for blockchain storage"""
        return json.dumps(asdict(self)).encode('utf-8')
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'VerificationRecord':
        """Create record from bytes retrieved from blockchain"""
        return cls(**json.loads(data.decode('utf-8')))


class BlockchainService:
    """
    Service for interacting with Polygon/Ethereum blockchain
    Stores verification records as tamper-proof evidence
    """
    
    # Supported networks
    NETWORKS = {
        'polygon_mainnet': {
            'rpc': 'https://polygon-rpc.com',
            'chain_id': 137,
            'explorer': 'https://polygonscan.com',
            'name': 'Polygon Mainnet'
        },
        'polygon_mumbai': {
            'rpc': 'https://rpc-mumbai.maticvigil.com',
            'chain_id': 80001,
            'explorer': 'https://mumbai.polygonscan.com',
            'name': 'Polygon Mumbai Testnet'
        },
        'polygon_amoy': {
            'rpc': 'https://rpc-amoy.polygon.technology',
            'chain_id': 80002,
            'explorer': 'https://amoy.polygonscan.com',
            'name': 'Polygon Amoy Testnet'
        },
        'ethereum_sepolia': {
            'rpc': 'https://sepolia.infura.io/v3/',
            'chain_id': 11155111,
            'explorer': 'https://sepolia.etherscan.io',
            'name': 'Ethereum Sepolia Testnet'
        },
        'localhost': {
            'rpc': 'http://127.0.0.1:8545',
            'chain_id': 31337,
            'explorer': None,
            'name': 'Local Development'
        }
    }
    
    # Minimal ABI for the RapidVerify contract
    CONTRACT_ABI = [
        {
            "inputs": [
                {"name": "_claimHash", "type": "bytes32"},
                {"name": "_score", "type": "uint256"},
                {"name": "_status", "type": "string"},
                {"name": "_verdict", "type": "string"}
            ],
            "name": "recordVerification",
            "outputs": [{"name": "", "type": "bytes32"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"name": "_recordId", "type": "bytes32"}],
            "name": "getVerification",
            "outputs": [
                {"name": "claimHash", "type": "bytes32"},
                {"name": "score", "type": "uint256"},
                {"name": "status", "type": "string"},
                {"name": "verdict", "type": "string"},
                {"name": "timestamp", "type": "uint256"},
                {"name": "verifier", "type": "address"}
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"name": "_claimHash", "type": "bytes32"}],
            "name": "getVerificationByClaimHash",
            "outputs": [
                {"name": "recordId", "type": "bytes32"},
                {"name": "score", "type": "uint256"},
                {"name": "status", "type": "string"},
                {"name": "verdict", "type": "string"},
                {"name": "timestamp", "type": "uint256"},
                {"name": "verifier", "type": "address"}
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "name": "recordId", "type": "bytes32"},
                {"indexed": True, "name": "claimHash", "type": "bytes32"},
                {"indexed": False, "name": "score", "type": "uint256"},
                {"indexed": False, "name": "status", "type": "string"},
                {"indexed": False, "name": "timestamp", "type": "uint256"}
            ],
            "name": "VerificationRecorded",
            "type": "event"
        }
    ]
    
    def __init__(self):
        """Initialize the blockchain service"""
        self.enabled = False
        self.w3: Optional[Web3] = None
        self.account = None
        self.contract = None
        self.network_name = os.getenv('BLOCKCHAIN_NETWORK', 'polygon_amoy')
        self.network_config = self.NETWORKS.get(self.network_name, self.NETWORKS['polygon_amoy'])
        
        # Local storage for demo mode (when blockchain is not configured)
        # Using file-based storage for persistence across restarts
        self._local_records: Dict[str, Dict] = {}
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        self._storage_file = os.path.join(data_dir, 'blockchain_records.json')
        self._load_local_records()
        
        self._initialize()
    
    def _initialize(self):
        """Initialize Web3 connection and contract"""
        if not WEB3_AVAILABLE:
            print("⚠️ Blockchain service running in demo mode (web3 not installed)")
            return
        
        private_key = os.getenv('BLOCKCHAIN_PRIVATE_KEY')
        contract_address = os.getenv('BLOCKCHAIN_CONTRACT_ADDRESS')
        rpc_url = os.getenv('BLOCKCHAIN_RPC_URL') or self.network_config['rpc']
        
        # Handle Infura URLs
        if 'infura.io' in rpc_url and not rpc_url.endswith('/'):
            infura_key = os.getenv('INFURA_API_KEY', '')
            rpc_url = f"{rpc_url}{infura_key}"
        
        try:
            # Connect to the blockchain
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            # Add PoA middleware for Polygon
            if 'polygon' in self.network_name:
                self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
            
            if self.w3.is_connected():
                print(f"✅ Connected to {self.network_config['name']}")
                
                # Set up account if private key is provided
                if private_key:
                    if private_key.startswith('0x'):
                        private_key = private_key[2:]
                    self.account = Account.from_key(private_key)
                    print(f"✅ Wallet loaded: {self.account.address[:10]}...{self.account.address[-6:]}")
                
                # Set up contract if address is provided
                if contract_address and Web3.is_address(contract_address):
                    self.contract = self.w3.eth.contract(
                        address=Web3.to_checksum_address(contract_address),
                        abi=self.CONTRACT_ABI
                    )
                    print(f"✅ Contract loaded: {contract_address[:10]}...{contract_address[-6:]}")
                    self.enabled = True
                else:
                    print("⚠️ No contract address configured - using demo mode with hash anchoring")
            else:
                print(f"⚠️ Could not connect to {self.network_config['name']}")
                
        except Exception as e:
            print(f"⚠️ Blockchain initialization error: {e}")
    
    def is_available(self) -> bool:
        """Check if blockchain service is available"""
        return WEB3_AVAILABLE and self.w3 is not None and self.w3.is_connected()
    
    def is_fully_configured(self) -> bool:
        """Check if blockchain service is fully configured with contract"""
        return self.enabled and self.contract is not None and self.account is not None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current blockchain service status"""
        return {
            'available': self.is_available(),
            'enabled': self.enabled,
            'fully_configured': self.is_fully_configured(),
            'network': self.network_config['name'],
            'chain_id': self.network_config['chain_id'],
            'explorer': self.network_config['explorer'],
            'contract_address': os.getenv('BLOCKCHAIN_CONTRACT_ADDRESS'),
            'wallet_address': self.account.address if self.account else None,
            'mode': 'live' if self.is_fully_configured() else 'demo'
        }
    
    @staticmethod
    def hash_claim(claim_text: str) -> str:
        """Create SHA-256 hash of a claim for blockchain storage"""
        return '0x' + hashlib.sha256(claim_text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def create_record_id(claim_hash: str, timestamp: int) -> str:
        """Create unique record ID from claim hash and timestamp"""
        combined = f"{claim_hash}{timestamp}"
        return '0x' + hashlib.sha256(combined.encode('utf-8')).hexdigest()
    
    def record_verification(
        self,
        claim_text: str,
        verification_score: float,
        status: str,
        verdict: str
    ) -> Dict[str, Any]:
        """
        Record a verification result on the blockchain
        
        Args:
            claim_text: The original claim that was verified
            verification_score: Score from 0.0 to 1.0
            status: verified, debunked, or investigating
            verdict: Human-readable verdict
            
        Returns:
            Dictionary with transaction details and record info
        """
        timestamp = int(time.time())
        claim_hash = self.hash_claim(claim_text)
        record_id = self.create_record_id(claim_hash, timestamp)
        
        result = {
            'success': True,
            'mode': 'demo',
            'record_id': record_id,
            'claim_hash': claim_hash,
            'verification_score': verification_score,
            'status': status,
            'verdict': verdict,
            'timestamp': timestamp,
            'timestamp_iso': datetime.fromtimestamp(timestamp).isoformat(),
            'network': self.network_config['name'],
            'explorer_url': None,
            'transaction_hash': None,
            'block_number': None,
            'gas_used': None
        }
        
        # If fully configured, submit to blockchain
        if self.is_fully_configured():
            try:
                # Prepare transaction
                score_wei = int(verification_score * 10000)  # Store as integer (0-10000)
                claim_hash_bytes = bytes.fromhex(claim_hash[2:])
                
                tx = self.contract.functions.recordVerification(
                    claim_hash_bytes,
                    score_wei,
                    status,
                    verdict[:256]  # Limit verdict length
                ).build_transaction({
                    'from': self.account.address,
                    'nonce': self.w3.eth.get_transaction_count(self.account.address),
                    'gas': 300000,
                    'gasPrice': self.w3.eth.gas_price
                })
                
                # Sign and send transaction
                signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                
                # Wait for transaction receipt
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
                
                result.update({
                    'mode': 'live',
                    'transaction_hash': receipt['transactionHash'].hex(),
                    'block_number': receipt['blockNumber'],
                    'gas_used': receipt['gasUsed'],
                    'explorer_url': f"{self.network_config['explorer']}/tx/{receipt['transactionHash'].hex()}" if self.network_config['explorer'] else None
                })
                
                print(f"✅ Verification recorded on blockchain: {receipt['transactionHash'].hex()}")
                
            except (ConnectionError, TimeoutError) as e:
                print(f"⚠️ Blockchain transaction failed (connection): {e}")
                result['error'] = str(e)
                result['mode'] = 'demo_fallback'
            except ValueError as e:
                print(f"⚠️ Blockchain transaction failed (invalid data): {e}")
                result['error'] = str(e)
                result['mode'] = 'demo_fallback'
            except Exception as e:
                print(f"⚠️ Blockchain transaction failed: {e}")
                import traceback
                traceback.print_exc()
                result['error'] = str(e)
                result['mode'] = 'demo_fallback'
        
        # Store locally for demo mode or as backup
        self._local_records[record_id] = result
        self._save_local_records()
        
        return result
    
    def get_verification(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a verification record from the blockchain
        
        Args:
            record_id: The unique record ID
            
        Returns:
            Dictionary with verification details or None if not found
        """
        # Try blockchain first
        if self.is_fully_configured():
            try:
                record_id_bytes = bytes.fromhex(record_id[2:] if record_id.startswith('0x') else record_id)
                
                result = self.contract.functions.getVerification(record_id_bytes).call()
                
                if result[4] > 0:  # timestamp > 0 means record exists
                    return {
                        'success': True,
                        'mode': 'live',
                        'record_id': record_id,
                        'claim_hash': '0x' + result[0].hex(),
                        'verification_score': result[1] / 10000,
                        'status': result[2],
                        'verdict': result[3],
                        'timestamp': result[4],
                        'timestamp_iso': datetime.fromtimestamp(result[4]).isoformat(),
                        'verifier': result[5],
                        'network': self.network_config['name']
                    }
            except Exception as e:
                print(f"⚠️ Error fetching from blockchain: {e}")
        
        # Fall back to local records
        if record_id in self._local_records:
            record = self._local_records[record_id].copy()
            record['source'] = 'local_cache'
            return record
        
        return None
    
    def verify_record(self, record_id: str, claim_text: str) -> Dict[str, Any]:
        """
        Verify that a record exists and matches the claim
        
        Args:
            record_id: The record ID to verify
            claim_text: The original claim text to match
            
        Returns:
            Dictionary with verification status
        """
        expected_claim_hash = self.hash_claim(claim_text)
        record = self.get_verification(record_id)
        
        if not record:
            return {
                'verified': False,
                'reason': 'Record not found',
                'record_id': record_id
            }
        
        if record.get('claim_hash') != expected_claim_hash:
            return {
                'verified': False,
                'reason': 'Claim hash mismatch - content may have been modified',
                'record_id': record_id,
                'expected_hash': expected_claim_hash,
                'actual_hash': record.get('claim_hash')
            }
        
        return {
            'verified': True,
            'record': record,
            'message': 'Record verified - content matches blockchain record'
        }
    
    def get_recent_records(self, limit: int = 10) -> list:
        """Get recent verification records from local cache"""
        records = list(self._local_records.values())
        records.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        return records[:limit]
    
    def anchor_hash(self, data: str) -> Dict[str, Any]:
        """
        Simple hash anchoring - creates a verifiable hash without full contract interaction
        Useful for demo mode or when contract is not deployed
        
        Args:
            data: Data to anchor
            
        Returns:
            Dictionary with hash details
        """
        timestamp = int(time.time())
        data_hash = self.hash_claim(data)
        anchor_id = self.create_record_id(data_hash, timestamp)
        
        result = {
            'anchor_id': anchor_id,
            'data_hash': data_hash,
            'timestamp': timestamp,
            'timestamp_iso': datetime.fromtimestamp(timestamp).isoformat(),
            'network': self.network_config['name'],
            'mode': 'hash_anchor'
        }
        
        # If we have a connection but no contract, we can still get block info
        if self.is_available():
            try:
                latest_block = self.w3.eth.get_block('latest')
                result.update({
                    'reference_block': latest_block['number'],
                    'block_hash': latest_block['hash'].hex(),
                    'block_timestamp': latest_block['timestamp']
                })
            except Exception as e:
                print(f"⚠️ Could not get block info: {e}")
        
        self._local_records[anchor_id] = result
        self._save_local_records()
        return result
    
    def _load_local_records(self):
        """Load local records from file"""
        if os.path.exists(self._storage_file):
            try:
                with open(self._storage_file, 'r') as f:
                    self._local_records = json.load(f)
                print(f"✅ Loaded {len(self._local_records)} local blockchain records")
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ Failed to load local records: {e}")
                self._local_records = {}
        else:
            self._local_records = {}
    
    def _save_local_records(self):
        """Save local records to file"""
        try:
            with open(self._storage_file, 'w') as f:
                json.dump(self._local_records, f, indent=2)
        except IOError as e:
            print(f"⚠️ Failed to save local records: {e}")


# Global instance
blockchain_service = BlockchainService()


# Convenience functions
def record_verification(claim_text: str, score: float, status: str, verdict: str) -> Dict[str, Any]:
    """Record a verification on the blockchain"""
    return blockchain_service.record_verification(claim_text, score, status, verdict)


def get_verification(record_id: str) -> Optional[Dict[str, Any]]:
    """Get a verification record"""
    return blockchain_service.get_verification(record_id)


def verify_record(record_id: str, claim_text: str) -> Dict[str, Any]:
    """Verify a record matches the claim"""
    return blockchain_service.verify_record(record_id, claim_text)


def get_blockchain_status() -> Dict[str, Any]:
    """Get blockchain service status"""
    return blockchain_service.get_status()

