from indy import agent, ledger, pool, signus
import json


def test():
    seed_trustee1 = "000000000000000000000000Steward1"

    print("Begin")

    print("Connect to test")
    pool_handle = pool.open_pool_ledger("test", None)
    print(pool_handle)

    print("new key seed 000000000000000000000000Steward1")
    (sender_did, sender_verkey, sender_pk) = signus.create_and_store_my_did("default", json.dumps({"seed": seed_trustee1}))

    print("close pool")
    pool.close_pool_ledger(pool_handle)

    print("reconnect pool")
    pool_handle = pool.open_pool_ledger("test", None)

    pool.close_pool_ledger(pool_handle)


test()
