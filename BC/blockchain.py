import json
from solcx import compile_source, install_solc
from web3 import Web3
from dotenv import load_dotenv
import os
from pathlib import Path


def record_classification(patient_id, result):
    env_path = Path(__file__).resolve().parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)   
    install_solc('0.8.0')

    contract_source = '''
    pragma solidity ^0.8.0;

    contract DataStorage {
        string public data;

        function store(string memory _data) public {
            data = _data;
        }

        function get() public view returns (string memory) {
            return data;
        }
    }
    '''

    compiled_sol = compile_source(
        contract_source,
        output_values=['abi', 'bin'],
        solc_version='0.8.0'
    )
    contract_id, contract_interface = compiled_sol.popitem()
    abi = contract_interface['abi']
    bytecode = contract_interface['bin']

    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    assert w3.is_connected(), "Failed to connect to Ganache"

    private_key = os.getenv("PRIVATE_KEY")
    account = w3.eth.account.from_key(private_key)
    sender_address = account.address

    DataStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

    nonce = w3.eth.get_transaction_count(sender_address)
    tx = DataStorage.constructor().build_transaction({
        'from': sender_address,
        'nonce': nonce,
        'gas': 2000000,
        'gasPrice': w3.to_wei('50', 'gwei')
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    contract_address = tx_receipt.contractAddress

    contract = w3.eth.contract(address=contract_address, abi=abi)

    my_dict = {"patient_id": patient_id, "result": result}
    json_str = json.dumps(my_dict)

    nonce = w3.eth.get_transaction_count(sender_address)
    store_txn = contract.functions.store(json_str).build_transaction({
        'from': sender_address,
        'nonce': nonce,
        'gas': 100000,
        'gasPrice': w3.to_wei('50', 'gwei')
    })


    signed_store_txn = w3.eth.account.sign_transaction(store_txn, private_key)
    store_tx_hash = w3.eth.send_raw_transaction(signed_store_txn.raw_transaction)
    w3.eth.wait_for_transaction_receipt(store_tx_hash)
    return ("Data stored on blockchain.", contract_address, abi, bytecode)

