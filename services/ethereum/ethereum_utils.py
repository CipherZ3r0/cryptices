import requests
from colorama import Fore, Style, init
from services.AI.account_summarization import ai_summarize

init(autoreset=True)

# --------------------------------
# Free Public RPC Nodes
# --------------------------------

RPC_URLS = [
    "https://cloudflare-eth.com",
    "https://rpc.ankr.com/eth",
    "https://ethereum.publicnode.com"
]


# --------------------------------
# Wei → ETH
# --------------------------------

def wei_to_eth(value):
    return int(value) / 1_000_000_000_000_000_000


# --------------------------------
# Generic RPC caller with fallback
# --------------------------------

def rpc_call(payload):

    for rpc in RPC_URLS:

        try:
            r = requests.post(rpc, json=payload, timeout=10)

            if r.status_code != 200:
                continue

            data = r.json()

            if "result" in data:
                return data["result"]

        except Exception:
            continue

    print(Fore.RED + "[ERROR] All Ethereum RPC nodes failed")
    return None


# --------------------------------
# Get wallet balance
# --------------------------------

def get_balance(address):

    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [address, "latest"],
        "id": 1
    }

    result = rpc_call(payload)

    if result is None:
        return None

    wei = int(result, 16)

    return wei


# --------------------------------
# Get transaction by hash
# (useful later for tracing)
# --------------------------------

def get_transaction(tx_hash):

    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionByHash",
        "params": [tx_hash],
        "id": 1
    }

    result = rpc_call(payload)

    return result


# --------------------------------
# Print summary
# --------------------------------

def print_summary(address, wei_balance):

    print(Fore.CYAN + "\n===== ETHEREUM ADDRESS SUMMARY =====")

    eth = wei_to_eth(wei_balance)

    print(Fore.YELLOW + "Address        :", Fore.WHITE + address)
    print(Fore.YELLOW + "Balance        :", Fore.GREEN + f"{eth} ETH")
    print(Fore.YELLOW + "Wei            :", Fore.WHITE + str(wei_balance))


# --------------------------------
# Handler
# --------------------------------

def handle_ethereum_address(address):

    print(Fore.CYAN + f"\nDetected: {Fore.YELLOW}Ethereum")
    print(Fore.CYAN + f"Address Type: {Fore.MAGENTA}EVM Address")

    balance = get_balance(address)

    if balance is None:
        print(Fore.RED + "[ERROR] Could not fetch balance")
        return

    print_summary(address, balance)

    data = {
        "address": address,
        "balance_wei": balance,
        "balance_eth": wei_to_eth(balance)
    }

    ai_summarize(data, chain="Ethereum")