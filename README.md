Modify `targets` attribute in `config.json` to change the target token to track. E.g. if the API is for `weETH`, then set `targets` to `weETH`'s address on its corresponding chain.

To run, use `brownie run scripts/main.py --network={NETWORK_NAME}`

To access API, use `http://127.0.0.1:5000/getBalance?address={USER_ADDRESS}&block={BLOCK}`

`block` is an optional parameter to query past balances

Sample response:

`{
  "address": "0x28aa4f9ffe21365473b64c161b566c3cdead0108",
  "balance": 16780703115661361156221
}`