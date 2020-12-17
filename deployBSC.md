# Deploy to BSC

## Add BSC network to brownie

1. Add bsc testnet and mainnet to brownie
```shell script
brownie networks add BSC bsc_testnet host=https://data-seed-prebsc-1-s1.binance.org:8545 chainid=97
brownie networks add BSC bsc_mainnet host=https://bsc-dataseed1.binance.org:443 chainid=56
```

2. List all network
```shell script
brownie networks list
```
Example response:
```text
Brownie v1.11.12 - Python development framework for Ethereum

The following networks are declared:

Ethereum
  ├─Mainnet (Infura): mainnet
  ├─Ropsten (Infura): ropsten
  ├─Rinkeby (Infura): rinkeby
  ├─Goerli (Infura): goerli
  └─Kovan (Infura): kovan

Ethereum Classic
  ├─Mainnet: etc
  └─Kotti: kotti

BSC
  ├─bsc_mainnet: bsc_mainnet
  └─bsc_testnet: bsc_testnet

Development
  ├─Ganache-CLI: development
  └─Ganache-CLI (Mainnet Fork): mainnet-fork
```

## Take USDN For Example

1. Edit `scripts/deploy.py`
```python
POOL_NAME = ""
```
To
```python
POOL_NAME = "usdn"
```

2. Edit `pooldata.json`

```json
        {
            "name": "3CRV",
            "decimals": 18,
            "base_pool_token": true,
            "underlying_address": "0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490"
        }
```
To
```json
        {
            "name": "3CRV",
            "decimals": 18,
            "base_pool_token": true,
            "underlying_address": "0x905406aA329695b4De2d68d59E36b1Ba4Ca523FB"
        }
```

3. Deploy token (USDN token)[https://etherscan.io/address/0x674C6Ad92Fd080e4004b2312b45f796a192D27a0#code] on bsc.

4. Deploy to bsc
```shell script
brownie run deploy --network bsc_testnet
```