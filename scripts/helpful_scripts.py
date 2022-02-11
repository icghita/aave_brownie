from brownie import (
    accounts,
    network,
    config,
    # MockV3Aggregator,
    # VRFCoordinatorMock,
    # LinkToken,
    Contract,
    interface,
)

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["mainnet-fork", "development", "ganache-local"]
DECIMALS = 8
INITIAL_VALUE = 200000000000


def get_account(index=None, id=None):
    # accounts[0]
    # accounts.add("env")
    # accounts.load("id")
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    if network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])
    return None
