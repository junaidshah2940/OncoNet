import json
import os
from pathlib import Path
from django.conf import settings
from solcx import compile_source, install_solc
from web3 import Web3
from dotenv import load_dotenv
from ANN.models import BlockchainRecord


def record_classification(patient_id, result):
    """Record classification result on blockchain"""
    
    # Load environment variables
    if hasattr(settings, 'BASE_DIR'):
        env_path = settings.BASE_DIR / '.env'
    else:
        env_path = Path(__file__).resolve().parent.parent / '.env'
    
    load_dotenv(dotenv_path=env_path)

    # Install and set Solidity compiler version
    try:
        install_solc('0.8.0')
    except Exception as e:
        print(f"Warning: Could not install Solidity compiler: {e}")

    # Solidity source code
    contract_source = '''
    pragma solidity ^0.8.0;

    contract DataStorage {
        string public data;
        
        event DataStored(string data);

        function store(string memory _data) public {
            data = _data;
            emit DataStored(_data);
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
    if not w3.is_connected():
        raise ConnectionError("Failed to connect to Ganache. Please ensure Ganache is running on http://127.0.0.1:8545")

    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        raise ValueError("PRIVATE_KEY not found in .env file")

    # Normalize private key format
    if private_key.startswith('0x'):
        private_key = private_key[2:]
    private_key = '0x' + private_key

    try:
        account = w3.eth.account.from_key(private_key)
        sender_address = account.address
        print(f"Using account: {sender_address}")
    except Exception as e:
        raise ValueError(f"Invalid private key: {e}")

    # Check account balance
    balance = w3.eth.get_balance(sender_address)
    balance_eth = w3.from_wei(balance, 'ether')
    print(f"Account {sender_address} has {balance_eth} ETH")
    
    # Fund account if insufficient balance
    if balance_eth < 0.01:  # Need at least 0.01 ETH for transactions
        print("Insufficient balance. Attempting to fund account...")
        
        # Ganache default accounts (first 3 are usually well-funded)
        ganache_accounts = [
            "0x0bae0c6cb4d2b350f7422102d6cc2f1ed7bce1f3776b4d23264017fd655ea5eb",
            "0xce44371f3865a4a7d15cdeff3e2a2d65968e9636effd2eed505dae3c408f2314",
            "0x47de1e1621fb2a7ac676d241e335d6ebde52627c4658292fbf60915ae2149599"
        ]
        
        funded = False
        for ganache_key in ganache_accounts:
            try:
                if fund_account_from_ganache(w3, ganache_key, sender_address, 1.0):
                    # Recheck balance
                    balance = w3.eth.get_balance(sender_address)
                    balance_eth = w3.from_wei(balance, 'ether')
                    print(f"Account funded successfully! New balance: {balance_eth} ETH")
                    funded = True
                    break
            except Exception as e:
                print(f"Failed to fund from account: {e}")
                continue
        
        if not funded:
            raise ValueError(
                "Could not fund account automatically. Please either:\n"
                "1. Use account 0 private key: 0x0bae0c6cb4d2b350f7422102d6cc2f1ed7bce1f3776b4d23264017fd655ea5eb\n"
                "2. Manually fund your account using Ganache GUI\n"
                "3. Restart Ganache to reset accounts"
            )

    # Get current network gas price
    try:
        gas_price = w3.eth.gas_price
        min_gas_price = max(gas_price, w3.to_wei('1', 'gwei'))
    except:
        min_gas_price = w3.to_wei('2', 'gwei')

    # Deploy contract
    DataStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(sender_address)

    try:
        print("Deploying contract...")
        deploy_tx = DataStorage.constructor().build_transaction({
            'from': sender_address,
            'nonce': nonce,
            'gas': 500000,  # Increased gas limit for safety
            'gasPrice': min_gas_price
        })

        signed_deploy_tx = w3.eth.account.sign_transaction(deploy_tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_deploy_tx.raw_transaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        contract_address = tx_receipt.contractAddress
        print(f"Contract deployed successfully at: {contract_address}")
        print(f"Gas used for deployment: {tx_receipt.gasUsed}")

    except Exception as e:
        if "insufficient funds" in str(e).lower():
            current_balance = w3.from_wei(w3.eth.get_balance(sender_address), 'ether')
            raise ValueError(f"Insufficient funds for contract deployment. Current balance: {current_balance} ETH")
        else:
            raise Exception(f"Contract deployment failed: {e}")

    # Store data in contract
    contract = w3.eth.contract(address=contract_address, abi=abi)
    json_data = json.dumps({"patient_id": patient_id, "result": result})

    nonce += 1
    try:
        print("Storing data on blockchain...")
        store_tx = contract.functions.store(json_data).build_transaction({
            'from': sender_address,
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': min_gas_price
        })

        signed_store_tx = w3.eth.account.sign_transaction(store_tx, private_key)
        store_tx_hash = w3.eth.send_raw_transaction(signed_store_tx.raw_transaction)
        store_receipt = w3.eth.wait_for_transaction_receipt(store_tx_hash, timeout=120)
        
        print(f"Data stored successfully! Transaction hash: {store_tx_hash.hex()}")
        print(f"Gas used for storage: {store_receipt.gasUsed}")

    except Exception as e:
        if "insufficient funds" in str(e).lower():
            current_balance = w3.from_wei(w3.eth.get_balance(sender_address), 'ether')
            raise ValueError(f"Insufficient funds for data storage. Current balance: {current_balance} ETH")
        else:
            raise Exception(f"Data storage failed: {e}")

    # Save to Django database
    try:
        # First, check if any records exist for this patient
        existing_records = BlockchainRecord.objects.filter(patient_id=patient_id)
        
        if existing_records.exists():
            # Delete old records and create new one
            old_count = existing_records.count()
            existing_records.delete()
            print(f"Deleted {old_count} old blockchain records for patient {patient_id}")
        
        # Create new record
        blockchain_record = BlockchainRecord.objects.create(
            patient_id=patient_id,
            contract_address=contract_address,
            abi=json.dumps(abi),
            bytecode=bytecode
        )
        
        print(f"New blockchain record created in database for patient {patient_id}")
            
    except Exception as e:
        print(f"Warning: Could not save blockchain record to database: {e}")
        # Don't raise error here as blockchain operation was successful

    return f"Data stored successfully on blockchain at {contract_address}", contract_address, abi, bytecode


def fund_account_from_ganache(w3, ganache_private_key, target_address, amount_eth=1.0):
    """Fund an account from a Ganache pre-funded account"""
    try:
        # Normalize key format
        if ganache_private_key.startswith('0x'):
            ganache_private_key = ganache_private_key[2:]
        ganache_private_key = '0x' + ganache_private_key
        
        from_account = w3.eth.account.from_key(ganache_private_key)
        
        # Check source account balance
        source_balance = w3.eth.get_balance(from_account.address)
        source_balance_eth = w3.from_wei(source_balance, 'ether')
        
        if source_balance_eth < amount_eth + 0.001:  # Include gas costs
            print(f"Source account {from_account.address} has insufficient balance: {source_balance_eth} ETH")
            return False
        
        # Get gas price
        try:
            gas_price = w3.eth.gas_price
            min_gas_price = max(gas_price, w3.to_wei('2', 'gwei'))
        except:
            min_gas_price = w3.to_wei('2', 'gwei')
        
        # Create funding transaction
        tx = {
            'to': target_address,
            'value': w3.to_wei(amount_eth, 'ether'),
            'gas': 21000,
            'gasPrice': min_gas_price,
            'nonce': w3.eth.get_transaction_count(from_account.address)
        }
        
        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(tx, ganache_private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
        
        print(f"Successfully funded {target_address} with {amount_eth} ETH")
        return True
        
    except Exception as e:
        print(f"Failed to fund account: {e}")
        return False


def retrieve_classification(patient_id):
    """Retrieve classification result from blockchain"""
    
    # Load environment variables
    if hasattr(settings, 'BASE_DIR'):
        env_path = settings.BASE_DIR / '.env'
    else:
        env_path = Path(__file__).resolve().parent.parent / '.env'
    
    load_dotenv(dotenv_path=env_path)

    # Connect to blockchain
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    if not w3.is_connected():
        raise ConnectionError("Failed to connect to Ganache")

    # Get contract details from database - handle multiple records
    try:
        # Get the most recent record for this patient
        record = BlockchainRecord.objects.filter(patient_id=patient_id).order_by('-id').first()
        
        if not record:
            raise Exception(f"No blockchain record found for Patient ID: {patient_id}")
            
        print(f"Using blockchain record ID: {record.id} for patient: {patient_id}")
        
    except Exception as e:
        raise Exception(f"Database error: {e}")

    # Parse contract details
    try:
        abi = json.loads(record.abi) if isinstance(record.abi, str) else record.abi
        contract_address = record.contract_address
        
        print(f"Connecting to contract at: {contract_address}")
        
        # Connect to deployed contract
        contract = w3.eth.contract(address=contract_address, abi=abi)
        
        # Retrieve data from contract
        stored_data = contract.functions.get().call()
        
        # Parse JSON data
        if stored_data:
            retrieved_dict = json.loads(stored_data)
            print(f"Retrieved data: {retrieved_dict}")
            return retrieved_dict
        else:
            raise Exception("No data found in contract")
            
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse stored data: {e}")
    except Exception as e:
        raise Exception(f"Failed to retrieve data from blockchain: {e}")


def get_account_balance(address=None):
    """Utility function to check account balance"""
    try:
        load_dotenv()
        w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
        
        if not w3.is_connected():
            return "Not connected to Ganache"
        
        if address is None:
            private_key = os.getenv("PRIVATE_KEY")
            if not private_key:
                return "PRIVATE_KEY not found in .env"
            
            if private_key.startswith('0x'):
                private_key = private_key[2:]
            private_key = '0x' + private_key
            
            account = w3.eth.account.from_key(private_key)
            address = account.address
        
        balance = w3.eth.get_balance(address)
        balance_eth = w3.from_wei(balance, 'ether')
        
        return f"Account {address} has {balance_eth} ETH"
        
    except Exception as e:
        return f"Error checking balance: {e}"


def check_ganache_connection():
    """Check if Ganache is running and accessible"""
    try:
        w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
        if w3.is_connected():
            latest_block = w3.eth.get_block('latest')
            return f"✓ Connected to Ganache. Latest block: {latest_block.number}"
        else:
            return "✗ Cannot connect to Ganache"
    except Exception as e:
        return f"✗ Ganache connection error: {e}"


def cleanup_duplicate_records():
    """Clean up duplicate blockchain records, keeping only the most recent one for each patient"""
    try:
        # Get all patient IDs that have multiple records
        from django.db.models import Count
        
        duplicates = (BlockchainRecord.objects
                     .values('patient_id')
                     .annotate(count=Count('patient_id'))
                     .filter(count__gt=1))
        
        if not duplicates:
            return "No duplicate records found"
        
        cleaned_count = 0
        for duplicate in duplicates:
            patient_id = duplicate['patient_id']
            # Get all records for this patient, ordered by ID (newest first)
            records = BlockchainRecord.objects.filter(patient_id=patient_id).order_by('-id')
            
            # Keep the first (newest) record, delete the rest
            records_to_delete = records[1:]  # Skip the first one
            delete_count = len(records_to_delete)
            
            for record in records_to_delete:
                record.delete()
            
            cleaned_count += delete_count
            print(f"Cleaned {delete_count} duplicate records for patient {patient_id}")
        
        return f"Cleaned up {cleaned_count} duplicate records for {len(duplicates)} patients"
        
    except Exception as e:
        return f"Error cleaning up duplicates: {e}"


def get_patient_blockchain_records(patient_id):
    """Get all blockchain records for a specific patient"""
    try:
        records = BlockchainRecord.objects.filter(patient_id=patient_id).order_by('-id')
        
        if not records:
            return f"No blockchain records found for patient {patient_id}"
        
        result = f"Blockchain records for patient {patient_id}:\n"
        for i, record in enumerate(records, 1):
            result += f"{i}. ID: {record.id}, Contract: {record.contract_address}\n"
        
        return result
        
    except Exception as e:
        return f"Error getting patient records: {e}"


# Django management command helper functions
def reset_blockchain_records():
    """Reset all blockchain records (useful for development)"""
    try:
        count = BlockchainRecord.objects.count()
        BlockchainRecord.objects.all().delete()
        return f"Deleted {count} blockchain records"
    except Exception as e:
        return f"Error resetting records: {e}"


def list_blockchain_records():
    """List all blockchain records"""
    try:
        records = BlockchainRecord.objects.all().order_by('patient_id', '-id')
        if not records:
            return "No blockchain records found"
        
        result = "Blockchain Records:\n"
        current_patient = None
        for record in records:
            if current_patient != record.patient_id:
                if current_patient is not None:
                    result += "\n"
                current_patient = record.patient_id
                result += f"Patient ID: {record.patient_id}\n"
            result += f"  - Record ID: {record.id}, Contract: {record.contract_address}\n"
        
        return result
    except Exception as e:
        return f"Error listing records: {e}"