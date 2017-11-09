import json
import sys
import logging
import os
import asyncio
import shutil
import time
from indy import pool, signus, wallet
from indy.error import IndyError
from utils.constant import Colors, Constant
from utils.report import TestReport


class MyVars:
    pool_handle = 0
    wallet_handle = 0
    pool_name = "pool_genesis_test3"
    wallet_name = "test_wallet3"
    debug = False
    test_report = TestReport("Test scenario 03: Check connection")
    test_results = {"Test 4": False, "Test 5": False, "Test 6": False}


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def test_precondition():
    print(Colors.HEADER + "\n\tCheck if the wallet and pool for this test already exist and delete them...\n" + Colors.ENDC)

    if os.path.exists(Constant.work_dir + "wallet/" + MyVars.wallet_name):
        try:
            shutil.rmtree(Constant.work_dir + "wallet/" + MyVars.wallet_name)
        except IOError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)

    if os.path.exists(Constant.work_dir + "pool/" + MyVars.pool_name):
        try:
            shutil.rmtree(Constant.work_dir + "pool/" + MyVars.pool_name)
        except IOError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)


async def test_scenario_03_check_connection():
    logger.info("Test scenario 3 -> started")

    seed_steward01 = "000000000000000000000000Steward1"
    pool_config = json.dumps({"genesis_txn": str(Constant.pool_genesis_txn_file)})

    # 1. Create pool ledger
    print(Colors.HEADER + "\n\t1.  Create pool ledger\n" + Colors.ENDC)
    try:
        await pool.create_pool_ledger_config(MyVars.pool_name, pool_config)
    except IndyError as E:
        MyVars.test_report.set_result(False)
        MyVars.test_report.set_step_status(1, "Create pool ledger", str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)
        sys.exit[1]

    # 2. Create wallet
    print(Colors.HEADER + "\n\t2. Create wallet\n" + Colors.ENDC)
    try:
        await wallet.create_wallet(MyVars.pool_name, MyVars.wallet_name, None, None, None)
    except IndyError as E:
        MyVars.test_report.set_result(False)
        MyVars.test_report.set_step_status(2, "Create wallet", str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)
        sys.exit[1]

    try:
        MyVars.wallet_handle = await wallet.open_wallet(MyVars.wallet_name, None, None)
    except IndyError as E:
        MyVars.test_report.set_result(False)
        MyVars.test_report.set_step_status(2, "Create wallet", str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 3. Create DID
    print(Colors.HEADER + "\n\t3. Create DID\n" + Colors.ENDC)
    try:
        await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({"seed": seed_steward01}))
    except IndyError as E:
        MyVars.test_report.set_result(False)
        MyVars.test_report.set_step_status(3, "Create DID", str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # ==========================================================================================================
    # Test starts here !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ==========================================================================================================

    # 4. Connect to pool.
    # Verify that the default wallet move to Test from NoEnv?
    # Cannot verify because ".indy/wallet" do not include any folder that name
    # no-env and test, and default wallet cannot be created via indy-sdk
    print(Colors.HEADER + "\n\t4.  Connect to pool\n" + Colors.ENDC)
    try:
        MyVars.pool_handle = await pool.open_pool_ledger(MyVars.pool_name, None)
        MyVars.test_results["Test 4"] = True
    except IndyError as E:
        MyVars.test_report.set_result(False)
        MyVars.test_report.set_step_status(4, "Connect to pool", str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 5. Disconnect from pool.
    print(Colors.HEADER + "\n\t5.  Disconnect from pool\n" + Colors.ENDC)
    try:
        await pool.close_pool_ledger(MyVars.pool_handle)
        MyVars.test_results["Test 5"] = True
    except IndyError as E:
        MyVars.test_report.set_result(False)
        MyVars.test_report.set_step_status(5, "Disconnect form pool", str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 6. Reconnect to pool.
    print(Colors.HEADER + "\n\t6.  Reconnect to pool\n" + Colors.ENDC)
    try:
        MyVars.pool_handle = await pool.open_pool_ledger(MyVars.pool_name, None)
        MyVars.test_results["Test 6"] = True
    except IndyError as E:
        MyVars.test_report.set_result(False)
        MyVars.test_report.set_step_status(6, "Reconnect to pool", str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    print(Colors.HEADER + "\n\t==Clean up==" + Colors.ENDC)
    # 8. Close pool ledger and wallet.
    print(Colors.HEADER + "\t8.  Close pool ledger and wallet\n" + Colors.ENDC)
    try:
        await wallet.close_wallet(MyVars.wallet_handle)
        await pool.close_pool_ledger(MyVars.pool_handle)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 9. Delete wallet.
    print(Colors.HEADER + "\n\t9.  Delete pool ledger and wallet\n" + Colors.ENDC)
    try:
        await wallet.delete_wallet(MyVars.wallet_name, None)
        await pool.delete_pool_ledger_config(MyVars.pool_name)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    logger.info("Test scenario 3 -> finished")


def final_result():
    print("\nTest result================================================" + Colors.ENDC)
    if all(value is True for value in MyVars.test_results.values()):
        print(Colors.OKGREEN + "\tAll the tests passed...\n" + Colors.ENDC)
    else:
        for test_num, value in MyVars.test_results.items():
            if not value:
                # print('{}: {}'.format(test_num, value))
                print('%s: ' % str(test_num) + Colors.FAIL + 'failed' + Colors.ENDC)


def test():
    test_precondition()

    begin_time = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_scenario_03_check_connection())
    loop.close()

    MyVars.test_report.set_duration(time.time() - begin_time)
    final_result()

    MyVars.test_report.write_result_to_file("")


test()
