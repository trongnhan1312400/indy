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
    pool_name = "pool_genesis_test9"
    wallet_name = "test_wallet9"
    roles = ["TRUSTEE", "STEWARD", "TRUST_ANCHOR", "TGB", ""]
    test_results = {'Test 5': False, 'Test 6': False, 'Test 7': False, 'Test 8': False, 'Test 9': False,
                    'Test 10': False, 'Test 11': False, 'Test 12': False, 'Test 13': False, 'Test 14': False,
                    'Test 15': False, 'Test 16': False, 'Test 17': False, 'Test 18': False, 'Test 19': False,
                    'Test 20': False, 'Test 21': False, 'Test 22': False, 'Test 23': False, 'Test 24': False,
                    'Test 25': False, 'Test 26': False, 'Test 27': False, 'Test 28': False, 'Test 29': False,
                    'Test 30': False, 'Test 31': False}
            

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def test_prep():
    print(Colors.HEADER + "\n\tCheck if the wallet and pool for this test already exist and delete them...\n"
          + Colors.ENDC)
    import os

    os.path.expanduser('~')

    if os.path.exists(".indy/wallet/" + MyVars.wallet_name):
        try:
            shutil.rmtree(".indy/wallet/" + MyVars.wallet_name)
        except IOError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)

    if os.path.exists(".indy/pool/" + MyVars.pool_name):
        try:
            shutil.rmtree(".indy/pool/" + MyVars.pool_name)
        except IOError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)


async def add_nym(submitter_did, target_did, ver_key, alias, role, can_add):
    nym_request = await ledger.build_nym_request(submitter_did, target_did, ver_key, alias, role)
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, submitter_did, nym_request)
        if can_add:
            return True
        return False
    except IndyError as E:
        if not can_add:
            if E.error_code == 304:
                return True
        print(Colors.FAIL + str(E) + Colors.ENDC)

    return False


async def get_nym(submitter_did, target_did):
    get_nym_request = await ledger.build_get_nym_request(submitter_did, target_did)
    try:
        await ledger.submit_request(MyVars.pool_handle, get_nym_request)
        return True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return False


