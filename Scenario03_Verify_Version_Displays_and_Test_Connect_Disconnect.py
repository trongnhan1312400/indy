from indy import agent, ledger, pool, signus
import json
import asyncio


async def test():
    seed_trustee1 = "000000000000000000000000Steward1"

    print("Begin")

    print("Connect to test")
    pool_handle = await pool.open_pool_ledger("test", None)
    print(pool_handle)

    print("new key seed 000000000000000000000000Steward1")
    (sender_did, sender_verkey, sender_pk) = await signus.create_and_store_my_did("default", json.dumps({"seed": seed_trustee1}))

    print("close pool")
    await pool.close_pool_ledger(pool_handle)

    print("reconnect pool")
    pool_handle = await pool.open_pool_ledger("test", None)

    await pool.close_pool_ledger(pool_handle)


loop = asyncio.get_event_loop()
loop.run_until_complete(test())
loop.close()

print("End")
