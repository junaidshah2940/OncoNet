from web3 import Web3
import hashlib
import datetime
import json

# Connect to local blockchain (Ganache)
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
account = w3.eth.accounts[0]

# Load ABI and address from files
def load_contract():
    with open('BC/contract_abi.json') as f:
        abi = json.load(f)

    with open('BC/contract_address.txt') as f:
        contract_address = f.read().strip()

    contract = w3.eth.contract(address=contract_address, abi=abi)
    return contract

# Generate hash of the classification data
def hash_classification(patient_id, result):
    data = f'{patient_id}_{result}_{datetime.datetime.utcnow()}'
    return Web3.toBytes(hexstr=hashlib.sha256(data.encode()).hexdigest())

# Store classification result on the blockchain
def record_classification(patient_id, result):
    contract = load_contract()  # Use the loaded contract
    data_hash = hash_classification(patient_id, result)
    tx_hash = contract.functions.storeHash(data_hash).transact({'from': account})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()
