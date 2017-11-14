import json
import sys
import logging
import os
import asyncio
import shutil
import time
from indy import agent, ledger, pool, signus, wallet
from indy.error import IndyError

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.constant import Constant, Colors, Roles
from utils.report import TestReport, Status


class MyVars:
    """  Needed some global variables. """

    pool_handle = 0
    # Need the path to the pool transaction file location
    begin_time = 0
    wallet_handle = 0
    pool_name = "pool_genesis_test9"
    wallet_name = "test_wallet9"
    test_results = {"Step 1": False, "Step 2": False, "Step 3": False, "Step 4": False,
                    "Step 5": False, "Step 6": False, "Step 7": True, "Step 8": False, "Step 9": False}


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def test_prep():
    print(Colors.HEADER + "\n\tCheck if the wallet and pool for this test already exist and delete them...\n"
          + Colors.ENDC)

    if os.path.exists(Constant.work_dir + "/wallet/" + MyVars.wallet_name):
        try:
            shutil.rmtree(Constant.work_dir + "/wallet/" + MyVars.wallet_name)
        except IOError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)

    if os.path.exists(Constant.work_dir + "/pool/" + MyVars.pool_name):
        try:
            shutil.rmtree(Constant.work_dir + "/pool/" + MyVars.pool_name)
        except IOError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)


async def do():
    logger.info("Step Scenario 09 -> started")

    # Declare all values use in the test
    seed_default_trustee = "000000000000000000000000Trustee1"

    # 1. Create ledger config from genesis txn file.
    print(Colors.HEADER + "\n\t1.  Create Ledger\n" + Colors.ENDC)
    pool_config = json.dumps({"genesis_txn": str(Constant.pool_genesis_txn_file)})
    try:
        await pool.create_pool_ledger_config(MyVars.pool_name, pool_config)
        MyVars.test_results["Step 1"] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return

    # 2. Open pool ledger.
    print(Colors.HEADER + "\n\t2.  Open Pool Ledger\n" + Colors.ENDC)
    try:
        MyVars.pool_handle = await pool.open_pool_ledger(MyVars.pool_name, None)
        MyVars.test_results["Step 2"] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return

    # 3. Create wallet.
    print(Colors.HEADER + "\n\t3.  Create Wallet\n" + Colors.ENDC)
    try:
        await wallet.create_wallet(MyVars.pool_name, MyVars.wallet_name, None, None, None)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return

    # Get wallet handle.
    try:
        MyVars.wallet_handle = await wallet.open_wallet(MyVars.wallet_name, None, None)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return

    MyVars.test_results["Step 3"] = True

    # 4. Create DIDs.
    print(Colors.HEADER + "\n\t4.  Create DIDs\n" + Colors.ENDC)
    try:
        (default_trustee_did,
         default_trustee_verkey,
         default_trustee_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({"seed": seed_default_trustee}))

        (trustee1_did,
         trustee1_verkey,
         trustee1_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (trustee2_did,
         trustee2_verkey,
         trustee2_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (steward1_did,
         steward1_verkey,
         steward1_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        MyVars.test_results["Step 4"] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # ==========================================================================================================
    # Test starts here !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ==========================================================================================================

    # 5. Add Trustee by default Trustee
    print(Colors.HEADER + "\n\t5.  Add Trustee by default Trustee\n" + Colors.ENDC)
    try:
        nym = await ledger.build_nym_request(default_trustee_did, trustee1_did, trustee1_verkey, None, "TRUSTEE")
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did, nym)
        MyVars.test_results["Step 5"] = True
    except IOError as E:
        print(str(E))

    # 6. Remove Trustee by default Trustee
    print(Colors.HEADER + "\n\t6. Remove Trustee by default Trustee\n" + Colors.ENDC)
    try:
        nym = await ledger.build_nym_request(default_trustee_did, trustee1_did, trustee1_verkey, None, "")
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did, nym)
        MyVars.test_results["Step 6"] = True
    except IOError as E:
        print(str(E))

    # 7. Use removed Trutee to create Steward and Trustee
    print(Colors.HEADER + "\n\t7. Use removed Trutee to create Steward and Trustee\n" + Colors.ENDC)
    try:
        nym = await ledger.build_nym_request(trustee1_did, trustee2_did, trustee2_verkey, None, "TRUSTEE")
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustee1_did, nym)
        MyVars.test_results["Step 7"] = False
    except IOError as E:
        print(str(E))

    try:
        nym = await ledger.build_nym_request(trustee1_did, steward1_did, steward1_verkey, None, "STEWARD")
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustee1_did, nym)
        MyVars.test_results["Step 7"] = False
    except IOError as E:
        print(str(E))

    # =========================================================================================
    # Clean up here
    # =========================================================================================

    # 8. Close pool ledger and wallet.
    print(Colors.HEADER + "\n\t8.  Close pool ledger and wallet\n" + Colors.ENDC)
    try:
        await wallet.close_wallet(MyVars.wallet_handle)
        await pool.close_pool_ledger(MyVars.pool_handle)
        MyVars.test_results["Step 8"] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 9. Delete wallet.
    print(Colors.HEADER + "\n\t9.  Delete pool ledger and wallet\n" + Colors.ENDC)
    try:
        await wallet.delete_wallet(MyVars.wallet_name, None)
        await pool.delete_pool_ledger_config(MyVars.pool_name)
        MyVars.test_results["Step 9"] = True
    except IndyError as E:
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
    loop.run_until_complete(do())
    loop.close()
    final_result()


test()
