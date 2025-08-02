import json
import time
from decimal import Decimal
from tronpy import Tron
from tronpy.providers import HTTPProvider
from tronpy.keys import PrivateKey
from key import PRIVATE_KEY, to_address
from keep_alive import keep_alive

def get_trx_balance(client, address):
    return client.get_account_balance(address)

def estimate_trx_fee(client, from_addr, to_addr, amount_sun):
    txn = client.trx.transfer(from_addr, to_addr, amount_sun).build()
    txn_dict = txn.to_json()
    res = client.provider.make_request("wallet/estimateenergy", txn_dict)
    energy_fee = res.get("energy_fee", 0)
    net_fee = res.get("net_fee", 0)
    total_fee_sun = energy_fee + net_fee
    return Decimal(total_fee_sun) / Decimal(1_000_000)

def send_all_trx(client, priv_key, from_addr, to_addr, send_amount_trx):
    send_amount_sun = int(send_amount_trx * Decimal(1_000_000))
    txn = client.trx.transfer(from_addr, to_addr, send_amount_sun).build().sign(priv_key).broadcast()
    return txn

def main():
    client = Tron(HTTPProvider("https://api.tronstack.io"))
    priv_key = PrivateKey(bytes.fromhex(PRIVATE_KEY))
    from_addr = priv_key.public_key.to_base58check_address()
    while True:
        try:
            balance = get_trx_balance(client, from_addr)
            if balance > 0:
                max_amount_sun = int(balance * Decimal(1_000_000))
                fee = estimate_trx_fee(client, from_addr, to_address, max_amount_sun)
                send_amount = balance - fee
                if send_amount > 0:
                    txn_result = send_all_trx(client, priv_key, from_addr, to_address, send_amount)
                    with open("log.txt", "a") as log:
                        log.write(f"Sent {send_amount} TRX\nTxID: {txn_result['txid']}\n")
            time.sleep(10)
        except Exception as e:
            with open("log.txt", "a") as log:
                log.write(f"Error: {e}\n")
            time.sleep(5)

if __name__ == "__main__":
    keep_alive()
    main()
