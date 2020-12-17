import json
import requests

from brownie import accounts
from brownie.project.main import get_loaded_projects

# modify this import if you wish to deploy a different liquidity gauge
from brownie import LiquidityGauge as LiquidityGauge

# set a throwaway admin account here
DEPLOYER = accounts.add('52aa4ed7d96818b652e6b2d677379f3b9b7cd182567622dafb2226e17c8ccdca')
REQUIRED_CONFIRMATIONS = 1

# deployment settings
# most settings are taken from `contracts/pools/{POOL_NAME}/pooldata.json`
POOL_NAME = ""
POOL_OWNER = "0xa1715792fE0C2F542BB78922878F956bB6E7d0d8"  # PoolProxy
MINTER = "0x0b6845BC97B28Bdf1E9Cec448DC5A0A075120697"


def _gas_price():
    data = requests.get("https://www.gasnow.org/api/v3/gas/price").json()
    # change `fast` to `rapid` if you're in a hurry
    return data['data']['fast'] + 10**9


def _tx_params():
    return {'from': DEPLOYER, 'required_confs': REQUIRED_CONFIRMATIONS, 'gas_price': _gas_price()}


def main():
    project = get_loaded_projects()[0]
    balance = DEPLOYER.balance()

    # load data about the deployment from `pooldata.json`
    contracts_path = project._path.joinpath("contracts/pools")
    with contracts_path.joinpath(f"{POOL_NAME}/pooldata.json").open() as fp:
        pool_data = json.load(fp)

    swap_name = next(i.stem for i in contracts_path.glob(f"{POOL_NAME}/StableSwap*"))
    swap_deployer = getattr(project, swap_name)
    token_deployer = getattr(project, pool_data.get('lp_contract'))

    underlying_coins = [i['underlying_address'] for i in pool_data['coins']]
    wrapped_coins = [i.get('wrapped_address', i['underlying_address']) for i in pool_data['coins']]

    base_pool = None
    if "base_pool" in pool_data:
        with contracts_path.joinpath(f"{pool_data['base_pool']}/pooldata.json").open() as fp:
            base_pool_data = json.load(fp)
            base_pool = base_pool_data['swap_address']

    # deploy the token
    token_args = pool_data["lp_constructor"]
    token = token_deployer.deploy(token_args['name'], token_args['symbol'], 18, 0, _tx_params())

    # deploy the pool
    abi = next(i['inputs'] for i in swap_deployer.abi if i['type'] == "constructor")
    args = pool_data["swap_constructor"]
    args.update(
        _coins=wrapped_coins,
        _underlying_coins=underlying_coins,
        _pool_token=token,
        _base_pool=base_pool,
        _owner=POOL_OWNER,
    )
    deployment_args = [args[i['name']] for i in abi] + [_tx_params()]

    swap = swap_deployer.deploy(*deployment_args)

    # set the minter
    token.set_minter(swap, _tx_params())

    # deploy the liquidity gauge
    LiquidityGauge.deploy(token, MINTER, POOL_OWNER, _tx_params())

    # deploy the zap
    zap_name = next((i.stem for i in contracts_path.glob(f"{POOL_NAME}/Deposit*")), None)
    if zap_name is not None:
        zap_deployer = getattr(project, zap_name)

        abi = next(i['inputs'] for i in zap_deployer.abi if i['type'] == "constructor")
        args = {
            '_coins': wrapped_coins,
            '_underlying_coins': underlying_coins,
            '_token': token,
            '_pool': swap,
            '_curve': swap,
        }
        deployment_args = [args[i['name']] for i in abi] + [_tx_params()]

        zap_deployer.deploy(*deployment_args)

    print(f'Gas used in deployment: {(balance - DEPLOYER.balance()) / 1e18:.4f} ETH')
