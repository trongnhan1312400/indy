#! /usr/bin/env python3
import sys
import os
import asyncio
import json
import logging
import shutil
from indy import ledger, signus, wallet, pool
from indy.error import IndyError
# from .utils import get_pool_genesis_txn_path  #  import later...

# -----------------------------------------------------------------------------------------
# This will run acceptance tests that will validate the add/remove roles functionality.
# -----------------------------------------------------------------------------------------


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
    pool_name = "test_pool091"
    wallet_name = "test_wallet091"
    debug = False
    test_results = {'Test 5': False, 'Test 6': False, 'Test 7': False, 'Test 8': False, 'Test 9': False,
                    'Test 10': False, 'Test 13': False, 'Test 14': False, 'Test 15': False, 'Test 16': False,
                    'Test 17': False, 'Test 18': False, 'Test 19': False, 'Test 20': False, 'Test 21': False,
                    'Test 22': False, 'Test 23': False, 'Test 24': False, 'Test 25': False, 'Test 26': False,
                    'Test 27': False, 'Test 28': False, 'Test 29': False, 'Test 30': False, 'Test 31': False}


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def test_prep():
    """  Delete all files out of the .indy/pool and .indy/wallet directories  """

    import os
    print(Colors.HEADER + "\n\tCheck if the wallet and pool for this test already exist and delete them...\n"
          + Colors.ENDC)
    x = os.path.expanduser('~')
    work_dir = ".indy"

    if os.path.exists(work_dir + "/pool/" + MyVars.pool_name):
        try:
            shutil.rmtree(work_dir + "/pool/" + MyVars.pool_name)
        except IOError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)

    if os.path.exists(work_dir + "/wallet/" + MyVars.wallet_name):
        try:
            shutil.rmtree(work_dir + "/wallet/" + MyVars.wallet_name)
        except IOError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)

    if MyVars.debug:
        input(Colors.WARNING + "Pause after test prep\n" + Colors.ENDC)


