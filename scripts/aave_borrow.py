from brownie import network, config, interface
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from web3 import Web3

amount = Web3.toWei(0.01, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    # ABI
    # address
    lending_pool = get_lending_pool()
    dai_address = config["networks"][network.show_active()]["dai_token"]

    print(lending_pool)
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    print("Depositing...")
    tx = lending_pool.deposit(
        erc20_address, amount, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("Deposited.")
    # how much ?
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Borrow some DAI")
    # DAi in terms of ETH
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    dai_to_borrow = (10 ** 18 / dai_eth_price) * (borrowable_eth * 0.90)
    print(f"Borrow {dai_to_borrow} DAI")

    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("Borrowed DAI.")
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    # repay all DAI
    repay_all(total_debt, lending_pool, dai_address, account)
    print(f"You have repayed all DAI debt of {total_debt}")


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    # ABI
    # address of lending pool - check
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def approve_erc20(amount, spender, erc20_address, account):
    """amount - amount to spend
    spender - who wpends the amount
    erc2_address - token address
    account - {"from": account}"""
    print("Approving erc20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved")
    return tx


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_luquidation_treshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"You have {total_collateral_eth} ETH collateral.")
    print(f"You have {total_debt_eth} ETH debt.")
    print(f"You have {available_borrow_eth} ETH to borrow.")
    return (float(available_borrow_eth), float(total_debt_eth))


def get_asset_price(price_feed_address):
    # get ABi
    # get address
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"DAI/ETH price is {converted_latest_price}")
    print(f"DAI/ETH price is {latest_price}")
    return float(latest_price)


def repay_all(repay_amount, lending_pool, token, account):
    approve_erc20(Web3.toWei(repay_amount, "ether"), lending_pool, token, account)
    repay_tx = lending_pool.repay(
        token, Web3.toWei(repay_amount, "ether"), 1, account.address, {"from": account}
    )
    repay_tx.wait(1)
