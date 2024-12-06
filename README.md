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
            "lp_sugar": "0x1381B1E6aaFa01bD28e95AdaB35bdA8191826bC8",
            "pool_lp_sugar": "0x248F8EFb59cdDF7d94816a891a14A2ac6C1e05AB",
            "ve_rewards_helper": "0x6fF159996Ec4237a9480E1B40857fa0c0F99C80c",
            "target": "0xTokenAddress",
            "v2_router": "0xa062ae8a9c5e11aaa026fc2670b0d65ccc8b2858",
            "cl_router": "0x416b433906b1b72fa758e166e239c43d68dc6f29",
            "first_block": 120000000
        },
        "base":{
            "lp_sugar": "0xdE1682E50b4AeE52347fdfF1ef37Ec157DE25d7A",
            "pool_lp_sugar": "0x2c16eA5CF27542afC23dDcD4F54815F406d33209",
            "ve_rewards_helper": "0x90D0368b5E96812568065bfebb43457282877743",
            "target": "0xTokenAddress",
            "v2_router": "0xcf77a3ba9a5ca399b7c97c74d54e5b1beb874e43",
            "cl_router": "0x827922686190790b37229fd06084350e74485b72",
            "first_block": 13000000
        },
        "chainbase_key": ""
    }
    ```

## Usage

### Running the Flask API

To run the Flask API, use the following command:
```bash
brownie run scripts/main.py --network={NETWORK_NAME}
```

### API Endpoints

#### `GET /getBalances`
Retrieves the balances of specified users at a given blockchain height. If no block is specified, it defaults to the current blockchain height. If no users are provided, it fetches balances for all users.

- **Parameters:**
    - `users` (optional): A comma-separated list of user addresses. If not provided, retrieves balances for all users.
    - `block` (optional): The block number to fetch the data from.

- **Example Request:**
    ```http
    GET /getBalances?block=123&users=user1_address,user2_address
    ```

- **Response:**
    ```json
    [
    {
        "address": "user1_address",
        "effective_balance": 2.5
    },
    {
        "address": "user2_address",
        "effective_balance": 1.8
    }
    ]
    ```

#### `GET /getPools`
Fetch information about pools including the target token, and each corresponding fee voting rewards and bribe voting reward contract.

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

#### `GET /getUsers`
Fetch all of the users that have deposited into pools containing the target token, before the given block.

- **Parameters:**
    - `block` (optional): The block number to fetch the data before.

- **Example Request:**
    ```http
    GET /getUsers?block=14000000
    ```

- **Response:**
    ```json
    [
        {
            "from_address": "0xUserAddress",
        },
        ...
    ]
    ```

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

This project uses [Brownie](https://github.com/eth-brownie/brownie), [Flask](https://flask.palletsprojects.com/), [Velodrome Sugar](https://github.com/velodrome-finance/sugar) and other libraries.