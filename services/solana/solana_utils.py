import requests
from colorama import Fore, Style, init
from services.AI.account_summarization import ai_summarize

init(autoreset=True)

RPC_URL = "https://api.mainnet-beta.solana.com"


# --------------------------------
# Lamports → SOL
# --------------------------------

def lamports_to_sol(value):
    return int(value) / 1_000_000_000


# --------------------------------
# RPC helper
# --------------------------------

def rpc_call(method, params):

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }

    r = requests.post(RPC_URL, json=payload)

    if r.status_code != 200:
        return None

    data = r.json()

    if "result" not in data:
        return None

    return data["result"]


# --------------------------------
# Get wallet balance
# --------------------------------

def get_balance(address):

    result = rpc_call("getBalance", [address])

    if not result:
        return None

    return result["value"]


# --------------------------------
# Get transaction signatures
# --------------------------------

def get_signatures(address, limit=5):

    result = rpc_call(
        "getSignaturesForAddress",
        [address, {"limit": limit}]
    )

    if not result:
        return []

    return result


# --------------------------------
# Get full transaction
# --------------------------------

def get_transaction(signature):

    result = rpc_call(
        "getTransaction",
        [
            signature,
            {
                "encoding": "json",
                "maxSupportedTransactionVersion": 0
            }
        ]
    )

    return result


# --------------------------------
# Extract transfers
# --------------------------------

def extract_transfers(tx):

    transfers = []

    if not tx:
        return transfers

    message = tx["transaction"]["message"]
    meta = tx["meta"]

    accounts = message["accountKeys"]

    pre_balances = meta["preBalances"]
    post_balances = meta["postBalances"]

    for i in range(len(accounts)):

        diff = post_balances[i] - pre_balances[i]

        if diff == 0:
            continue

        transfers.append({
            "wallet": accounts[i],
            "change": lamports_to_sol(diff)
        })

    return transfers


# --------------------------------
# Print summary
# --------------------------------

def print_summary(address, lamports):

    print(Fore.CYAN + "\n===== SOLANA ADDRESS SUMMARY =====")

    sol = lamports_to_sol(lamports)

    print(Fore.YELLOW + "Address        :", Fore.WHITE + address)
    print(Fore.YELLOW + "Balance        :", Fore.GREEN + f"{sol} SOL")
    print(Fore.YELLOW + "Lamports       :", Fore.WHITE + str(lamports))


# --------------------------------
# Print transactions
# --------------------------------

def print_recent_transactions(signatures):

    if not signatures:
        print(Fore.MAGENTA + "[INFO] No recent transactions found")
        return

    print(Fore.CYAN + "\n===== RECENT TRANSACTIONS =====")

    for tx_info in signatures:

        signature = tx_info.get("signature")

        print(Fore.MAGENTA + f"\nTX SIGNATURE: {Fore.WHITE}{signature}")

        tx = get_transaction(signature)

        if not tx:
            print(Fore.RED + "Could not fetch transaction details")
            continue

        transfers = extract_transfers(tx)

        if not transfers:
            print(Fore.YELLOW + "No balance changes detected")
            continue

        for t in transfers:

            wallet = t["wallet"]
            change = t["change"]

            if change > 0:
                print(f"{Fore.WHITE}{wallet} {Fore.BLUE}<- {Fore.GREEN}{change} SOL")
            else:
                print(f"{Fore.WHITE}{wallet} {Fore.BLUE}-> {Fore.RED}{abs(change)} SOL")


# --------------------------------
# Handler
# --------------------------------

def handle_solana_address(address):

    print(Fore.CYAN + f"\nDetected: {Fore.YELLOW}Solana")
    print(Fore.CYAN + f"Address Type: {Fore.MAGENTA}Solana Wallet")

    lamports = get_balance(address)

    if lamports is None:
        print(Fore.RED + "[ERROR] Could not fetch balance")
        return

    signatures = get_signatures(address)

    print_summary(address, lamports)
    print_recent_transactions(signatures)

    data = {
        "address": address,
        "balance_lamports": lamports,
        "balance_sol": lamports_to_sol(lamports),
        "transactions": signatures
    }

    ai_summarize(data, chain="Solana")