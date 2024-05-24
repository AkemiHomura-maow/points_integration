# Readme

## Overview

This project provides a Flask-based API to fetch the balance of a target token in a user's LP positions and unclaimed rewards on Optimism/Base. The balances are calculated by interacting with several smart contracts (`LpSugar`, `VotingRewardsHelper`, `PoolLpSugar`) deployed on different chains. The API also schedules periodic updates to pool data to ensure the information remains current.

## Prerequisites

- Python 3.x
- Brownie
- Flask
- Pandas
- Schedule
- Concurrent Futures

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/AkemiHomura-maow/points_integration.git
    cd points_integration
    ```

2. Install the required Python packages:
    ```bash
    pip3 install pipx
    npm install -g ganache-cli
    pipx install eth-brownie
    pipx inject eth-brownie pandas flask schedule
    ```

3. Create a `config.json` file with the necessary configurations. Example structure:
    ```json
    {
        "op":{
            "lp_sugar": "0xa8D674c71d34798Ec65C6cb1d2e7c0864735d2FD",
            "pool_lp_sugar": "0x55131F5215CC96f6784406d65aD0AC9598913D37",
            "ve_rewards_helper": "0x6fF159996Ec4237a9480E1B40857fa0c0F99C80c",
            "target": "0xTokenAddress"
        },
        "base":{
            "lp_sugar": "0x066D31221152f1f483DA474d1Ce47a4F50433e22",
            "pool_lp_sugar": "0xa3FE539901fe9836d4D32c88ef669ba1B28E3804",
            "ve_rewards_helper": "0x90D0368b5E96812568065bfebb43457282877743",
            "target": "0xTokenAddress"
        }
    }
    ```

## Usage

### Running the Flask API

To run the Flask API, use the following command:
```bash
brownie run scripts/main.py --network={NETWORK_NAME}
```

### API Endpoints

#### `GET /getBalance`
Fetch the balance of the target token in a user's LP positions and unclaimed rewards.

- **Parameters:**
    - `address` (required): The Ethereum address of the user.
    - `block` (optional): The block number to fetch the data from.

- **Example Request:**
    ```http
    GET /getBalance?address=0xYourEthereumAddress
    ```

- **Response:**
    ```json
    {
        "address": "0xUserAddress",
        "balance": 1234567890
    }
    ```

#### `GET /getPools`
Fetch information about pools and each corresponding fee voting rewards and bribe voting reward contract.

- **Parameters:**
    - None

- **Example Request:**
    ```http
    GET /getPools
    ```

- **Response:**
    ```json
    [
        {
            "bribe_voting_reward": "0xd57e9480234F2ac9321a48d875688827d2271451",
            "fee_voting_reward": "0x9291E1E76561749AF097F86B02C39F603f60d910",
            "pool": "0x8134A2fDC127549480865fB8E5A9E8A8a95a54c5"
        },
        ...
    ]
    ```

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

This project uses [Brownie](https://github.com/eth-brownie/brownie), [Flask](https://flask.palletsprojects.com/), [Velodrome Sugar](https://github.com/velodrome-finance/sugar) and other libraries.