// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title RapidVerify
 * @notice Smart contract for storing tamper-proof verification records
 * @dev Stores verification results for misinformation detection on Polygon
 */
contract RapidVerify {
    
    // ============================================
    // STRUCTS
    // ============================================
    
    struct VerificationRecord {
        bytes32 claimHash;      // SHA-256 hash of the original claim
        uint256 score;          // Verification score (0-10000, representing 0.00-100.00%)
        string status;          // "verified", "debunked", or "investigating"
        string verdict;         // Human-readable verdict
        uint256 timestamp;      // Unix timestamp of verification
        address verifier;       // Address of the verifier
        bool exists;            // Record existence flag
    }
    
    // ============================================
    // STATE VARIABLES
    // ============================================
    
    /// @notice Contract owner
    address public owner;
    
    /// @notice Mapping of record ID to verification record
    mapping(bytes32 => VerificationRecord) public verifications;
    
    /// @notice Mapping of claim hash to record ID (for lookup by claim)
    mapping(bytes32 => bytes32) public claimToRecord;
    
    /// @notice List of all record IDs
    bytes32[] public recordIds;
    
    /// @notice Mapping of authorized verifiers
    mapping(address => bool) public authorizedVerifiers;
    
    /// @notice Total number of verifications
    uint256 public totalVerifications;
    
    /// @notice Count by status
    mapping(string => uint256) public statusCounts;
    
    // ============================================
    // EVENTS
    // ============================================
    
    event VerificationRecorded(
        bytes32 indexed recordId,
        bytes32 indexed claimHash,
        uint256 score,
        string status,
        uint256 timestamp
    );
    
    event VerifierAuthorized(address indexed verifier);
    event VerifierRevoked(address indexed verifier);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    
    // ============================================
    // MODIFIERS
    // ============================================
    
    modifier onlyOwner() {
        require(msg.sender == owner, "RapidVerify: caller is not owner");
        _;
    }
    
    modifier onlyAuthorized() {
        require(
            msg.sender == owner || authorizedVerifiers[msg.sender],
            "RapidVerify: caller is not authorized"
        );
        _;
    }
    
    // ============================================
    // CONSTRUCTOR
    // ============================================
    
    constructor() {
        owner = msg.sender;
        authorizedVerifiers[msg.sender] = true;
    }
    
    // ============================================
    // MAIN FUNCTIONS
    // ============================================
    
    /**
     * @notice Record a new verification result
     * @param _claimHash SHA-256 hash of the claim being verified
     * @param _score Verification score (0-10000)
     * @param _status Status string ("verified", "debunked", "investigating")
     * @param _verdict Human-readable verdict
     * @return recordId The unique ID for this verification record
     */
    function recordVerification(
        bytes32 _claimHash,
        uint256 _score,
        string calldata _status,
        string calldata _verdict
    ) external onlyAuthorized returns (bytes32) {
        require(_score <= 10000, "RapidVerify: score must be <= 10000");
        require(bytes(_status).length > 0, "RapidVerify: status required");
        
        // Generate unique record ID
        bytes32 recordId = keccak256(
            abi.encodePacked(_claimHash, block.timestamp, msg.sender, totalVerifications)
        );
        
        // Ensure record doesn't already exist
        require(!verifications[recordId].exists, "RapidVerify: record already exists");
        
        // Store the verification
        verifications[recordId] = VerificationRecord({
            claimHash: _claimHash,
            score: _score,
            status: _status,
            verdict: _verdict,
            timestamp: block.timestamp,
            verifier: msg.sender,
            exists: true
        });
        
        // Update mappings and counters
        claimToRecord[_claimHash] = recordId;
        recordIds.push(recordId);
        totalVerifications++;
        statusCounts[_status]++;
        
        emit VerificationRecorded(recordId, _claimHash, _score, _status, block.timestamp);
        
        return recordId;
    }
    
    /**
     * @notice Get a verification record by ID
     * @param _recordId The unique record ID
     * @return claimHash The claim hash
     * @return score The verification score
     * @return status The status string
     * @return verdict The verdict string
     * @return timestamp The verification timestamp
     * @return verifier The verifier address
     */
    function getVerification(bytes32 _recordId) external view returns (
        bytes32 claimHash,
        uint256 score,
        string memory status,
        string memory verdict,
        uint256 timestamp,
        address verifier
    ) {
        VerificationRecord storage record = verifications[_recordId];
        require(record.exists, "RapidVerify: record not found");
        
        return (
            record.claimHash,
            record.score,
            record.status,
            record.verdict,
            record.timestamp,
            record.verifier
        );
    }
    
    /**
     * @notice Get verification by claim hash
     * @param _claimHash The claim hash to look up
     */
    function getVerificationByClaimHash(bytes32 _claimHash) external view returns (
        bytes32 recordId,
        uint256 score,
        string memory status,
        string memory verdict,
        uint256 timestamp,
        address verifier
    ) {
        bytes32 _recordId = claimToRecord[_claimHash];
        require(_recordId != bytes32(0), "RapidVerify: no record for claim");
        
        VerificationRecord storage record = verifications[_recordId];
        
        return (
            _recordId,
            record.score,
            record.status,
            record.verdict,
            record.timestamp,
            record.verifier
        );
    }
    
    /**
     * @notice Check if a record exists
     * @param _recordId The record ID to check
     */
    function recordExists(bytes32 _recordId) external view returns (bool) {
        return verifications[_recordId].exists;
    }
    
    /**
     * @notice Check if a claim has been verified
     * @param _claimHash The claim hash to check
     */
    function claimVerified(bytes32 _claimHash) external view returns (bool) {
        return claimToRecord[_claimHash] != bytes32(0);
    }
    
    /**
     * @notice Get total record count
     */
    function getRecordCount() external view returns (uint256) {
        return recordIds.length;
    }
    
    /**
     * @notice Get records with pagination
     * @param _offset Starting index
     * @param _limit Maximum number of records to return
     */
    function getRecords(uint256 _offset, uint256 _limit) external view returns (bytes32[] memory) {
        uint256 length = recordIds.length;
        
        if (_offset >= length) {
            return new bytes32[](0);
        }
        
        uint256 end = _offset + _limit;
        if (end > length) {
            end = length;
        }
        
        bytes32[] memory result = new bytes32[](end - _offset);
        for (uint256 i = _offset; i < end; i++) {
            result[i - _offset] = recordIds[i];
        }
        
        return result;
    }
    
    /**
     * @notice Get latest records
     * @param _count Number of recent records to return
     */
    function getLatestRecords(uint256 _count) external view returns (bytes32[] memory) {
        uint256 length = recordIds.length;
        
        if (_count > length) {
            _count = length;
        }
        
        bytes32[] memory result = new bytes32[](_count);
        for (uint256 i = 0; i < _count; i++) {
            result[i] = recordIds[length - 1 - i];
        }
        
        return result;
    }
    
    // ============================================
    // ADMIN FUNCTIONS
    // ============================================
    
    /**
     * @notice Authorize a new verifier
     * @param _verifier Address to authorize
     */
    function authorizeVerifier(address _verifier) external onlyOwner {
        require(_verifier != address(0), "RapidVerify: zero address");
        authorizedVerifiers[_verifier] = true;
        emit VerifierAuthorized(_verifier);
    }
    
    /**
     * @notice Revoke verifier authorization
     * @param _verifier Address to revoke
     */
    function revokeVerifier(address _verifier) external onlyOwner {
        require(_verifier != owner, "RapidVerify: cannot revoke owner");
        authorizedVerifiers[_verifier] = false;
        emit VerifierRevoked(_verifier);
    }
    
    /**
     * @notice Transfer ownership
     * @param _newOwner New owner address
     */
    function transferOwnership(address _newOwner) external onlyOwner {
        require(_newOwner != address(0), "RapidVerify: zero address");
        
        address oldOwner = owner;
        owner = _newOwner;
        authorizedVerifiers[_newOwner] = true;
        
        emit OwnershipTransferred(oldOwner, _newOwner);
    }
    
    // ============================================
    // STATISTICS
    // ============================================
    
    /**
     * @notice Get verification statistics
     */
    function getStatistics() external view returns (
        uint256 total,
        uint256 verified,
        uint256 debunked,
        uint256 investigating
    ) {
        return (
            totalVerifications,
            statusCounts["verified"],
            statusCounts["debunked"],
            statusCounts["investigating"]
        );
    }
}


