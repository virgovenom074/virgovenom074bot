# Ethereum Balance Checker

Check balances for multiple Ethereum/EVM addresses from a file.

## Installation

1. Clone or download the script
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Create a file with addresses (one per line):

```bash
# addresses.txt
0x742d35Cc6634C0532925a3b844Bc152e5e7b5f5a
0x1234567890123456789012345678901234567890
```

Then run:

```bash
python check_balances.py addresses.txt
```

Output will be saved to `balances.json` by default.

### Specify Output File

```bash
python check_balances.py addresses.txt results.json
```

### Using a Custom RPC Endpoint

```bash
# Use environment variable
RPC_ENDPOINT=https://your-rpc-url.com python check_balances.py addresses.txt
```

### Using Infura (Recommended)

1. Get a free API key from [Infura](https://infura.io)
2. Run:

```bash
INFURA_KEY=your_api_key python check_balances.py addresses.txt
```

### Using Alchemy (Recommended)

1. Get a free API key from [Alchemy](https://www.alchemy.com/)
2. Run:

```bash
ALCHEMY_KEY=your_api_key python check_balances.py addresses.txt
```

## Output

The script creates a JSON file with results:

```json
[
  {
    "address": "0x742d35Cc6634C0532925a3b844Bc152e5e7b5f5a",
    "balance_wei": "0x1a4d5f0a9e2c8f1b",
    "balance_eth": 0.118504,
    "status": "success"
  },
  {
    "address": "0x1234567890123456789012345678901234567890",
    "error": "Failed to retrieve balance",
    "status": "error"
  }
]
```

Console output includes:
- Progress for each address
- Summary with total addresses, successful checks, failed checks
- Total ETH across all addresses

## RPC Endpoints Used (in order)

1. Ankr - `https://rpc.ankr.com/eth`
2. Cloudflare - `https://cloudflare-eth.com`
3. Blast API - `https://eth-mainnet.public.blastapi.io`
4. Pokt Network - `https://eth-rpc.gateway.pokt.network`

If one fails, the script automatically tries the next.

## Features

✅ Batch check multiple addresses  
✅ Handles rate limiting with automatic retries  
✅ Validates address format  
✅ Saves results to JSON  
✅ Displays progress in real-time  
✅ Shows summary statistics  
✅ Works with custom RPC endpoints  
✅ Supports Infura and Alchemy APIs  

## Troubleshooting

**"Request failed: 403 Forbidden"**
- The RPC endpoint is blocking your requests. Try using Infura or Alchemy.

**"Request failed: 429 Too Many Requests"**
- Rate limiting. Use Infura or Alchemy with an API key for higher limits.

**"Connection Error"**
- Check your internet connection or RPC endpoint URL.

**"Invalid Ethereum address format"**
- Ensure addresses are valid Ethereum addresses (42 characters, starting with 0x).

## Supported Chains

This script works with any EVM-compatible blockchain by changing the RPC endpoint:

- Ethereum Mainnet (default)
- Polygon: `https://polygon-rpc.com`
- Arbitrum: `https://arb1.arbitrum.io/rpc`
- Optimism: `https://mainnet.optimism.io`
- Base: `https://mainnet.base.org`

Example:
```bash
RPC_ENDPOINT=https://polygon-rpc.com python check_balances.py addresses.txt
```

## License

MIT License - See repository for details
