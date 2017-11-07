from indy import agent, ledger, pool, signus, wallet
import json
from indy.error import IndyError
import subprocess
import asyncio


async def test():
    seed_trustee01 = "000000000000000000000000Steward1"
    wallet_name = "test_wallet"
    pool_name = "pool_genesis_test1_s3"
    sovrin_version = "Running Sovrin 1.1.4.3"
    new_wallet_created = "New wallet Default created"
    pool_config_txn = ".sovrin/pool_transactions_sandbox_genesis"
    pool_config = json.dumps({"genesis_txn": str(pool_config_txn)})
    try:
        await pool.create_pool_ledger_config(pool_name, pool_config)
    except IndyError as E:
        print("Try to create new pool")
        await pool.delete_pool_ledger_config(pool_name)
        await pool.create_pool_ledger_config(pool_name, pool_config)

    # try:
    #     await wallet.create_wallet(pool_name, wallet_name, None, None, None)
    # except IndyError as E:
    #     print("Try to create wallet")
    #     await wallet.delete_wallet(wallet_name, None)
    #     await wallet.create_wallet(pool_name, wallet_name, None, None, None)
    #
    # wallet_handle = await wallet.open_wallet(wallet_name, None, None)
    #
    # await signus.create_and_store_my_did(wallet_handle, json.dumps({"seed": seed_trustee01}))
    #
    # print("Connect")
    # pool_handle = await pool.open_pool_ledger(pool_name, None)
    #
    # print("Disconnect")
    # await pool.close_pool_ledger(pool_handle)
    #
    # print("Reconnect")
    # pool_handle = await pool.open_pool_ledger(pool_name, None)


loop = asyncio.get_event_loop()
loop.run_until_complete(test())
loop.close()

print("End")
