import json
from solcx import compile_source, install_solc
from web3 import Web3
from dotenv import load_dotenv
import os
from pathlib import Path
from ANN.models import BlockchainRecord


def record_classification(patient_id, result):
    # Load .env file
    env_path = Path(__file__).resolve().parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)

    # Install and set Solidity compiler version
    install_solc('0.8.0')

    # Solidity source code
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

    # Compile contract
    compiled_sol = compile_source(
        contract_source,
        output_values=['abi', 'bin'],
        solc_version='0.8.0'
    )
    contract_id, contract_interface = compiled_sol.popitem()
    abi = contract_interface['abi']
    bytecode = contract_interface['bin']

    # Web3 and account setup
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    assert w3.is_connected(), "Failed to connect to Ganache"

    private_key = os.getenv("PRIVATE_KEY")
    account = w3.eth.account.from_key(private_key)
    sender_address = account.address

    # Deploy contract
    DataStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(sender_address)

    deploy_tx = DataStorage.constructor().build_transaction({
        'from': sender_address,
        'nonce': nonce,
        'maxFeePerGas': w3.to_wei('2', 'gwei'),
        'maxPriorityFeePerGas': w3.to_wei('1', 'gwei'),
        'gas': 500000
    })

    signed_deploy_tx = w3.eth.account.sign_transaction(deploy_tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_deploy_tx.raw_transaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = tx_receipt.contractAddress

    # Store data
    contract = w3.eth.contract(address=contract_address, abi=abi)
    json_data = json.dumps({"patient_id": patient_id, "result": result})

    nonce = w3.eth.get_transaction_count(sender_address)
    store_tx = contract.functions.store(json_data).build_transaction({
        'from': sender_address,
        'nonce': nonce,
        'maxFeePerGas': w3.to_wei('2', 'gwei'),
        'maxPriorityFeePerGas': w3.to_wei('1', 'gwei'),
        'gas': 200000
    })

    signed_store_tx = w3.eth.account.sign_transaction(store_tx, private_key)
    store_tx_hash = w3.eth.send_raw_transaction(signed_store_tx.raw_transaction)
    w3.eth.wait_for_transaction_receipt(store_tx_hash)

    return "Data stored on blockchain.", contract_address, abi, bytecode

def retrieve_classification(patient_id):
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)

    # Connect to blockchain
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    assert w3.is_connected(), "Ganache not connected"

    # Get contract from DB
    try:
        record = BlockchainRecord.objects.get(patient_id=patient_id)
    except BlockchainRecord.DoesNotExist:
        raise Exception(f"No blockchain record found for Patient ID: {patient_id}")

    # Parse ABI
    abi = record.abi
    contract_address = record.contract_address
    print(abi)
    print(contract_address)

    # Connect to deployed contract
    contract = w3.eth.contract(address=contract_address, abi=abi)

    # Call contract function
    stored_data = contract.functions.get().call()
    retrieved_dict = json.loads(stored_data)

    return retrieved_dict