async def demo():
    logger.info("Test Scenario 09 -> started")

    # Roles and values that will be used for the test
    seed_default_trustee = "000000000000000000000000Trustee1"
    seed_trustee1 = "TestTrustee100000000000000000000"
    seed_trustee2 = "TestTrustee200000000000000000000"
    seed_steward1 = "TestSteward100000000000000000000"
    seed_steward2 = "TestSteward200000000000000000000"
    seed_steward3 = "TestSteward300000000000000000000"
    seed_tgb1 = "TestTGB1000000000000000000000000"
    seed_trustanchor1 = "TestTrustAnchor10000000000000000"
    seed_trustanchor2 = "TestTrustAnchor20000000000000000"
    seed_trustanchor3 = "TestTrustAnchor30000000000000000"
    seed_user1 = "RandomUser1000000000000000000000"
    seed_user2 = "RandomUser2000000000000000000000"
    seed_user3 = "RandomUser3000000000000000000000"
    seed_user4 = "RandomUser4000000000000000000000"
    seed_user5 = "RandomUser5000000000000000000000"
    seed_user6 = "RandomUser6000000000000000000000"
    # pool_genesis_txn_path = get_pool_genesis_txn_path(MyVars.pool_name)  #  ...
    roles = ("TRUSTEE", "STEWARD", "TRUST_ANCHOR", "TGB", "")

    # 1. Create ledger config from genesis txn file  ---------------------------------------------------------
    print(Colors.HEADER + "\n\t1.  Create Ledger\n" + Colors.ENDC)
    pool_config = json.dumps({"genesis_txn": str(MyVars.pool_genesis_txn_file)})
    try:
        await pool.create_pool_ledger_config(MyVars.pool_name, pool_config)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        sys.exit[1]

    await asyncio.sleep(0)

    # 2. Open pool ledger -----------------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t2.  Open pool ledger\n" + Colors.ENDC)
    try:
        pool_handle = await pool.open_pool_ledger(MyVars.pool_name, None)
        MyVars.pool_handle = pool_handle
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        sys.exit(1)

    await asyncio.sleep(0)
    if MyVars.debug:
        print("\n\nPool name = " + str(MyVars.pool_name))
        input(Colors.WARNING + "\n\nPoolHandle is %s" % str(MyVars.pool_handle) + "\n\n" + Colors.ENDC)

    # 3. Create Wallet -----------------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t3. Create wallet\n" + Colors.ENDC)
    try:
        await wallet.create_wallet(MyVars.pool_name, MyVars.wallet_name, None, None, None)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        sys.exit[1]

    # Get wallet handle
    try:
        MyVars.wallet_handle = await wallet.open_wallet(MyVars.wallet_name, None, None)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)
    if MyVars.debug:
        input(Colors.WARNING + "\n\nWallet handle is %s" % str(MyVars.wallet_handle) + Colors.ENDC)

    # 4. Create DIDs - cli command = new key with seed ----------------------------------------------------
    print(Colors.HEADER + "\n\t4. Create DID's\n" + Colors.ENDC)
    try:
        # Changed to not use seeds so the test can run more than once on the same pool except for the default
        # trustee did
        (default_trustee_did, default_trustee_verkey, default_trustee_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({"seed": seed_default_trustee}))

        (trustee1_did, trustee1_verkey, trustee1_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({}))
        (trustee2_did, trustee2_verkey, trustee2_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({}))

        (steward1_did, steward1_verkey, steward1_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({}))
        (steward2_did, steward2_verkey, steward2_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({}))
        (steward3_did, steward3_verkey, steward3_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({}))

        (tgb1_did, tgb1_verkey, tgb1_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({}))

        (trustanchor1_did, trustanchor1_verkey, trustanchor1_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({}))
        (trustanchor2_did, trustanchor2_verkey, trustanchor2_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({}))
        (trustanchor3_did, trustanchor3_verkey, trustanchor3_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({}))

        (user1_did, user1_verkey, user1_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({}))
        (user2_did, user2_verkey, user2_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({}))
        (user3_did, user3_verkey, user3_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({}))
        (user4_did, user4_verkey, user4_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({}))
        (user5_did, user5_verkey, user5_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({}))
        (user6_did, user6_verkey, user6_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({}))
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    if MyVars.debug:
        input(Colors.WARNING + "\n\nDID's created..." + Colors.ENDC)

    # ==========================================================================================================
    # Test starts here !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ==========================================================================================================
    # 5. Initialize Trustee1 -----------------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t5. Initialize Trustee1\n" + Colors.ENDC)
    nym_txn_req1 = await ledger.build_nym_request(default_trustee_did, trustee1_did, trustee1_verkey, None, roles[0])

    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did,
                                             nym_txn_req1)
        MyVars.test_results['Test 5'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 6. Verify GET_NYM -----------------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t6. Verify get nym for trustee1\n" + Colors.ENDC)
    get_nym_txn_req1 = await ledger.build_get_nym_request(default_trustee_did, trustee1_did)
    try:
        get_nym_txn_resp1 = await ledger.submit_request(MyVars.pool_handle, get_nym_txn_req1)
        MyVars.test_results['Test 6'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    if MyVars.debug:
        input(Colors.WARNING + "\n\nInitialized trustee1 and created nym..." + Colors.ENDC)

    # 7. Using Trustee1 create a Steward1 -----------------------------------------------------------------
    print(Colors.HEADER + "\n\t7. Use Trustee1 to create Steward1\n" + Colors.ENDC)
    nym_txn_req2 = await ledger.build_nym_request(trustee1_did, steward1_did, steward1_verkey, None, roles[1])
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustee1_did, nym_txn_req2)
        MyVars.test_results['Test 7'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 8. Verify GET_NYM -----------------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t8. Verify get nym for Steward1\n" + Colors.ENDC)
    get_nym_txn_req2 = await ledger.build_get_nym_request(trustee1_did, steward1_did)
    try:
        get_nym_txn_resp2 = await ledger.submit_request(MyVars.pool_handle, get_nym_txn_req2)
        MyVars.test_results['Test 8'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    if MyVars.debug:
        input(Colors.WARNING + "\n\nCreated steward1 and a nym..." + Colors.ENDC)

    # 9. Verify add identity (no role) by Trustee1 ---------------------------------------------------------
    print(Colors.HEADER + "\n\t9. Use Trustee1 to add identity - no role\n" + Colors.ENDC)
    nym_txn_req3 = await ledger.build_nym_request(trustee1_did, user3_did, user3_verkey, None, None)
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustee1_did, nym_txn_req3)
        MyVars.test_results['Test 9'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 10. Verify GET_NYM  -----------------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t10. Verify get nym - no role\n" + Colors.ENDC)
    get_nym_txn_req3 = await ledger.build_get_nym_request(trustee1_did, user3_did)
    try:
        get_nym_txn_resp3 = await ledger.submit_request(MyVars.pool_handle, get_nym_txn_req3)
        MyVars.test_results['Test 10'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    if MyVars.debug:
        input(Colors.WARNING + "\n\nVerify added identity and get the nym..." + Colors.ENDC)

    # # 11. Using Trustee1 create a TGB1
    # print(Colors.HEADER + "\n\tUse Trustee1 to create TGB1\n" + Colors.ENDC)
    # nym_txn_req4 = await ledger.build_nym_request(trustee1_did, tgb1_did, tgb1_verkey, None, roles[3])
    # await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustee1_did, nym_txn_req4)

    # # 12. Verify GET_NYM
    # print(Colors.HEADER + "\n\t12. Get nyms for TGB1\n" + Colors.ENDC)
    # get_nym_txn_req4 = await ledger.build_get_nym_request(trustee1_did, tgb1_did)
    # get_nym_txn_resp4 = await ledger.submit_request(MyVars.pool_handle, get_nym_txn_req4)
    # print(get_nym_txn_resp4)

    # 13. Using Steward1 create a TrustAnchor1 -------------------------------------------------------------
    print(Colors.HEADER + "\n\t13. Use Steward1 to create Trustanchor1\n" + Colors.ENDC)
    nym_txn_req5 = await ledger.build_nym_request(steward1_did, trustanchor1_did, trustanchor1_verkey, None, roles[2])
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, steward1_did, nym_txn_req5)
        MyVars.test_results['Test 13'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 14. Verify GET_NYM -----------------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t14. Verify get nym - Trustanchor1\n" + Colors.ENDC)
    get_nym_txn_req5 = await ledger.build_get_nym_request(steward1_did, trustanchor1_did)
    try:
        get_nym_txn_resp5 = await ledger.submit_request(MyVars.pool_handle, get_nym_txn_req5)
        MyVars.test_results['Test 14'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    if MyVars.debug:
        input(Colors.WARNING + "\n\nUse steward1 to create trustanchor1, get the nym" + Colors.ENDC)

    # 15. Verify add identity (no role) by Steward1 --------------------------------------------------------
    print(Colors.HEADER + "\n\t15. Add identity -no role - by Steward1\n" + Colors.ENDC)
    nym_txn_req6 = await ledger.build_nym_request(steward1_did, user4_did, user4_verkey, None, None)
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, steward1_did, nym_txn_req6)
        MyVars.test_results['Test 15'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    if MyVars.debug:
        input(Colors.WARNING + "\n\nVerified add identity (no role) by Steward1" + Colors.ENDC)

    # 16. Verify GET_NYM for user -no role- ---------------------------------------------------------------
    print(Colors.HEADER + "\n\t16. Verify get nym for user4\n" + Colors.ENDC )
    get_nym_txn_req6 = await ledger.build_get_nym_request(steward1_did, user4_did)
    try:
        get_nym_txn_resp6 = await ledger.submit_request(MyVars.pool_handle, get_nym_txn_req6)
        MyVars.test_results['Test 16'] = True
    except Exception as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    if MyVars.debug:
        print("Pool Handle = ", str(MyVars.pool_handle))
        print("Pool name = ", str(MyVars.pool_name))
        input(Colors.WARNING + "\n\nAdd no role by steward, get the nym" + Colors.ENDC)

    # 17. Verify that a Steward1 cannot create a Steward2 --------------------------------------------------
    print(Colors.HEADER + "\n\t17. Verify Steward1 cannot create a new Steward\n" + Colors.ENDC)
    try:
        nym_txn_req7 = await ledger.build_nym_request(steward1_did, steward2_did, steward2_verkey, None, roles[1])
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, steward1_did, nym_txn_req7)
    except Exception as E:
        if E.error_code == 304:
            MyVars.test_results['Test 17'] = True
            print(Colors.OKGREEN + ("::PASS::Validated that a steward cannot create a steward...\n" + Colors.ENDC))
        else:
            print(str(E))
            raise

    if MyVars.debug:
        input(Colors.WARNING + "\n\nSteward cannot create a steward" + Colors.ENDC)

    # 18. Verify that a Steward1 cannot create a Trustee2 --------------------------------------------------
    print(Colors.HEADER + "\n\t18. Verify a Steward cannot create a Trustee\n" + Colors.ENDC)
    try:
        nym_txn_req8 = await ledger.build_nym_request(steward1_did, trustee2_did, trustee2_verkey, None, roles[0])
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, steward1_did, nym_txn_req8)
    except Exception as E:
        if E.error_code == 304:
            MyVars.test_results['Test 18'] = True
            print(Colors.OKGREEN + ("::PASS::Validated that a steward cannot create a trustee...\n" + Colors.ENDC))
        else:
            print(str(E))
            raise

    if MyVars.debug:
        input(Colors.WARNING + "\n\nSteward cannot create a trustee" + Colors.ENDC)

    # 19. Using the TrustAnchor1 add a NYM -----------------------------------------------------------------
    print(Colors.HEADER + "\n\t19. Use TrustAnchor1 to add a nym\n" + Colors.ENDC)
    nym_txn_req9 = await ledger.build_nym_request(trustanchor1_did, user1_did, user1_verkey, None, None)
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustanchor1_did, nym_txn_req9)
        MyVars.test_results['Test 19'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 20. Verify GET_NYM -----------------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t20. Verify new nym added with TrustAnchor1\n" + Colors.ENDC)
    get_nym_txn_req9 = await ledger.build_get_nym_request(trustanchor1_did, user1_did)
    try:
        get_nym_txn_resp9 = await ledger.submit_request(MyVars.pool_handle, get_nym_txn_req9)
        MyVars.test_results['Test 20'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    if MyVars.debug:
        input(Colors.WARNING + "\n\nTustanchor add a nym, get the nym" + Colors.ENDC)

    await asyncio.sleep(0)

    # 21. Verify that a TrustAnchor1 cannot create another TrustAnchor2 -------------------------------------
    print(Colors.HEADER + "\n\t21. Verify TrustAnchor1 cannot create a TrustAnchor\n" + Colors.ENDC)
    try:
        nym_txn_req10 = await ledger.build_nym_request(trustanchor1_did, trustanchor2_did, trustanchor2_verkey, None,
                                                       roles[2])
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustanchor2_did, nym_txn_req10)
    except Exception as E:
        if E.error_code == 304:
            MyVars.test_results['Test 21'] = True
            print(Colors.OKGREEN + ("::PASS::Validated that a TrustAnchor cannot create a TrustAnchor" + Colors.ENDC))
        else:
            print(str(E))
            raise

    if MyVars.debug:
        input(Colors.WARNING + "\n\nTrustAnchor cannot create another TrustAnchor" + Colors.ENDC)

    # 22. Using default Trustee remove the new roles --------------------------------------------------------
    print(Colors.HEADER + "\n\t22. Use default Trustee to remove roles\n" + Colors.ENDC)

    # Create a dict for the parts of this test, use this to determine if everything worked
    parts22 = {'req22a': False, 'req22b': False, 'req22c': False, 'req22d': False}

    nym_txn_req11 = await ledger.build_nym_request(default_trustee_did, trustee1_did, trustee1_verkey, None, None)

    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did,
                                             nym_txn_req11)
        parts22['req22a'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    nym_txn_req12 = await ledger.build_nym_request(default_trustee_did, steward1_did, steward1_verkey, None, roles[4])
    get_nym_txn = await ledger.build_get_nym_request(default_trustee_did, trustee1_did)

    try:
        get_nym_txn2 = await ledger.submit_request(MyVars.pool_handle, get_nym_txn)
    except IndyError as E:
        print(str(E))

    if MyVars.debug:
        print(30*"=")
        print("\n" + get_nym_txn2)
        stringToJson = json.loads(get_nym_txn2)
        getNYMData = stringToJson['result']['data']
        stringToJson2 = json.loads(getNYMData)
        print("\nGetnymdata: " + repr(getNYMData))
        print("\n\tRole: " + repr(stringToJson2['role']))
        print(30 * "=")

    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did,
                                             nym_txn_req12)
        parts22['req22b'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    get_nym_txn2 = await ledger.build_get_nym_request(default_trustee_did, steward1_did)

    try:
        get_nym_txn2a = await ledger.submit_request(MyVars.pool_handle, get_nym_txn2)
    except IndyError as E:
        print(str(E))

    await asyncio.sleep(0)

    nym_txn_req13 = await ledger.build_nym_request(default_trustee_did, tgb1_did, tgb1_verkey, None, roles[4])
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did,
                                             nym_txn_req13)
        parts22['req22c'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    nym_txn_req14 = await ledger.build_nym_request(default_trustee_did, trustanchor1_did, trustanchor1_verkey, None,
                                                   roles[4])
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did,
                                             nym_txn_req14)
        parts22['req22d'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)

    # If any of the results are are not true, then fail the test
    if not all(value == True for value in parts22.values()):
        print(Colors.FAIL + "\n\tOne of the commands in test 22 failed" + Colors.ENDC)
    else:
        # Pass the test
        MyVars.test_results['Test 22'] = True

    if MyVars.debug:
        input(Colors.WARNING + "\n\nDefault trustee - removed new roles" + Colors.ENDC)

    await asyncio.sleep(0)

    # 23. See if the removed TestTrustee1 can create a new Trustee or Steward ---------------------------
    print(Colors.HEADER + "\n\t23. Can the removed Trustee1 create a Trustee or Steward\n" + Colors.ENDC)
    # Create a dict for the parts of this test, use this to determine if everything worked
    parts23 = {'trustee': False, 'steward': False}

    try:
        nym_txn_req15 = await ledger.build_nym_request(trustee1_did, trustee2_did, trustee2_verkey, None, roles[0])
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustee1_did, nym_txn_req15)
    except Exception as E:
        if E.error_code == 304:
            parts23['trustee'] = True
            print(Colors.OKGREEN + ("::PASS::The removed Trustee1 cannot create a trustee" + Colors.ENDC))
        else:
            print(str(E))
            raise

    await asyncio.sleep(0)

    try:
        nym_txn_req16 = await ledger.build_nym_request(trustee1_did, steward2_did, steward2_verkey, None, roles[1])
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustee1_did, nym_txn_req16)
    except Exception as E:
        if E.error_code == 304:
            parts23['steward'] = True
            print(Colors.OKGREEN + ("::PASS::The removed Trustee1 cannot create a steward" + Colors.ENDC))
        else:
            print(str(E))
            raise

    await asyncio.sleep(0)

    # If any of the results are are not true, then fail the test
    if not all(value == True for value in parts23.values()):
        print(Colors.FAIL + "\n\tOne of the commands in test 23 failed" + Colors.ENDC)
    else:
        # Pass the test
        MyVars.test_results['Test 23'] = True
    if MyVars.debug:
        input(Colors.WARNING + "\n\nTestTrustee1, create new trustee or steward" + Colors.ENDC)

    # 24. See if the removed TestSteward1 can create a new Trust_Anchor ---------------------------------
    print(Colors.HEADER + "\n\t24. Can removed Steward1 create a new TrustAnchor?\n" + Colors.ENDC)
    try:
        nym_txn_req17 = await ledger.build_nym_request(steward1_did, trustanchor2_did, trustanchor2_verkey, None,
                                                       roles[2])
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, steward1_did, nym_txn_req17)
    except Exception as E:
        if E.error_code == 304:
            MyVars.test_results['Test 24'] = True
            print(Colors.OKGREEN + ("::PASS::Validated that a removed TestSteward1 cannot create a new TrustAnchor\n"
                                    + Colors.ENDC))
        else:
            print(str(E))
            raise

    if MyVars.debug:
        input(Colors.WARNING + "\n\nDeleted teststeward cannot create a new trust anchor..." + Colors.ENDC)

    # 25. Using the default Trustee add TestTrustee1 -----------------------------------------------------
    print(Colors.HEADER + "\n\t25. Use default trustee to create TestTrustee1\n" + Colors.ENDC)
    nym_txn_req18 = await ledger.build_nym_request(default_trustee_did, trustee1_did, trustee1_verkey, None, roles[0])
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did,
                                             nym_txn_req18)
        MyVars.test_results['Test 25'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 26. Using the Trustee1 add Steward1 and TestTGB1 -------------------------------------------
    print(Colors.HEADER + "\n\t26. Use TestTrustee1 to add TestSteward1 ...\n" + Colors.ENDC)
    nym_txn_req19 = await ledger.build_nym_request(trustee1_did, steward1_did, steward1_verkey, None, roles[1])
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustee1_did, nym_txn_req19)
        MyVars.test_results['Test 26'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # nym_txn_req20 = await ledger.build_nym_request(trustee1_did, tgb1_did, tgb1_verkey, None, roles[3])
    # await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustee1_did, nym_txn_req20)

    if MyVars.debug:
        input(Colors.WARNING + "\n\nUse default trustee..." + Colors.ENDC)

    # 27. Verify that Steward1 cannot add back a Trust_Anchor that a Trustee removed ------------------------
    print(Colors.HEADER + "\n\t27. Verify Steward1 cannot add back a TrustAnchor (a Trustee)that was removed...\n"
          + Colors.ENDC)
    try:
        nym_txn_req21 = await ledger.build_nym_request(steward1_did, trustanchor1_did, trustanchor1_verkey, None,
                                                       roles[2])
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, steward1_did, nym_txn_req21)
    except Exception as E:
        if E.error_code == 304:
            MyVars.test_results['Test 27'] = True
            print(Colors.OKGREEN + ("::PASS::Steward1 cannot add back a TrustAnchor (trustee) that was removed\n"
                                    + Colors.ENDC))
        else:
            print(str(E))
            raise

    await asyncio.sleep(0)

    # 28. Verify that Steward cannot remove a Trustee --------------------------------------------------------
    print(Colors.HEADER + "\n\t28. Verify a Steward cannot remove a Trustee\n" + Colors.ENDC)
    try:
        nym_txn_req22 = await ledger.build_nym_request(steward1_did, trustee1_did, trustee1_verkey, None, roles[4])
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, steward1_did, nym_txn_req22)
    except Exception as E:
        if E.error_code == 304:
            MyVars.test_results['Test 28'] = True
            print(Colors.OKGREEN + ("::PASS::Verified a Steward cannot remove a Trustee\n"
                                    + Colors.ENDC))
        else:
            print(str(E))
            raise

    # 29. To verify see if the Trustee can add a new Stewards ------------------------------------------------
    print(Colors.HEADER + "\n\t29.  Verify the Trustee can add new Stewards\n" + Colors.ENDC)
    parts29 = {'req29a': False, 'req29b': False}
    nym_txn_req23 = await ledger.build_nym_request(trustee1_did, steward2_did, steward2_verkey, None, roles[1])
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustee1_did, nym_txn_req23)
        parts29['req29a'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    nym_txn_req24 = await ledger.build_nym_request(trustee1_did, steward3_did, steward3_verkey, None, roles[1])
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustee1_did, nym_txn_req24)
        parts29['req29b'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # If any of the results are are not true, then fail this specific test
    if not all(value == True for value in parts29.values()):
        print(Colors.FAIL + "\n\tOne of the commands in test 28 failed" + Colors.ENDC)
    else:
        # Pass the test
        MyVars.test_results['Test 29'] = True

    # 30. Verify that Steward1 cannot remove Steward2 -------------------------------------------------------
    print(Colors.HEADER + "\n\t30. Verify the Steward1 cannot remove other Stewards (Steward2)\n" + Colors.ENDC)
    try:
        nym_txn_req25 = await ledger.build_nym_request(steward1_did, steward2_did, steward2_verkey, None, roles[4])
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, steward1_did, nym_txn_req25)
    except Exception as E:
        if E.error_code == 304:
            MyVars.test_results['Test 30'] = True
            print(Colors.OKGREEN + ("::PASS::Validated that a Steward1 cannot remove other Stewards (Steward2)\n"
                                    + Colors.ENDC))
        else:
            print(str(E))
            raise

    # 31. To verify see if the Steward can add a new Trust Anchor -------------------------------------------
    print(Colors.HEADER + "\n\t31. Verify the Steward can add a new TrustAnchor\n" + Colors.ENDC)
    nym_txn_req26 = await ledger.build_nym_request(steward2_did, trustanchor3_did, trustanchor3_verkey, None, roles[2])
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, steward2_did, nym_txn_req26)
        MyVars.test_results['Test 31'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)
    if MyVars.debug:
        input(Colors.WARNING + "\n\nCheck various scenarios for deleting and creating roles using valid and "
                               "invalid roles" + Colors.ENDC)

    # 32. Delete the DID's used in this test
    # await ledger.------------------------------------------------------------------------------------??

    # 32. Close wallet and pool ------------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t==Clean up==\n\t32. Close and delete the wallet and the pool ledger...\n" + Colors.ENDC)
    try:
        await wallet.close_wallet(MyVars.wallet_handle)
        await pool.close_pool_ledger(MyVars.pool_handle)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)
    if MyVars.debug:
        input(Colors.WARNING + "\n\nClosed wallet and pool\n" + Colors.ENDC)

    # 33. Delete wallet and pool ledger --------------------------------------------------------------------
    print(Colors.HEADER + "\n\t33. Delete the wallet and pool ledger...\n" + Colors.ENDC)
    try:
        await wallet.delete_wallet(MyVars.wallet_name, None)
        await pool.delete_pool_ledger_config(MyVars.pool_name)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)
    if MyVars.debug:
        input(Colors.WARNING + "\n\nDeleted wallet and pool ledger\n" + Colors.ENDC)

    logger.info("Test Scenario 09 -> completed")


# async def check_the_nym(requestor, target):
#     """  Validate the nym after it is obtained  """
#
#     get_nym_txn = await ledger.build_get_nym_request(requestor, target)
#
#     try:
#         nym = await ledger.submit_request(MyVars.pool_handle, get_nym_txn)
#     except IndyError as E:
#         print(Colors.FAIL + str(E) + Colors.ENDC)
#
#     print(Colors.HEADER + "\n\n\tThe nym is : " + repr(nym) + Colors.ENDC)


def final_results():
    """  Show the test results  """

    if all(value == True for value in MyVars.test_results.values()):
        print(Colors.OKGREEN + "\n\tAll the tests passed...\n" + Colors.ENDC)
    else:
        for test_num, value in MyVars.test_results.items():
            if not value:
                # print('{}: {}'.format(test_num, value))
                print('%s: ' % str(test_num) + Colors.FAIL + 'failed' + Colors.ENDC)


# Run the cleanup first...
test_prep()

# Create the loop instance using asyncio
loop = asyncio.get_event_loop()
loop.run_until_complete(demo())
loop.close()

print("\n\nResults\n+" + 40*"=" + "+")
final_results()

