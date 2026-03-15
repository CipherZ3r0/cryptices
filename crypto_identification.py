# crypto_identification.py

import hashlib

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


# -------------------------
# BASE58
# -------------------------

def base58_decode(address):
    num = 0
    for char in address:
        num *= 58
        if char not in BASE58_ALPHABET:
            return None
        num += BASE58_ALPHABET.index(char)

    return num.to_bytes(25, byteorder="big")


def validate_base58_checksum(address):
    decoded = base58_decode(address)

    if not decoded or len(decoded) != 25:
        return False

    payload = decoded[:-4]
    checksum = decoded[-4:]

    hash1 = hashlib.sha256(payload).digest()
    hash2 = hashlib.sha256(hash1).digest()

    return checksum == hash2[:4]


# -------------------------
# BECH32
# -------------------------

def validate_bech32(address):

    if address.lower() != address and address.upper() != address:
        return False

    address = address.lower()
    pos = address.rfind("1")

    if pos < 1 or pos + 7 > len(address):
        return False

    return True


# -------------------------
# BITCOIN DETECTION
# -------------------------

def get_btc_address_type(address):

    if address.startswith("1") and validate_base58_checksum(address):
        return "P2PKH (Legacy)"

    if address.startswith("3") and validate_base58_checksum(address):
        return "P2SH"

    if address.startswith("bc1q") and validate_bech32(address):
        return "SegWit (Bech32)"

    if address.startswith("bc1p") and validate_bech32(address):
        return "Taproot"

    return None


# -------------------------
# ROUTING
# -------------------------

def identify_crypto(address):

    btc_type = get_btc_address_type(address)

    if btc_type:
        print("Detected: Bitcoin")
        print("Address Type:", btc_type)

        from services.bitcoin.bitcoin_utils import handle_bitcoin_address
        handle_bitcoin_address(address)

        return

    print("Unknown or unsupported address")