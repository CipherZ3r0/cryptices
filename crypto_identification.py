# crypto_identification.py

import hashlib

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


# --------------------------------------------------
# BASE58
# --------------------------------------------------

def base58_decode(address):
    num = 0

    for char in address:
        num *= 58

        if char not in BASE58_ALPHABET:
            return None

        num += BASE58_ALPHABET.index(char)

    try:
        return num.to_bytes((num.bit_length() + 7) // 8, byteorder="big")
    except:
        return None


def validate_base58_checksum(address):

    decoded = base58_decode(address)

    if not decoded or len(decoded) != 25:
        return False

    payload = decoded[:-4]
    checksum = decoded[-4:]

    hash1 = hashlib.sha256(payload).digest()
    hash2 = hashlib.sha256(hash1).digest()

    return checksum == hash2[:4]


# --------------------------------------------------
# BECH32
# --------------------------------------------------

def validate_bech32(address):

    if address.lower() != address and address.upper() != address:
        return False

    address = address.lower()
    pos = address.rfind("1")

    if pos < 1 or pos + 7 > len(address):
        return False

    return True


# --------------------------------------------------
# BITCOIN DETECTOR
# --------------------------------------------------

def detect_bitcoin(address):

    if address.startswith("1") and validate_base58_checksum(address):
        return {
            "chain": "Bitcoin",
            "type": "P2PKH (Legacy)",
            "handler": "services.bitcoin.bitcoin_utils.handle_bitcoin_address"
        }

    if address.startswith("3") and validate_base58_checksum(address):
        return {
            "chain": "Bitcoin",
            "type": "P2SH",
            "handler": "services.bitcoin.bitcoin_utils.handle_bitcoin_address"
        }

    if address.startswith("bc1q") and validate_bech32(address):
        return {
            "chain": "Bitcoin",
            "type": "SegWit (Bech32)",
            "handler": "services.bitcoin.bitcoin_utils.handle_bitcoin_address"
        }

    if address.startswith("bc1p") and validate_bech32(address):
        return {
            "chain": "Bitcoin",
            "type": "Taproot",
            "handler": "services.bitcoin.bitcoin_utils.handle_bitcoin_address"
        }

    return None


# --------------------------------------------------
# SOLANA DETECTOR
# --------------------------------------------------

def detect_solana(address):

    decoded = base58_decode(address)

    if decoded and len(decoded) == 32:
        return {
            "chain": "Solana",
            "type": "Solana Wallet",
            "handler": "services.solana.solana_utils.handle_solana_address"
        }

    return None


def detect_ethereum(address):

    if address.startswith("0x") and len(address) == 42:
        return {
            "chain": "Ethereum",
            "type": "EVM Address",
            "handler": "services.ethereum.ethereum_utils.handle_ethereum_address"
        }

    return None


# --------------------------------------------------
# DETECTOR REGISTRY
# --------------------------------------------------

DETECTORS = [
    detect_bitcoin,
    detect_solana,
    detect_ethereum
]


# --------------------------------------------------
# ROUTER
# --------------------------------------------------

def identify_crypto(address):

    for detector in DETECTORS:

        result = detector(address)

        if result:

            print("Detected:", result["chain"])
            print("Address Type:", result["type"])

            module_path, func_name = result["handler"].rsplit(".", 1)

            module = __import__(module_path, fromlist=[func_name])
            handler = getattr(module, func_name)

            handler(address)

            return

    print("Unknown or unsupported address")