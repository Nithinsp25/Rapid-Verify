# RapidVerify Smart Contracts

Smart contracts for blockchain-based verification records on Polygon/Ethereum.

## Overview

The `RapidVerify` smart contract stores verification records as tamper-proof evidence on the blockchain. Each record contains:

- **Claim Hash**: SHA-256 hash of the original content
- **Score**: Verification score (0-100%)
- **Status**: verified, debunked, or investigating
- **Verdict**: Human-readable verdict
- **Timestamp**: When the verification was recorded
- **Verifier**: Address of the verifier

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn
- A wallet with testnet MATIC (for Polygon Amoy)

### Installation

```bash
cd contracts
npm install
```

### Configuration

Create a `.env` file in the project root (one level up):

```env
BLOCKCHAIN_NETWORK=polygon_amoy
BLOCKCHAIN_PRIVATE_KEY=your_private_key_without_0x
POLYGONSCAN_API_KEY=your_polygonscan_api_key
```

### Get Test MATIC

For Polygon Amoy testnet, get free test MATIC from:
- https://faucet.polygon.technology/

## Deployment

### Local Testing

```bash
# Start local node
npm run node

# In another terminal, deploy
npm run deploy:local
```

### Polygon Amoy Testnet

```bash
npm run deploy:amoy
```

### Polygon Mainnet

```bash
npm run deploy:polygon
```

After deployment, copy the contract address to your `.env`:

```env
BLOCKCHAIN_CONTRACT_ADDRESS=0x...
```

## Contract Functions

### recordVerification

Records a new verification result.

```solidity
function recordVerification(
    bytes32 _claimHash,
    uint256 _score,      // 0-10000 (0.00% - 100.00%)
    string _status,      // "verified", "debunked", "investigating"
    string _verdict
) returns (bytes32 recordId)
```

### getVerification

Retrieves a verification record by ID.

```solidity
function getVerification(bytes32 _recordId) returns (
    bytes32 claimHash,
    uint256 score,
    string status,
    string verdict,
    uint256 timestamp,
    address verifier
)
```

### getVerificationByClaimHash

Look up verification by the claim's hash.

```solidity
function getVerificationByClaimHash(bytes32 _claimHash) returns (...)
```

### getStatistics

Get verification statistics.

```solidity
function getStatistics() returns (
    uint256 total,
    uint256 verified,
    uint256 debunked,
    uint256 investigating
)
```

## Events

```solidity
event VerificationRecorded(
    bytes32 indexed recordId,
    bytes32 indexed claimHash,
    uint256 score,
    string status,
    uint256 timestamp
);
```

## Security

- Only authorized verifiers can record verifications
- Owner can add/remove verifiers
- Records are immutable once created

## Networks

| Network | Chain ID | RPC URL |
|---------|----------|---------|
| Polygon Mainnet | 137 | https://polygon-rpc.com |
| Polygon Amoy | 80002 | https://rpc-amoy.polygon.technology |
| Ethereum Sepolia | 11155111 | https://sepolia.infura.io/v3/... |

## License

MIT


