# bitcoin_utils.py
import requests
from colorama import Fore, Style, init

init(autoreset=True)  # Automatically reset colors after each print

API_BASE = "https://blockchain.info"

def satoshi_to_btc(value):
    """Convert satoshi to BTC"""
    return int(value) / 100_000_000

def get_address_info(address):
    """Fetch all relevant data for a Bitcoin address"""
    url = f"{API_BASE}/rawaddr/{address}"
    r = requests.get(url)
    if r.status_code != 200:
        print(Fore.RED + f"[ERROR] Could not fetch data for {address}")
        return None
    return r.json()

def print_summary(data):
    """Print summary of the address"""
    print(Fore.CYAN + "\n===== BITCOIN ADDRESS SUMMARY =====")
    print(Fore.YELLOW + "Address        :", Fore.WHITE + data.get("address", "N/A"))
    print(Fore.YELLOW + "Hash160        :", Fore.WHITE + data.get("hash160", "N/A"))
    print(Fore.YELLOW + "Number of TX   :", Fore.WHITE + str(data.get("n_tx", 0)))
    print(Fore.YELLOW + "Unspent Outputs:", Fore.WHITE + str(data.get("n_unredeemed", 0)))
    print(Fore.YELLOW + "Total Received :", Fore.GREEN + f"{satoshi_to_btc(data.get('total_received', 0))} BTC")
    print(Fore.YELLOW + "Total Sent     :", Fore.RED + f"{satoshi_to_btc(data.get('total_sent', 0))} BTC")
    print(Fore.YELLOW + "Final Balance  :", Fore.GREEN + f"{satoshi_to_btc(data.get('final_balance', 0))} BTC")

def print_recent_transactions(data, limit=5):
    """Print recent transactions with inputs/outputs"""
    txs = data.get("txs", [])[:limit]
    if not txs:
        print(Fore.MAGENTA + "[INFO] No recent transactions found")
        return

    print(Fore.CYAN + "\n===== RECENT TRANSACTIONS =====")
    for tx in txs:
        print(Fore.MAGENTA + f"\nTX HASH: {Fore.WHITE}{tx.get('hash')}")
        print(Fore.YELLOW + "Block Height:", Fore.WHITE, tx.get("block_height", "Unconfirmed"))
        print(Fore.YELLOW + "Relayed by:", Fore.WHITE, tx.get("relayed_by", "Unknown"))
        print(Fore.YELLOW + "Size:", Fore.WHITE, tx.get("size", "Unknown"))

        print(Fore.BLUE + "Inputs:")
        for i in tx.get("inputs", []):
            prev = i.get("prev_out", {})
            addr = prev.get("addr", "Unknown")
            val = satoshi_to_btc(prev.get("value", 0))
            print(f"  {Fore.WHITE}{addr} {Fore.BLUE}-> {Fore.GREEN}{val} BTC")

        print(Fore.BLUE + "Outputs:")
        for o in tx.get("out", []):
            addr = o.get("addr", "Unknown")
            val = satoshi_to_btc(o.get("value", 0))
            print(f"  {Fore.WHITE}{addr} {Fore.BLUE}<- {Fore.GREEN}{val} BTC")

def handle_bitcoin_address(address):
    """Main function to fetch and print Bitcoin address info"""
    data = get_address_info(address)
    if not data:
        return

    # Detect address type
    addr_type = "Unknown"
    if address.startswith("1"):
        addr_type = "P2PKH (Legacy)"
    elif address.startswith("3"):
        addr_type = "P2SH"
    elif address.startswith("bc1q"):
        addr_type = "SegWit (Bech32)"
    elif address.startswith("bc1p"):
        addr_type = "Taproot"

    print(Fore.CYAN + f"\nDetected: {Fore.YELLOW}Bitcoin")
    print(Fore.CYAN + f"Address Type: {Fore.MAGENTA}{addr_type}")

    print_summary(data)
    print_recent_transactions(data)