# OncoNet

# Breast Cancer Classification with Blockchain Integration

This project aims to classify breast cancer data into "Malignant" or "Benign" categories using a machine learning model and securely store the classification results on a blockchain. It involves the following components:
- **Machine Learning Model**: A classifier built with Keras and trained on breast cancer data.
- **Blockchain**: A smart contract deployed on Ethereum (using Ganache for local development) to securely store the classification result.
- **Django Web Application**: A web interface to collect user input, classify data, and interact with the blockchain.

## Project Structure

- `Onconet/`: Main Django project directory.
- `ANN/`: Artificial Neural Network app.
- `BC/`: Blockchain app.
- `accounts/`: user app.
- `migrations/`: Django database migrations.
- `static/`: Static files (CSS, JavaScript).
- `templates/`: HTML templates.
- `requirements.txt`: Python dependencies.

## Features

- **Machine Learning Classifier**: Classifies breast cancer data as either benign or malignant using Keras.
- **Blockchain Integration**: Stores the classification result securely on the Ethereum blockchain using a Solidity smart contract.
- **Django Web Application**: Provides a user-friendly form to input data and see the result of the classification.

## Prerequisites

- Python 3.6 or higher
- Django 3.x or higher
- Keras
- TensorFlow
- Web3.py
- Solidity
- Ganache (local Ethereum blockchain)

## Installation

### 1. Clone the Repository

First, clone the project repository to your local machine.

```bash
git clone https://github.com/junaidshah2940/onconet.git
cd onconet
```

### 2. Install Dependencies

Make sure you have pip installed, then install the required dependencies.

```bash
pip install -r requirements.txt
```

### 3. Install Solidity Compiler (solcx)
This project uses solcx to compile Solidity contracts. To install it, run:

```bash
pip install py-solc-x
```

### 4. Install and Set Up Ganache
Install Ganache, which is a personal Ethereum blockchain for local development.

```bash
npm install -g ganache
ganache-cli --gasLimit 120000000 --port 8545 --deterministic
```

- `--gasLimit 120000000`: Sets a higher gas limit for transactions.
- `--port 8545`: Specifies the port for the blockchain.
- `--deterministic`: Ensures the same accounts and private keys are generated each time, which is useful for consistent development.

### 5. Run Django Development Server
Finally, run the Django development server to start the web application.

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000 in your browser to use the application.

## Usage
- **Input Data:** Navigate to the form and input the features for a breast cancer patient (e.g., radius, texture, perimeter, etc.).

- **Get Classification:** After submitting the form, the application will classify the data using the trained machine learning model and display the result.

- **Blockchain Integration:** The result will also be stored on the Ethereum blockchain, and a transaction hash will be displayed on the results page.

## Example Data
Here’s an example of some data you can input:

- radius1: 17.99

- texture1: 10.38

- perimeter1: 122.8

- area1: 1001

- smoothness1: 0.1184

- compactness1: 0.2776

- concavity1: 0.3001

- concave_points1: 0.1471

- symmetry1: 0.2416

- fractal_dimension1: 0.07871

Once you submit the form, the model will classify the result and save the hash of the classification to the blockchain.

## Code Structure
- **ANN:** Contains the machine learning model and related logic for classification.

- model.py: Contains the logic to load the trained Keras model and classify new data.

- views.py: Handles the Django views and processes the form data.

- forms.py: Defines the input form for breast cancer data.

- **BC:** Contains the blockchain-related functionality.

- blockchain.py: Contains the logic for storing and verifying the hash of classification results on the blockchain.

- contract_abi.json: The ABI of the deployed smart contract.

- contract_address.txt: The address of the deployed smart contract.

## How the Blockchain Works
The smart contract HashStore stores the SHA-256 hash of the classification result for each patient. By using the blockchain, the result is securely stored and can be verified by anyone with access to the contract.

## Smart Contract
The smart contract was written in Solidity and allows:

Storing the hash of the classification result.

Verifying the hash to ensure data integrity.

## Testing
To test the system, simply follow the usage instructions and input different values for the features. You can verify the blockchain interaction by checking the transaction hash and verifying it on the Ganache UI.

## Contributing
If you would like to contribute to this project, feel free to open an issue or submit a pull request. All contributions are welcome!



