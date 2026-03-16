import os
from groq import Groq
from dotenv import load_dotenv
from colorama import Fore

# Load .env file
load_dotenv()

# Initialize Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def extract_wallet_stats(data):
    """Extract only important statistics for AI analysis"""

    stats = {
        "address": data.get("address"),
        "total_received": data.get("total_received", 0),
        "total_sent": data.get("total_sent", 0),
        "final_balance": data.get("final_balance", 0),
        "transaction_count": data.get("n_tx", 0),
    }

    return stats


def ai_summarize(data, chain="Unknown"):
    """Generate AI summary of wallet activity"""

    stats = extract_wallet_stats(data)

    prompt = f"""
You are a blockchain investigation assistant.

Analyze this cryptocurrency wallet activity and summarize it briefly.

Blockchain: {chain}

Wallet Data:
Address: {stats['address']}
Total Received (satoshi): {stats['total_received']}
Total Sent (satoshi): {stats['total_sent']}
Final Balance (satoshi): {stats['final_balance']}
Transaction Count: {stats['transaction_count']}

Explain the wallet behavior in simple terms.
Mention possible usage patterns if visible.
Limit response to 3-5 sentences.
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.6
        )

        summary = completion.choices[0].message.content

        print(Fore.CYAN + "\n===== AI WALLET ANALYSIS =====")
        print(Fore.WHITE + summary)

    except Exception as e:
        print(Fore.RED + f"[AI ERROR] {str(e)}")