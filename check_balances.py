#!/usr/bin/env python3
"""
Balance Checker for Ethereum/EVM Addresses
Reads addresses from a file and checks their balances using an RPC endpoint
"""

import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configuration - Multiple RPC endpoints to try
RPC_ENDPOINTS = [
    "https://rpc.ankr.com/eth",
    "https://cloudflare-eth.com",
    "https://eth-mainnet.public.blastapi.io",
    "https://eth-rpc.gateway.pokt.network",
]

# You can also use Infura, Alchemy, or other services by setting these env vars:
# INFURA_KEY=your_key python check_balances.py addresses.txt
# ALCHEMY_KEY=your_key python check_balances.py addresses.txt

class BalanceChecker:
    """Check Ethereum address balances via JSON-RPC"""
    
    def __init__(self, rpc_url: Optional[str] = None):
        self.rpc_url = rpc_url or self._get_rpc_endpoint()
        self.session = self._create_session()
        self.request_id = 0
        print(f"Using RPC endpoint: {self.rpc_url}\n")
    
    def _get_rpc_endpoint(self) -> str:
        """Get RPC endpoint from env vars or use defaults"""
        # Check for Infura
        infura_key = os.getenv("INFURA_KEY")
        if infura_key:
            return f"https://mainnet.infura.io/v3/{infura_key}"
        
        # Check for Alchemy
        alchemy_key = os.getenv("ALCHEMY_KEY")
        if alchemy_key:
            return f"https://eth-mainnet.g.alchemy.com/v2/{alchemy_key}"
        
        # Check for custom endpoint
        custom_endpoint = os.getenv("RPC_ENDPOINT")
        if custom_endpoint:
            return custom_endpoint
        
        # Use first available default
        return RPC_ENDPOINTS[0]
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def _make_rpc_call(self, method: str, params: List) -> Optional[str]:
        """Make a JSON-RPC call to the endpoint"""
        self.request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self.request_id,
        }
        
        try:
            response = self.session.post(
                self.rpc_url,
                json=payload,
                timeout=15,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                print(f"RPC Error for {params[0]}: {data['error'].get('message', data['error'])}")
                return None
            
            return data.get("result")
        except requests.exceptions.Timeout:
            print(f"Timeout: Request took too long")
            return None
        except requests.exceptions.ConnectionError:
            print(f"Connection Error: Failed to connect to RPC endpoint")
            return None
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def get_balance(self, address: str) -> Optional[Dict]:
        """Get balance for a single address"""
        # Normalize address
        if not address.startswith("0x"):
            address = "0x" + address
        
        # Validate address format
        if not self._is_valid_address(address):
            return {
                "address": address,
                "error": "Invalid Ethereum address format",
                "status": "error"
            }
        
        try:
            # Get balance in Wei
            balance_wei = self._make_rpc_call("eth_getBalance", [address, "latest"])
            
            if balance_wei is None:
                return {
                    "address": address,
                    "error": "Failed to retrieve balance",
                    "status": "error"
                }
            
            # Convert to Ether
            balance_eth = int(balance_wei, 16) / 1e18
            
            return {
                "address": address,
                "balance_wei": balance_wei,
                "balance_eth": balance_eth,
                "status": "success"
            }
        except Exception as e:
            return {
                "address": address,
                "error": str(e),
                "status": "error"
            }
    
    @staticmethod
    def _is_valid_address(address: str) -> bool:
        """Validate Ethereum address format"""
        if not address.startswith("0x"):
            return False
        if len(address) != 42:
            return False
        try:
            int(address[2:], 16)
            return True
        except ValueError:
            return False
    
    def get_balances_from_file(self, file_path: str) -> List[Dict]:
        """Read addresses from file and check all balances"""
        results = []
        
        try:
            with open(file_path, 'r') as f:
                addresses = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return []
        except IOError as e:
            print(f"Error reading file: {e}")
            return []
        
        if not addresses:
            print("No addresses found in file")
            return []
        
        print(f"Found {len(addresses)} addresses. Checking balances...\n")
        
        for i, address in enumerate(addresses, 1):
            result = self.get_balance(address)
            if result:
                results.append(result)
                
                # Display progress
                if result["status"] == "success":
                    print(f"[{i}/{len(addresses)}] {result['address']}: {result['balance_eth']:.6f} ETH")
                else:
                    print(f"[{i}/{len(addresses)}] {result['address']}: ERROR - {result['error']}")
        
        return results
    
    def save_results(self, results: List[Dict], output_file: str = "balances.json"):
        """Save results to a JSON file"""
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to {output_file}")
        except IOError as e:
            print(f"Error saving results: {e}")


def print_summary(results: List[Dict]):
    """Print a summary of the balance check results"""
    if not results:
        return
    
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "error"]
    
    total_balance = sum(r.get("balance_eth", 0) for r in successful)
    
    print("\n" + "="*60)
    print("BALANCE CHECK SUMMARY")
    print("="*60)
    print(f"Total addresses checked: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"Total balance: {total_balance:.6f} ETH")
    print("="*60)
    
    # Show addresses with balance
    if successful:
        print("\nAddresses with balance:")
        for result in sorted(successful, key=lambda x: x["balance_eth"], reverse=True):
            if result["balance_eth"] > 0:
                print(f"  {result['address']}: {result['balance_eth']:.6f} ETH")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python check_balances.py <addresses_file> [output_file]")
        print("\nExample:")
        print("  python check_balances.py addresses.txt")
        print("  python check_balances.py addresses.txt results.json")
        print("\nOptional environment variables:")
        print("  INFURA_KEY=your_key python check_balances.py addresses.txt")
        print("  ALCHEMY_KEY=your_key python check_balances.py addresses.txt")
        print("  RPC_ENDPOINT=https://your-rpc.com python check_balances.py addresses.txt")
        print("\nAddress file format (one address per line):")
        print("  0x742d35Cc6634C0532925a3b844Bc152e5e7b5f5a")
        print("  0x1234567890123456789012345678901234567890")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "balances.json"
    
    # Check if file exists
    if not Path(input_file).exists():
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    
    # Create checker and run
    checker = BalanceChecker()
    results = checker.get_balances_from_file(input_file)
    
    if results:
        print_summary(results)
        checker.save_results(results, output_file)
    else:
        print("No results to save")
        sys.exit(1)


if __name__ == "__main__":
    main()
