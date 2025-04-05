import json
from solcx import compile_source, install_solc
from web3 import Web3
import os

install_solc('0.8.0')  # Ensure the version matches your contract

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))  # Ganache
account = w3.eth.accounts[0]

# Solidity source
contract_source_code = '''
pragma solidity ^0.8.0;

contract HashStore {
    mapping(bytes32 => bool) private storedHashes;

    function storeHash(bytes32 _hash) public {
        storedHashes[_hash] = true;
    }

    function verifyHash(bytes32 _hash) public view returns (bool) {
        return storedHashes[_hash];
    }
}
'''

def deploy_contract():
    # Check if ABI and contract address already exist
    if os.path.exists('BC/contract_abi.json') and os.path.exists('BC/contract_address.txt'):
        with open('BC/contract_abi.json', 'r') as f:
            abi = json.load(f)
        with open('BC/contract_address.txt', 'r') as f:
            contract_address = f.read()
        return contract_address, abi

    # Otherwise, compile and deploy the contract
    compiled_sol = compile_source(contract_source_code)
    contract_id, contract_interface = compiled_sol.popitem()

    # Deploy contract
    contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
    tx_hash = contract.constructor().transact({'from': account})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # Save ABI and address
    contract_address = tx_receipt.contractAddress
    abi = contract_interface['abi']

    with open("BC/contract_abi.json", "w") as f:
        json.dump(abi, f)

    with open("BC/contract_address.txt", "w") as f:
        f.write(contract_address)

    return contract_address, abi
