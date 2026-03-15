# # main.py

# from crypto_identification import identify_crypto


# def main():

#     address = input("Enter crypto address: ").strip()

#     identify_crypto(address)


# if __name__ == "__main__":
#     main()

# main.py
from crypto_identification import identify_crypto

if __name__ == "__main__":
    # Get address input
    address = input("Enter crypto address: ").strip()

    # Identify cryptocurrency and handle it
    identify_crypto(address)