async def do():
    logger.info("Test Scenario 09 -> started")

    # Declare all values use in the test
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

    # 1. Create ledger config from genesis txn file.
    print(Colors.HEADER + "\n\t1.  Create Ledger\n" + Colors.ENDC)
    pool_config = json.dumps({"genesis_txn": str(MyVars.pool_genesis_txn_file)})
    try:
        await pool.create_pool_ledger_config(MyVars.pool_name, pool_config)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        sys.exit[1]

    # 2. Open pool ledger.
    print(Colors.HEADER + "\n\t2.  Open Pool Ledger\n" + Colors.ENDC)
    try:
        MyVars.pool_handle = await pool.open_pool_ledger(MyVars.pool_name, None)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        sys.exit[1]

    # 3. Create wallet.
    print(Colors.HEADER + "\n\t3.  Create Wallet\n" + Colors.ENDC)
    try:
        await wallet.create_wallet(MyVars.pool_name, MyVars.wallet_name, None, None, None)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        sys.exit[1]

    # Get wallet handle.
    try:
        MyVars.wallet_handle = await wallet.open_wallet(MyVars.wallet_name, None, None)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 4. Create DIDs.
    print(Colors.HEADER + "\n\t4.  Create DIDs\n" + Colors.ENDC)
    (default_trustee_did,
     default_trustee_verkey,
     default_trustee_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle,
                                                                json.dumps({"seed": seed_default_trustee}))

    (trustee1_did,
     trustee1_verkey,
     trustee1_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle,
                                                         json.dumps({}))

    (trustee2_did,
     trustee2_verkey,
     trustee2_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle,
                                                         json.dumps({}))

    (steward1_did,
     steward1_verkey,
     steward1_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle,
                                                         json.dumps({}))

    (steward2_did,
     steward2_verkey,
     steward2_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle,
                                                         json.dumps({}))

    (steward3_did,
     steward3_verkey,
     steward3_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle,
                                                         json.dumps({}))

    (tgb1_did,
     tgb1_verkey,
     tgb1_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle,
                                                     json.dumps({}))

    (trustanchor1_did,
     trustanchor1_verkey,
     trustanchor1_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle,
                                                             json.dumps({}))

    (trustanchor2_did,
     trustanchor2_verkey,
     trustanchor2_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle,
                                                             json.dumps({}))

    (trustanchor3_did,
     trustanchor3_verkey,
     trustanchor3_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle,
                                                             json.dumps({}))

    (user1_did,
     user1_verkey,
     user1_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

    (user2_did,
     user2_verkey,
     user2_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

    (user3_did,
     user3_verkey,
     user3_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

    (user4_did,
     user4_verkey,
     user4_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

    (user5_did,
     user5_verkey,
     user5_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

    (user6_did,
     user6_verkey,
     user6_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

    # ==========================================================================================================
    # Test starts here !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ==========================================================================================================

    # 5. Using default Trustee to create Trustee1.
    print(Colors.HEADER + "\n\t5.  Using default Trustee to create Trustee1\n" + Colors.ENDC)
    MyVars.test_results["Test 5"] = await add_nym(default_trustee_did, trustee1_did, trustee1_verkey,
                                                  None, MyVars.roles[0], can_add=True)

    # 6. Verify GET NYM.
    print(Colors.HEADER + "\n\t6.  Verify GET NYM - Trustee1\n" + Colors.ENDC)
    MyVars.test_results["Test 6"] = await get_nym(default_trustee_did, trustee1_did)

    # 7. Using Trustee1 to create Steward1.
    print(Colors.HEADER + "\n\t7.  Using Trustee1 to create Steward1\n" + Colors.ENDC)
    MyVars.test_results["Test 7"] = await add_nym(trustee1_did, steward1_did, steward1_verkey,
                                                  None, MyVars.roles[1], can_add=True)

    # 8. Verify GET NYM.
    print(Colors.HEADER + "\n\t8.  Verify GET NYM - Steward1\n" + Colors.ENDC)
    MyVars.test_results["Test 8"] = await get_nym(trustee1_did, steward1_did)

    # 9. Verify add identity (no role) by Trustee1.
    print(Colors.HEADER + "\n\t9.  Add identity (no role) by Trustee1\n" + Colors.ENDC)
    nym_txn_req3 = await ledger.build_nym_request(trustee1_did, user3_did, user3_verkey, None, None)
    try:
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, trustee1_did, nym_txn_req3)
        MyVars.test_results['Test 9'] = True
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 10. Verify GET NYM.
    print(Colors.HEADER + "\n\t10.  Verify GET NYM - no role\n" + Colors.ENDC)
    MyVars.test_results["Test 10"] = await get_nym(trustee1_did, user3_did)

    # 11. Using Trustee1 to create a TGB role.
    print(Colors.HEADER + "\n\t11.  Using Trustee1 to create a TGB role\n" + Colors.ENDC)
    MyVars.test_results["Test 11"] = await add_nym(trustee1_did, tgb1_did, tgb1_verkey,
                                                   None, MyVars.roles[3], can_add=True)

    # 12. Verify GET NYM.
    print(Colors.HEADER + "\n\t12.  Verify GET NYM - TGB1\n" + Colors.ENDC)
    MyVars.test_results["Test 12"] = await get_nym(trustee1_did, tgb1_did)

    # 13. Using Steward1 to create TrustAnchor1.
    print(Colors.HEADER + "\n\t13.  Using Steward1 to create TrustAnchor1\n" + Colors.ENDC)
    MyVars.test_results["Test 13"] = await add_nym(steward1_did, trustanchor1_did, trustanchor1_verkey,
                                                   None, MyVars.roles[2], can_add=True)

    # 14. Verify GET NYM.
    print(Colors.HEADER + "\n\t14.  Verify GET NYM - TrustAnchor1\n" + Colors.ENDC)
    MyVars.test_results["Test 14"] = await get_nym(steward1_did, trustanchor1_did)

    # 15. Verify add identity (no role) by Steward1.
    print(Colors.HEADER + "\n\t15.  Add identity (no role) by Steward1\n" + Colors.ENDC)
    MyVars.test_results["Test 15"] = await add_nym(steward1_did, user4_did, user4_verkey, None, None, can_add=True)

    # 16. Verify GET NYM.
    print(Colors.HEADER + "\n\t16.  Verify GET NYM - no role\n" + Colors.ENDC)
    MyVars.test_results["Test 16"] = await get_nym(steward1_did, user4_did)

    # 17. Verify that a Steward cannot create another Steward.
    print(Colors.HEADER + "\n\t17.  Verify Steward cannot create another Steward\n" + Colors.ENDC)
    if await add_nym(steward1_did, steward2_did, steward2_verkey, None, MyVars.roles[1], can_add=False):
        print(Colors.OKGREEN + "::PASS::Validated that a Steward cannot create a Steward!\n" + Colors.ENDC)
        MyVars.test_results["Test 17"] = True

    # 18. Verify that a Steward cannot create a Trustee.
    print(Colors.HEADER + "\n\t18.  Verify Steward cannot create a Trustee\n" + Colors.ENDC)
    if await add_nym(steward1_did, trustee1_did, trustee1_verkey, None, MyVars.roles[0], can_add=False):
        print(Colors.OKGREEN + "::PASS::Validated that a Steward cannot create a Trustee!\n" + Colors.ENDC)
        MyVars.test_results["Test 18"] = True

    # 19. Using TrustAnchor1 to add a NYM.
    print(Colors.HEADER + "\n\t19.  Using TrustAnchor1 to add a NYM\n" + Colors.ENDC)
    MyVars.test_results["Test 19"] = await add_nym(trustanchor1_did, user1_did, user1_verkey, None, None, can_add=True)

    # 20. Verify GET NYM.
    print(Colors.HEADER + "\n\t20.  Verify that new NYM added with TrustAnchor1\n" + Colors.ENDC)
    MyVars.test_results["Test 20"] = await get_nym(trustanchor1_did, user1_did)

    # 21. Verify that TrustAnchor cannot create another TrustAnchor.
    print(Colors.HEADER + "\n\t21.  Verify that TrustAnchor cannot create another TrustAnchor\n" + Colors.ENDC)
    if await add_nym(trustanchor1_did, trustanchor2_did, trustanchor2_verkey, None, MyVars.roles[2], can_add=False):
        MyVars.test_results["Test 21"] = True
        print(Colors.OKGREEN + "::PASS::Validated that a TrustAnchor cannot create another TrustAnchor!\n"
              + Colors.ENDC)

    # 22. Using default Trustee to remove new roles.
    print(Colors.HEADER + "\n\t22.  Using default Trustee to remove new roles\n" + Colors.ENDC)
    temp = await add_nym(default_trustee_did, trustee1_did, trustee1_verkey, None, MyVars.roles[4], can_add=True)
    MyVars.test_results["Test 22"] = temp
    await get_nym(default_trustee_did, trustee1_did)

    temp = await add_nym(default_trustee_did, steward1_did, steward1_verkey, None, MyVars.roles[4], can_add=True)
    MyVars.test_results["Test 22"] = MyVars.test_results["Test 22"] and temp
    await get_nym(default_trustee_did, steward1_did)

    temp = await add_nym(default_trustee_did, tgb1_did, tgb1_verkey, None, MyVars.roles[4], can_add=True)
    MyVars.test_results["Test 22"] = MyVars.test_results["Test 22"] and temp
    await get_nym(default_trustee_did, tgb1_did)

    temp = await add_nym(default_trustee_did, trustanchor1_did, trustanchor1_verkey,
                         None, MyVars.roles[4], can_add=True)
    MyVars.test_results["Test 22"] = MyVars.test_results["Test 22"] and temp
    await get_nym(default_trustee_did, trustanchor1_did)

    # 23. Verify that removed Trustee1 cannot create Trustee or Steward.
    print(Colors.HEADER + "\n\t23.  Verify that removed Trustee1 cannot create Trustee or Steward\n" + Colors.ENDC)
    temp = await add_nym(trustee1_did, trustee2_did, trustee2_verkey, None, MyVars.roles[0], can_add=False)
    if temp:
        print(Colors.OKGREEN + "::PASS::Validated that removed Trustee1 cannot create another Trustee!\n"
              + Colors.ENDC)
    MyVars.test_results["Test 23"] = temp

    temp = await add_nym(trustee1_did, steward2_did, steward2_verkey, None, MyVars.roles[1], can_add=False)
    if temp:
        print(Colors.OKGREEN + "::PASS::Validated that removed Trustee1 cannot create a Steward!\n" + Colors.ENDC)
    MyVars.test_results["Test 23"] = MyVars.test_results["Test 23"] and temp

    # 24. Verify that removed Steward1 cannot create TrustAnchor.
    print(Colors.HEADER + "\n\t24.  Verify that removed Steward1 cannot create TrustAnchor\n" + Colors.ENDC)
    if await add_nym(steward1_did, trustanchor2_did, trustanchor2_verkey, None, MyVars.roles[2], can_add=False):
        print(Colors.OKGREEN + "::PASS::Validated that removed Steward1 cannot create a TrustAnchor!\n" + Colors.ENDC)
        MyVars.test_results["Test 24"] = True

    # 25. Using default Trustee to create Trustee1.
    print(Colors.HEADER + "\n\t25.  Using default Trustee to create Trustee1\n" + Colors.ENDC)
    MyVars.test_results["Test 25"] = await add_nym(default_trustee_did, trustee1_did, trustee1_verkey,
                                                   None, MyVars.roles[0], can_add=True)

    # 26. Using Trustee1 to add Steward1 and TGB1.
    print(Colors.HEADER + "\n\t26.  Using Trustee1 to add Steward1 and TGB1\n" + Colors.ENDC)
    temp = await add_nym(trustee1_did, steward1_did, steward2_verkey, None, MyVars.roles[1], can_add=True)
    MyVars.test_results["Test 26"] = temp

    temp = await add_nym(trustee1_did, tgb1_did, tgb1_verkey, None, MyVars.roles[3], can_add=True)
    MyVars.test_results["Test 26"] = MyVars.test_results["Test 26"] and temp

    # 27. Verify that Steward1 cannot add back a TrustAnchor removed by TrustTee.
    print(Colors.HEADER + "\n\t27. Verify that Steward1 cannot add back a TrustAnchor removed by TrustTee\n"
          + Colors.ENDC)
    if await add_nym(steward1_did, trustanchor1_did, trustanchor1_verkey, None, MyVars.roles[2], can_add=False):
        print(Colors.OKGREEN + "::PASS::Validated that Steward1 cannot add back a TrustAnchor removed by TrustTee!\n"
              + Colors.ENDC)
        MyVars.test_results["Test 27"] = True

    # 28. Verify that Steward cannot remove a Trustee.
    print(Colors.HEADER + "\n\t28.  Verify that Steward cannot remove a Trustee\n" + Colors.ENDC)
    if await add_nym(steward1_did, trustee1_did, trustee1_verkey, None, MyVars.roles[4], can_add=False):
        print(Colors.OKGREEN + "::PASS::Validated that Steward cannot remove a Trustee!\n" + Colors.ENDC)
        MyVars.test_results["Test 28"] = True

    # 29. Verify that Trustee can add new Steward.
    print(Colors.HEADER + "\n\t29.  Verify that Trustee can add new Steward\n" + Colors.ENDC)
    temp = await add_nym(trustee1_did, steward2_did, steward2_verkey, None, MyVars.roles[1], can_add=True)
    MyVars.test_results["Test 29"] = temp

    temp = await add_nym(trustee1_did, steward3_did, steward3_verkey, None, MyVars.roles[1], can_add=True)
    MyVars.test_results["Test 29"] = MyVars.test_results["Test 29"] and temp

    # 30. Verify that Steward cannot remove another Steward.
    print(Colors.HEADER + "\n\t30.  Verify that Steward cannot remove another Steward\n" + Colors.ENDC)
    if await add_nym(steward1_did, steward2_did, steward2_verkey, None, MyVars.roles[4], can_add=False):
        print(Colors.OKGREEN + "::PASS::Validated that Steward cannot remove another Steward!\n" + Colors.ENDC)
        MyVars.test_results["Test 30"] = True

    # 31. Verify Steward can add a TrustAnchor.
    print(Colors.HEADER + "\n\t31.  Verify Steward can add a TrustAnchor\n" + Colors.ENDC)
    MyVars.test_results["Test 31"] = await add_nym(steward2_did, trustanchor3_did, trustanchor3_verkey,
                                                   None, MyVars.roles[3], can_add=True)

    # 32. Close pool ledger and wallet.
    print(Colors.HEADER + "\n\t32.  Close pool ledger and wallet\n" + Colors.ENDC)
    try:
        await wallet.close_wallet(MyVars.wallet_handle)
        await pool.close_pool_ledger(MyVars.pool_handle)
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 33. Delete wallet.
    print(Colors.HEADER + "\n\t33.  Delete pool ledger and wallet\n" + Colors.ENDC)
    try:
        await wallet.delete_wallet(MyVars.wallet_name, None)
        await pool.delete_pool_ledger_config(MyVars.pool_name)
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
