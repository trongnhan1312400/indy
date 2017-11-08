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
    pool_name = "test_pool11"
    wallet_name = "test_wallet11"
    debug = False
    test_results = {'Test 5': False, 'Test 6': False, 'Test 7': False, 'Test 8': False, 'Test 9': False,
                    'Test 10': False, 'Test 11': False, 'Test 12': False}


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def test_prep():
    """  Delete all files out of the .indy/pool and .indy/wallet directories  """

    import os
    print(Colors.HEADER + "\n\tCheck if the wallet and pool for this test already exist and delete them...\n"
          + Colors.ENDC)
    x = os.path.expanduser('~')
    work_dir = x + os.sep + ".indy_client"

    if os.path.exists(".indy/pool/" + MyVars.pool_name):
        try:
            shutil.rmtree(".indy/pool/" + MyVars.pool_name)
        except IOError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)

    if os.path.exists(".indy/wallet/" + MyVars.wallet_name):
        try:
            shutil.rmtree(".indy/wallet/" + MyVars.wallet_name)
        except IOError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)

    if MyVars.debug:
        input(Colors.WARNING + "Pause after test prep\n" + Colors.ENDC)


async def demo():
    logger.info("Test Scenario 11 -> started")

    # Roles and values that will be used for the test
    seed_default_trustee = "000000000000000000000000Trustee1"
    seed_trustee1 = "TestTrustAnchorTrustee1000000000"
    seed_trustee2 = "TestTrustAnchorTrustee2000000000"
    seed_steward1 = "TestTrustAnchorSteward1000000000"
    seed_steward2 = "TestTrustAnchorSteward2000000000"
    seed_trustanchor1 = "TestTrustAnchorCreateTrustAncho1"
    seed_trustanchor2 = "TestTrustAnchorCreateTrustAncho2"
    seed_trustanchor3 = "TestTrustAnchorCreateTrustAncho3"
    seed_trustanchor4 = "TestTrustAnchorCreateTrustAncho4"
    seed_user1 = "TestTrustAnchorRandomUser1000000"
    seed_user2 = "TestTrustAnchorRandomUser2000000"

    # seed_steward3 = "TestSteward300000000000000000000"
    # seed_tgb1 = "TestTGB1000000000000000000000000"
    # seed_user3 = "RandomUser3000000000000000000000"
    # seed_user4 = "RandomUser4000000000000000000000"
    # seed_user5 = "RandomUser5000000000000000000000"
    # seed_user6 = "RandomUser6000000000000000000000"
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

    await asyncio.sleep(0)
    if MyVars.debug:
        input(Colors.WARNING + "\n\nPoolHandle is %s" % str(MyVars.pool_handle) + Colors.ENDC)

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
        (trustanchor1_did, trustanchor1_verkey, trustanchor1_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({}))
        (trustanchor2_did, trustanchor2_verkey, trustanchor2_pk) = await signus.create_and_store_my_did(
            MyVars.wallet_handle, json.dumps({}))
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    if MyVars.debug:
        input(Colors.WARNING + "\n\nDID's created..." + Colors.ENDC)

    # ==================================================================================================================
    #      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Test starts here !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ==================================================================================================================

    # 5. Using the default Trustee, create a TrustAnchor and a new Trustee----------------------------------------------
    # Create a dict for the parts of this test, use this to determine if everything worked
    parts5 = {'trustee1': False, 'trusteenym': False, 'trustanchor1': False, 'trustanchor1nym': False}

    print(Colors.HEADER + "\n\t5. Use default Trustee to create a Trustee\n" + Colors.ENDC)
    nym_txn_req5 = await ledger.build_nym_request(default_trustee_did, trustee1_did, trustee1_verkey, None, roles[0])

    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did,
                                             nym_txn_req5)
        parts5['trustee1'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 5a. Verify GET_NYM for trustee1-----------------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t5a. Verify get nym for Trustee\n" + Colors.ENDC)
    get_nym_txn_req5a = await ledger.build_get_nym_request(default_trustee_did, trustee1_did)
    try:
        get_nym_txn_resp5a = await ledger.submit_request(MyVars.pool_handle, get_nym_txn_req5a)
        parts5['trusteenym'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 5b. TrustAnchor1
    print(Colors.HEADER + "\n\t5b. Use Trustee to create a TrustAnchor\n" + Colors.ENDC)
    nym_txn_req5b = await ledger.build_nym_request(default_trustee_did, trustanchor1_did, trustanchor1_verkey, None,
                                                  roles[2])
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, default_trustee_did,
                                             nym_txn_req5b)
        parts5['trustanchor1'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 5c. Verify GET_NYM for TrustAnchor1-------------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t5c. Verify get NYM for TrustAnchor\n" + Colors.ENDC)
    get_nym_txn_req5c = await ledger.build_get_nym_request(default_trustee_did, trustanchor1_did)
    try:
        get_nym_txn_resp5c = await ledger.submit_request(MyVars.pool_handle, get_nym_txn_req5c)
        parts5['trustanchor1nym'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # If any of the results are are not true, then fail the test
    if not all(value == True for value in parts5.values()):
        print(Colors.FAIL + "\n\tOne of the commands in test 5 failed" + Colors.ENDC)
    else:
        # Pass the test
        MyVars.test_results['Test 5'] = True

    if MyVars.debug:
        for k, v in parts5.items():
            print("\t\tResults for #5: ", (k, v))
        input(Colors.WARNING + "\n\nInitialized trustee1 and TrustAnchor1 and created NYMS..." + Colors.ENDC)

    await asyncio.sleep(0)

    # 6. Using the TrustAnchor create a Trustee (Trust Anchor should not be able to create Trustee) --------------------
    parts6 = {'trustee': False, 'trusteenym': False}

    print(Colors.HEADER + "\n\t6. Use TrustAnchor1 to create a Trustee\n" + Colors.ENDC)
    nym_txn_req6 = await ledger.build_nym_request(trustanchor1_did, trustee2_did, trustee2_verkey, None, roles[0])
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustanchor1_did, nym_txn_req6)
    except IndyError as E:
        if E.error_code == 304:
            parts6['trustee'] = True
            print(Colors.OKGREEN + ("::PASS::Validated that a TrustAnchor cannot add a Trustee\n"
                                    + Colors.ENDC))
        else:
            print(str(E))
            raise

    # 6a. Verify GET_NYM for new Trustee--------------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t6a. Verify get NYM for new trustee\n" + Colors.ENDC)
    get_nym_txn_req6a = await ledger.build_get_nym_request(trustanchor1_did, trustee2_did)
    try:
        get_nym_txn_resp6a = await ledger.submit_request(MyVars.pool_handle, get_nym_txn_req6a)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # The value for the NYM should be none.  This will check to make sure the result for the request is correct
    check_response_to = json.loads(get_nym_txn_resp6a)
    print(repr(check_response_to))
    if str(check_response_to["result"]["data"]) == "None":
        parts6['trusteenym'] = True

    # If any of the results are are not true, then fail the test
    if not all(value == True for value in parts6.values()):
        print(Colors.FAIL + "\n\tOne of the commands in test 6 failed" + Colors.ENDC)
    else:
        # Pass the test
        MyVars.test_results['Test 6'] = True

    if MyVars.debug:
        for k, v in parts6.items():
            print("\t\tResults for #6: ", (k, v))
        input(Colors.WARNING + "\n\nTried to create Trustee using the Trust Anchor ..." + Colors.ENDC)

    await asyncio.sleep(0)

    # 7. Verify that the TestTrustAnchorTrustee cannot create a new Steward
    print(Colors.HEADER + "\n\t7. Verify a trustee cannot create a new Steward\n" + Colors.ENDC)
    nym_txn_req7 = await ledger.build_nym_request(trustee2_did, steward2_did, steward2_verkey, None, roles[1])
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, steward2_did, nym_txn_req7)
    except IndyError as E:
        if E.error_code == 304:
            MyVars.test_results['Test 7'] = True
            print(Colors.OKGREEN + ("::PASS::Validated that a Trustee cannot create a Steward...\n" + Colors.ENDC))
        else:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            raise

    if MyVars.debug:
        input(Colors.WARNING + "\n\nSteward cannot create a steward" + Colors.ENDC)

    await asyncio.sleep(0)

    # 8. Using the TrustAnchor blacklist a Trustee (TrustAnchor should not be able to blacklist Trustee)
    # Create a dict for the parts of this test, use this to determine if everything worked
    parts8 = {'trustee1': False, 'trustee2': False}

    print(Colors.HEADER + "\n\t8. Use TrustAnchor to blacklist a Trustee\n" + Colors.ENDC)
    nym_txn_req8 = await ledger.build_nym_request(trustanchor1_did, trustee1_did, trustee1_verkey, None, roles[2])

    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustanchor1_did,
                                             nym_txn_req8)
    except IndyError as E:
        if E.error_code == 304:
            parts8['trustee1'] = True
            print(Colors.OKGREEN + ("::PASS::TrustAnchor could not blacklist a Trustee...\n" + Colors.ENDC))
        else:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            raise

    await asyncio.sleep(0)

    # 8a. Verify Trustee was not blacklisted by creating another Trustee------------------------------------------------
    print(Colors.HEADER + "\n\t8a. Verify Trustee was not blacklisted by creating another Trustee\n" + Colors.ENDC)
    get_nym_txn_req8a = await ledger.build_nym_request(trustee1_did, trustee2_did, trustee2_verkey, None, roles[0])
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustee1_did, get_nym_txn_req8a)
        parts8['trustee2'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)

    # If any of the results are are not true, then fail the test
    if not all(value == True for value in parts8.values()):
        print(Colors.FAIL + "\n\tOne of the commands in test 8 failed" + Colors.ENDC)
    else:
        # Pass the test
        MyVars.test_results['Test 8'] = True

    # 9. Using the TrustAnchor1 to create a Steward1 -----------------------------------------------------------------
    print(Colors.HEADER + "\n\t9. Use TrustAnchor1 to create a Steward2\n" + Colors.ENDC)
    nym_txn_req9 = await ledger.build_nym_request(trustanchor1_did, steward2_did, steward2_verkey, None, roles[2])
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustanchor1_did, nym_txn_req9)
    except IndyError as E:
        if E.error_code == 304:
            MyVars.test_results['Test 9'] = True
            print(Colors.OKGREEN + ("::PASS::Validated that a TrustAnchor cannot create a Steward" + Colors.ENDC))
        else:
            print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)

    # 10. Using the TrustAnchor1 blacklist Steward1 -----------------------------------------------------------------
    print(Colors.HEADER + "\n\t10. Use TrustAnchor1 to blacklist Steward1...\n" + Colors.ENDC)
    parts10 = {'setup': False, 'blacklist': False}

    # Setup:  Add Steward1 for the test
    setup_10 = await ledger.build_nym_request(trustee1_did, steward1_did, steward1_verkey, None, roles[1])
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustee1_did, setup_10)
        parts10['setup'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # Now run the test to blacklist Steward1
    nym_txn_req10 = await ledger.build_nym_request(trustanchor1_did, steward1_did, steward1_verkey, None, roles[2])
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustanchor1_did, nym_txn_req10)
    except IndyError as E:
        if E.error_code == 304:
            parts10['blacklist'] = True
            print(Colors.OKGREEN + ("::PASS::Validated that a TrustAnchor cannot blacklist a Steward" + Colors.ENDC))
        else:
            print(Colors.FAIL + str(E) + Colors.ENDC)

    # If any of the results are are not true, then fail the test
    if not all(value == True for value in parts10.values()):
        print(Colors.FAIL + "\n\tOne of the commands in test 10 failed" + Colors.ENDC)
    else:
        # Pass the test
        MyVars.test_results['Test 10'] = True

    await asyncio.sleep(0)

    # 11. Verify that a TrustAnchor1 cannot create another TrustAnchor2 -------------------------------------
    print(Colors.HEADER + "\n\t11. Verify TrustAnchor1 cannot create a TrustAnchor\n" + Colors.ENDC)
    nym_txn_req11 = await ledger.build_nym_request(trustanchor1_did, trustanchor2_did, trustanchor2_verkey, None,
                                                   roles[2])
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustanchor2_did, nym_txn_req11)
    except Exception as E:
        if E.error_code == 304:
            MyVars.test_results['Test 11'] = True
            print(Colors.OKGREEN + ("::PASS::Validated that a TrustAnchor cannot create a TrustAnchor" + Colors.ENDC))
        else:
            print(str(E))
            raise

    if MyVars.debug:
        input(Colors.WARNING + "\n\nTrustAnchor cannot create another TrustAnchor" + Colors.ENDC)

    # 12. Verify that a TrustAnchor1 cannot blacklist another TrustAnchor2 -------------------------------------
    print(Colors.HEADER + "\n\t12. Verify TrustAnchor1 cannot blacklist TrustAnchor2\n" + Colors.ENDC)
    nym_txn_req11 = await ledger.build_nym_request(trustanchor1_did, trustanchor2_did, trustanchor2_verkey, None,
                                                   roles[2])
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustanchor2_did,
                                             nym_txn_req11)
    except Exception as E:
        if E.error_code == 304:
            MyVars.test_results['Test 12'] = True
            print(
                Colors.OKGREEN + ("::PASS::Validated that a TrustAnchor cannot blacklist a TrustAnchor" + Colors.ENDC))
        else:
            print(str(E))
            raise

    if MyVars.debug:
        input(Colors.WARNING + "\n\nTrustAnchor cannot blacklist another TrustAnchor" + Colors.ENDC)

    # ==================================================================================================================
    #      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! End of test, run cleanup !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ==================================================================================================================
    # 13. Close wallet and pool ------------------------------------------------------------------------------
    print(Colors.HEADER + "\n\t==Clean up==\n\t13. Close and delete the wallet and the pool ledger...\n" + Colors.ENDC)
    try:
        await wallet.close_wallet(MyVars.wallet_handle)
        await pool.close_pool_ledger(MyVars.pool_handle)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)
    if MyVars.debug:
        input(Colors.WARNING + "\n\nClosed wallet and pool\n" + Colors.ENDC)

    # 14. Delete wallet and pool ledger --------------------------------------------------------------------
    print(Colors.HEADER + "\n\t14. Delete the wallet and pool ledger...\n" + Colors.ENDC)
    try:
        await wallet.delete_wallet(MyVars.wallet_name, None)
        await pool.delete_pool_ledger_config(MyVars.pool_name)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    await asyncio.sleep(0)
    if MyVars.debug:
        input(Colors.WARNING + "\n\nDeleted wallet and pool ledger\n" + Colors.ENDC)

    logger.info("Test Scenario 11 -> completed")


async def check_the_nym(requestor, value):
    """  Validate the nym after it is obtained  """

    # The value for the NYM should be none.  This will check to make sure the result for the request is correct
    check_response_to = json.loads(requestor)
    print(repr(check_response_to))
    if str(check_response_to["result"]["data"]) == "None":
        return True

    #     # 6a. Verify GET_NYM for new Trustee--------------------------------------------------------------------------------
    # print(Colors.HEADER + "\n\t6a. Verify get NYM for new trustee\n" + Colors.ENDC)
    # get_nym_txn_req6a = await ledger.build_get_nym_request(trustanchor1_did, trustee2_did)
    # try:
    #     get_nym_txn_resp6a = await ledger.submit_request(MyVars.pool_handle, get_nym_txn_req6a)
    # except IndyError as E:
    #     print(Colors.FAIL + str(E) + Colors.ENDC)
    #
    # # The value for the NYM should be none.  This will check to make sure the result for the request is correct
    # check_response_to = json.loads(get_nym_txn_resp6a)
    # print(repr(check_response_to))
    # if str(check_response_to["result"]["data"]) == "None":
    #     parts6['trusteenym'] = True


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
