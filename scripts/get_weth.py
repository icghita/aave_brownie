from scripts.helpful_scripts import get_account
from brownie import interface, config, network


# Swap ETH for WETH
def main():
    get_weth()


def get_weth():
    """deposit ETH, mint WETH"""
    # ABI
    # address
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    val = 0.01
    tx = weth.deposit({"from": account, "value": val * 10**18})
    tx.wait(1)
    print(f"Received {val} WETH.")
    return tx
