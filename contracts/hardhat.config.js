require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config({ path: "../.env" });

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.19",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  networks: {
    hardhat: {
      chainId: 31337,
    },
    localhost: {
      url: "http://127.0.0.1:8545",
      chainId: 31337,
    },
    polygon_amoy: {
      url: process.env.BLOCKCHAIN_RPC_URL || "https://rpc-amoy.polygon.technology",
      chainId: 80002,
      accounts: process.env.BLOCKCHAIN_PRIVATE_KEY 
        ? [process.env.BLOCKCHAIN_PRIVATE_KEY]
        : [],
    },
    polygon_mainnet: {
      url: process.env.BLOCKCHAIN_RPC_URL || "https://polygon-rpc.com",
      chainId: 137,
      accounts: process.env.BLOCKCHAIN_PRIVATE_KEY 
        ? [process.env.BLOCKCHAIN_PRIVATE_KEY]
        : [],
    },
    sepolia: {
      url: `https://sepolia.infura.io/v3/${process.env.INFURA_API_KEY || ""}`,
      chainId: 11155111,
      accounts: process.env.BLOCKCHAIN_PRIVATE_KEY 
        ? [process.env.BLOCKCHAIN_PRIVATE_KEY]
        : [],
    },
  },
  etherscan: {
    apiKey: {
      polygonAmoy: process.env.POLYGONSCAN_API_KEY || "",
      polygon: process.env.POLYGONSCAN_API_KEY || "",
      sepolia: process.env.ETHERSCAN_API_KEY || "",
    },
    customChains: [
      {
        network: "polygonAmoy",
        chainId: 80002,
        urls: {
          apiURL: "https://api-amoy.polygonscan.com/api",
          browserURL: "https://amoy.polygonscan.com",
        },
      },
    ],
  },
  paths: {
    sources: "./",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts",
  },
};

