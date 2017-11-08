from indy import agent, ledger, pool, signus, wallet
import json
from indy.error import IndyError
import sys
import logging
import os
import asyncio
import shutil


class Colors:
    """ Class to set the colors for text.  Syntax:  print(Colors.OKGREEN +"TEXT HERE" +Colors.ENDC) """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'  # Normal default color
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class MyVars:
    """  Needed some global variables. """

    pool_handle = 0
    # Need the path to the pool transaction file location
    pool_genesis_txn_file = ".sovrin/pool_transactions_sandbox_genesis"
    wallet_handle = 0
    pool_name = "pool_genesis_test3"
    wallet_name = "test_wallet3"
    debug = False
    test_results = {'Test 4': True}


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def test_prep():
    print(Colors.HEADER + "\n\tCheck if the wallet and pool for this test already exist and delete them...\n"
          + Colors.ENDC)

    if os.path.exists(".sovrin/wallets/no-env/" + MyVars.wallet_name):
        try:
            shutil.rmtree(".sovrin/wallets/no-env/" + MyVars.wallet_name)
        except IOError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)

    if os.path.exists(".sovrin/wallets/test/" + MyVars.wallet_name):
        try:
            shutil.rmtree(".sovrin/wallets/test/" + MyVars.wallet_name)
        except IOError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)

    if os.path.exists(".sovrin/" + MyVars.pool_name):
        try:
            shutil.rmtree(".sovrin/" + MyVars.pool_name)
        except IOError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)


async def do():
    logger.info("Test scenario 3 -> started")

    seed_trustee01 = "000000000000000000000000Steward1"
    pool_config = json.dumps({"genesis_txn": str(MyVars.pool_genesis_txn_file)})

    print(Colors.HEADER + "\n\t1.  Create Ledger\n" + Colors.ENDC)
    try:
        await pool.create_pool_ledger_config(MyVars.pool_name, pool_config)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        sys.exit[1]

    print(Colors.HEADER + "\n\t3. Create wallet\n" + Colors.ENDC)
    try:
        await wallet.create_wallet(MyVars.pool_name, MyVars.wallet_name, None, None, None)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        sys.exit[1]

    try:
        MyVars.wallet_handle = wallet.open_wallet(MyVars.wallet_name, None)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    print(Colors.HEADER + "\n\t4. Create DID's\n" + Colors.ENDC)
    try:
        await signus.create_and_store_my_did(None, json.dumps({"seed": seed_trustee01}))
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    print(Colors.HEADER + "\n\t5.  Connect test\n" + Colors.ENDC)
    try:
        pool_handle = await pool.open_pool_ledger(MyVars.pool_name, None)
        MyVars.pool_handle = pool_handle
    except IndyError as E:
        MyVars.test_results["Test 4"] = False;
        print(Colors.FAIL + str(E) + Colors.ENDC)

    print(Colors.HEADER + "\n\t6.  Disconnect\n" + Colors.ENDC)
    try:
        await pool.close_pool_ledger(pool_handle)
    except IndyError as E:
        MyVars.test_results["Test 4"] = False;
        print(Colors.FAIL + str(E) + Colors.ENDC)

    print(Colors.HEADER + "\n\t7.  Reconnect\n" + Colors.ENDC)
    try:
        pool_handle = await pool.open_pool_ledger(MyVars.pool_name, None)
        MyVars.pool_handle = pool_handle
    except IndyError as E:
        MyVars.test_results["Test 4"] = False;
        print(Colors.FAIL + str(E) + Colors.ENDC)


def final_result():
    if all(value is True for value in MyVars.test_results.values()):
        print(Colors.OKGREEN + "\n\tAll the tests passed...\n" + Colors.ENDC)
    else:
        for test_num, value in MyVars.test_results.items():
            if not value:
                # print('{}: {}'.format(test_num, value))
                print('%s: ' % str(test_num) + Colors.FAIL + 'failed' + Colors.ENDC)


def test():
    test_prep()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
    loop.close()
    final_result()
