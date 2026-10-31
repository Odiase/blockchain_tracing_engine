# blockchain related variables and constants
CHAINS = {
    "Ethereum Mainnet": 1,
    "Sepolia Testnet": 11155111,
    "Hoodi Testnet": 560048,
    "BNB Smart Chain Mainnet": 56,
    "BNB Smart Chain Testnet": 97,
    "Polygon Mainnet": 137,
    "Polygon Amoy Testnet": 80002,
    "Base Mainnet": 8453,
    "Base Sepolia Testnet": 84532,
    "Arbitrum One Mainnet": 42161,
    "Arbitrum Sepolia Testnet": 421614,
    "Linea Mainnet": 59144,
    "Linea Sepolia Testnet": 59141,
    "Blast Mainnet": 81457,
    "Blast Sepolia Testnet": 168587773,
    "OP Mainnet": 10,
    "OP Sepolia Testnet": 11155420,
    "Avalanche C-Chain": 43114,
    "Avalanche Fuji Testnet": 43113,
    "BitTorrent Chain Mainnet": 199,
    "BitTorrent Chain Testnet": 1029,
    "Celo Mainnet": 42220,
    "Celo Sepolia Testnet": 11142220,
    "Fraxtal Mainnet": 252,
    "Fraxtal Hoodi Testnet": 2523,
    "Gnosis": 100,
    "Mantle Mainnet": 5000,
    "Mantle Sepolia Testnet": 5003,
    "Memecore Mainnet": 4352,
    "Memecore Insectarium Testnet": 43522,
    "Moonbeam Mainnet": 1284,
    "Moonriver Mainnet": 1285,
    "Moonbase Alpha Testnet": 1287,
    "opBNB Mainnet": 204,
    "opBNB Testnet": 5611,
    "Taiko Mainnet": 167000,
    "Taiko Hoodi": 167013,
    "XDC Mainnet": 50,
    "XDC Apothem Testnet": 51,
    "ApeChain Mainnet": 33139,
    "ApeChain Curtis Testnet": 33111,
    "World Mainnet": 480,
    "World Sepolia Testnet": 4801,
    "Sonic Mainnet": 146,
    "Sonic Testnet": 14601,
    "Unichain Mainnet": 130,
    "Unichain Sepolia Testnet": 1301,
    "Abstract Mainnet": 2741,
    "Abstract Sepolia Testnet": 11124,
    "Berachain Mainnet": 80094,
    "Berachain Bepolia Testnet": 80069,
    "Monad Mainnet": 143,
    "Monad Testnet": 10143,
    "HyperEVM Mainnet": 999,
    "Katana Mainnet": 747474,
    "Katana Bokuto": 737373,
    "Sei Mainnet": 1329,
    "Sei Testnet": 1328,
    "Stable Mainnet": 988,
    "Stable Testnet": 2201,
    "Plasma Mainnet": 9745,
    "Plasma Testnet": 9746,
    "MegaETH Mainnet": 4326,
    "MegaETH Testnet": 6343
}
ETHERSCAN_API_ENDPOINT = "https://api.etherscan.io/v2/api"
ERC20_USDT_DECIMALS = 1_000_000
CHAIN = "Ethereum Mainnet"
# ERC-20 token ABI
ERC_20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {
                "name": "_spender",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "approve",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {
                "name": "_from",
                "type": "address"
            },
            {
                "name": "_to",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "transferFrom",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {
                "name": "",
                "type": "uint8"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "balance",
                "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {
                "name": "_to",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "transfer",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            },
            {
                "name": "_spender",
                "type": "address"
            }
        ],
        "name": "allowance",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "payable": True,
        "stateMutability": "payable",
        "type": "fallback"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "name": "owner",
                "type": "address"
            },
            {
                "indexed": True,
                "name": "spender",
                "type": "address"
            },
            {
                "indexed": False,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Approval",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "name": "from",
                "type": "address"
            },
            {
                "indexed": True,
                "name": "to",
                "type": "address"
            },
            {
                "indexed": False,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Transfer",
        "type": "event"
    }
]

ETHEREUM_MAINNET_ENDPOINT = "https://eth-mainnet.g.alchemy.com/v2/SEt4dUL3_hJdsYvylkkuV"
ERC20_USDT_CONTRACT_ADDRESS = "0xdac17f958d2ee523a2206206994597c13d831ec7"

# time in seconds, to use for EPOCH time conversion
FIVE_MINUTES = 300
FIFTEEN_MINUTES = 900
THIRTY_MINUTES = 1_800
HOUR = 3_600
FOUR_HOURS = 14_400
EIGHT_HOURS = 24_800
TWELVE_HOURS = 49_600
DAY = 86_400
WEEK = 604_800
THIRTY_DAYS = 2_592_000
SIXTY_DAYS = 5_184_000