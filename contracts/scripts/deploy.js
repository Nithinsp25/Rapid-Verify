const hre = require("hardhat");

async function main() {
  console.log("🚀 Deploying RapidVerify contract...\n");

  // Get the deployer
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with account:", deployer.address);
  
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", hre.ethers.formatEther(balance), "MATIC/ETH\n");

  // Deploy the contract
  const RapidVerify = await hre.ethers.getContractFactory("RapidVerify");
  const rapidVerify = await RapidVerify.deploy();

  await rapidVerify.waitForDeployment();
  const address = await rapidVerify.getAddress();

  console.log("✅ RapidVerify deployed to:", address);
  console.log("\n📋 Add this to your .env file:");
  console.log(`BLOCKCHAIN_CONTRACT_ADDRESS=${address}`);
  
  // Get network info
  const network = await hre.ethers.provider.getNetwork();
  console.log("\n🌐 Network:", network.name);
  console.log("Chain ID:", network.chainId.toString());
  
  // Explorer link based on network
  const explorers = {
    "137": "https://polygonscan.com",
    "80002": "https://amoy.polygonscan.com",
    "11155111": "https://sepolia.etherscan.io",
  };
  
  const explorer = explorers[network.chainId.toString()];
  if (explorer) {
    console.log(`\n🔍 View on explorer: ${explorer}/address/${address}`);
  }

  // Verify owner was set correctly
  const owner = await rapidVerify.owner();
  console.log("\n👤 Contract owner:", owner);

  console.log("\n✨ Deployment complete!");
  
  return address;
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });

