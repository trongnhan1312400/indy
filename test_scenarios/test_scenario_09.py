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
    test_report = TestReport("Test_Scenario_09_Remove_And_Add_Role")
    # Need the path to the pool transaction file location
    begin_time = 0
    wallet_handle = 0
    pool_name = "pool_genesis_test9"
    wallet_name = "test_wallet9"
    test_results = {"Step 1": False, "Step 2": False, "Step 3": False, "Step 4": False,
                    "Step 5": False, "Step 6": False, "Step 7": False, "Step 8": False, "Step 9": False,
                    "Step 10": False, "Step 13": False, "Step 14": False,
                    "Step 15": False, "Step 16": False, "Step 17": False, "Step 18": False, "Step 19": False,
                    "Step 20": False, "Step 21": False, "Step 22": False, "Step 23": False, "Step 24": False,
                    "Step 25": False, "Step 26": False, "Step 27": False, "Step 28": False, "Step 29": False,
                    "Step 30": False, "Step 31": False, "Step 32": False, "Step 33": False}
            

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


async def add_nym(submitter_did, target_did, ver_key, alias, role, can_add):
    result = False
    e = None
    try:
        nym_request = await ledger.build_nym_request(submitter_did, target_did, ver_key, alias, role)
        await ledger.sign_and_submit_request(MyVars.pool_handle, MyVars.wallet_handle, submitter_did, nym_request)
        if can_add:
            result = True
    except IndyError as E:
        if not can_add:
            if E.error_code == 304:
                result = True
        else:
            e = str(E)
            print(Colors.FAIL + e + Colors.ENDC)

    return result, e


async def get_nym(submitter_did, target_did):
    try:
        get_nym_request = await ledger.build_get_nym_request(submitter_did, target_did)
        await ledger.submit_request(MyVars.pool_handle, get_nym_request)
        return True, None
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return False, str(E)


async def test_09_remove_and_add_role():
    logger.info("Step Scenario 09 -> started")

    # Declare all values use in the test
    seed_default_trustee = "000000000000000000000000Trustee1"

    # 1. Create ledger config from genesis txn file.
    print(Colors.HEADER + "\n\t1.  Create Ledger\n" + Colors.ENDC)
    pool_config = json.dumps({"genesis_txn": str(Constant.pool_genesis_txn_file)})
    try:
        await pool.create_pool_ledger_config(MyVars.pool_name, pool_config)
        MyVars.test_results["Step 1"] = True
        MyVars.test_report.set_step_status("Step01. Create Ledger", Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step01. Create Ledger", Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return

    # 2. Open pool ledger.
    print(Colors.HEADER + "\n\t2.  Open Pool Ledger\n" + Colors.ENDC)
    try:
        MyVars.pool_handle = await pool.open_pool_ledger(MyVars.pool_name, None)
        MyVars.test_results["Step 2"] = True
        MyVars.test_report.set_step_status("Step02. Open pool ledger", Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step02. Open pool ledger", Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return

    # 3. Create wallet.
    print(Colors.HEADER + "\n\t3.  Create Wallet\n" + Colors.ENDC)
    try:
        await wallet.create_wallet(MyVars.pool_name, MyVars.wallet_name, None, None, None)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step03. Create wallet", Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return

    # Get wallet handle.
    try:
        MyVars.wallet_handle = await wallet.open_wallet(MyVars.wallet_name, None, None)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step03. Create wallet", Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)
        return

    MyVars.test_results["Step 3"] = True
    MyVars.test_report.set_step_status("Step03. Create wallet", Status.PASSED)

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

        (steward2_did,
         steward2_verkey,
         steward2_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (steward3_did,
         steward3_verkey,
         steward3_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (tgb1_did,
         tgb1_verkey,
         tgb1_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (trustanchor1_did,
         trustanchor1_verkey,
         trustanchor1_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (trustanchor2_did,
         trustanchor2_verkey,
         trustanchor2_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

        (trustanchor3_did,
         trustanchor3_verkey,
         trustanchor3_pk) = await signus.create_and_store_my_did(MyVars.wallet_handle, json.dumps({}))

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
        MyVars.test_results["Step 4"] = True
        MyVars.test_report.set_step_status("Step04. Create DID", Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step04. Create DID", Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # ==========================================================================================================
    # Test starts here !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ==========================================================================================================

    # 5. Using default Trustee to create Trustee1.
    print(Colors.HEADER + "\n\t5.  Using default Trustee to create Trustee1\n" + Colors.ENDC)
    (MyVars.test_results["Step 5"], message) = await add_nym(default_trustee_did, trustee1_did, trustee1_verkey,
                                                             None, Roles.TRUSTEE, can_add=True)
    if MyVars.test_results["Step 5"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step05. Using default Trustee to create Trustee1",
                                           Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status("Step05. Using default Trustee to create Trustee1", Status.PASSED)

    # 6. Verify GET NYM.
    print(Colors.HEADER + "\n\t6.  Verify GET NYM - Trustee1\n" + Colors.ENDC)
    (MyVars.test_results["Step 6"], message) = await get_nym(default_trustee_did, trustee1_did)

    if MyVars.test_results["Step 6"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step06. Verify GET NYM - Trustee1", Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status("Step06. Verify GET NYM - Trustee1", Status.PASSED)

    # 7. Using Trustee1 to create Steward1.
    print(Colors.HEADER + "\n\t7.  Using Trustee1 to create Steward1\n" + Colors.ENDC)
    (MyVars.test_results["Step 7"], message) = await add_nym(trustee1_did, steward1_did, steward1_verkey,
                                                             None, Roles.STEWARD, can_add=True)

    if MyVars.test_results["Step 7"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step07. Using Trustee1 to create Steward1", Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status("Step07. Using Trustee1 to create Steward1", Status.PASSED)

    # 8. Verify GET NYM.
    print(Colors.HEADER + "\n\t8.  Verify GET NYM - Steward1\n" + Colors.ENDC)
    (MyVars.test_results["Step 8"], message) = await get_nym(trustee1_did, steward1_did)

    if MyVars.test_results["Step 8"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step08. Verify GET NYM - Steward1", Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status("Step08. Verify GET NYM - Steward1", Status.PASSED)

    # 9. Verify add identity (no role) by Trustee1.
    print(Colors.HEADER + "\n\t9.  Add identity (no role) by Trustee1\n" + Colors.ENDC)
    (MyVars.test_results["Step 9"], message) = await add_nym(trustee1_did, user3_did, user3_verkey,
                                                             None, None, can_add=True)

    if MyVars.test_results["Step 9"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step09. Add identity (no role) by Trustee1", Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status("Step09. Add identity (no role) by Trustee1", Status.PASSED)

    # 10. Verify GET NYM.
    print(Colors.HEADER + "\n\t10.  Verify GET NYM - no role\n" + Colors.ENDC)
    (MyVars.test_results["Step 10"], message) = await get_nym(trustee1_did, user3_did)

    if MyVars.test_results["Step 10"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step10. Verify GET NYM - no role", Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status("Step10. Verify GET NYM - no role", Status.PASSED)

    # Role TGB is not exist so we do not execute step 11.
    # 11. Using Trustee1 to create a TGB role.
    # print(Colors.HEADER + "\n\t11.  Using Trustee1 to create a TGB role\n" + Colors.ENDC)
    # (MyVars.test_results["Step 11"], message) = await add_nym(trustee1_did, tgb1_did, tgb1_verkey,
    #                                                           None, Roles.TGB, can_add=True)
    #
    # if MyVars.test_results["Step 11"] is False:
    #     MyVars.test_report.set_test_failed()
    #     MyVars.test_report.set_step_status("Step11. Using Trustee1 to create a TGB role", str(message))

    MyVars.test_report.set_step_status("Step11. Using Trustee1 to create a TGB role (SKIP)")

    # Role TGB is not exist so we do not execute step 12.
    # 12. Verify GET NYM.
    # print(Colors.HEADER + "\n\t12.  Verify GET NYM - TGB1\n" + Colors.ENDC)
    # (MyVars.test_results["Step 12"], message) = await get_nym(trustee1_did, tgb1_did)
    #
    # if MyVars.test_results["Step 12"] is False:
    #     MyVars.test_report.set_test_failed()
    #     MyVars.test_report.set_step_status("Step12. Verify GET NYM - TGB1", str(message))
    MyVars.test_report.set_step_status("Step12. Verify GET NYM - TGB1 (SKIP)")

    # 13. Using Steward1 to create TrustAnchor1.
    print(Colors.HEADER + "\n\t13.  Using Steward1 to create TrustAnchor1\n" + Colors.ENDC)
    (MyVars.test_results["Step 13"], message) = await add_nym(steward1_did, trustanchor1_did, trustanchor1_verkey,
                                                              None, Roles.TRUST_ANCHOR, can_add=True)

    if MyVars.test_results["Step 13"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step13. Using Steward1 to create TrustAnchor1",
                                           Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status("Step13. Using Steward1 to create TrustAnchor1", Status.PASSED)

    # 14. Verify GET NYM.
    print(Colors.HEADER + "\n\t14.  Verify GET NYM - TrustAnchor1\n" + Colors.ENDC)
    (MyVars.test_results["Step 14"], message) = await get_nym(steward1_did, trustanchor1_did)

    if MyVars.test_results["Step 14"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step14. Verify GET NYM - TrustAnchor1", Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status("Step14. Verify GET NYM - TrustAnchor1", Status.PASSED)

    # 15. Verify add identity (no role) by Steward1.
    print(Colors.HEADER + "\n\t15.  Add identity (no role) by Steward1\n" + Colors.ENDC)
    (MyVars.test_results["Step 15"], message) = await add_nym(steward1_did, user4_did, user4_verkey,
                                                              None, None, can_add=True)

    if MyVars.test_results["Step 15"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step15. Add identity (no role) by Steward1", Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status("Step15. Add identity (no role) by Steward1", Status.PASSED)

    # 16. Verify GET NYM.
    print(Colors.HEADER + "\n\t16.  Verify GET NYM - no role\n" + Colors.ENDC)
    (MyVars.test_results["Step 16"], message) = await get_nym(steward1_did, user4_did)

    if MyVars.test_results["Step 16"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step16. Verify GET NYM - no role", Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status("Step16. Verify GET NYM - no role", Status.PASSED)

    # 17. Verify that a Steward cannot create another Steward.
    print(Colors.HEADER + "\n\t17.  Verify Steward cannot create another Steward\n" + Colors.ENDC)
    (temp, message) = await add_nym(steward1_did, steward2_did, steward2_verkey, None, Roles.STEWARD, can_add=False)

    if temp:
        print(Colors.OKGREEN + "::PASS::Validated that a Steward cannot create a Steward!\n" + Colors.ENDC)
        MyVars.test_results["Step 17"] = True
        MyVars.test_report.set_step_status("Step17. Verify that a Steward cannot create another Steward",
                                           Status.PASSED)
    else:
        MyVars.test_report.set_test_failed()
        if message is None:
            message = "Steward can create another Steward (should fail)"
        MyVars.test_report.set_step_status("Step17. Verify that a Steward cannot create another Steward",
                                           Status.FAILED, str(message))

    # 18. Verify that a Steward cannot create a Trustee.
    print(Colors.HEADER + "\n\t18.  Verify Steward cannot create a Trustee\n" + Colors.ENDC)
    (temp, message) = await add_nym(steward1_did, trustee1_did, trustee1_verkey, None, Roles.TRUSTEE, can_add=False)

    if temp:
        print(Colors.OKGREEN + "::PASS::Validated that a Steward cannot create a Trustee!\n" + Colors.ENDC)
        MyVars.test_results["Step 18"] = True
        MyVars.test_report.set_step_status("Step18. Verify that a Steward cannot create a Trustee",
                                           Status.PASSED)
    else:
        MyVars.test_report.set_test_failed()
        if message is None:
            message = "Steward can create a Trustee (should fail)"
        MyVars.test_report.set_step_status("Step18. Verify that a Steward cannot create a Trustee",
                                           Status.FAILED, str(message))

    # 19. Using TrustAnchor1 to add a NYM.
    print(Colors.HEADER + "\n\t19.  Using TrustAnchor1 to add a NYM\n" + Colors.ENDC)
    (MyVars.test_results["Step 19"], message) = await add_nym(trustanchor1_did, user1_did, user1_verkey,
                                                              None, None, can_add=True)

    if MyVars.test_results["Step 19"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step19. Using TrustAnchor1 to add a NYM", Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status("Step19. Using TrustAnchor1 to add a NYM", Status.PASSED)

    # 20. Verify GET NYM.
    print(Colors.HEADER + "\n\t20.  Verify that new NYM added with TrustAnchor1\n" + Colors.ENDC)
    (MyVars.test_results["Step 20"], message) = await get_nym(trustanchor1_did, user1_did)

    if MyVars.test_results["Step 20"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step20. Verify that new NYM added with TrustAnchor1",
                                           Status.FAILED, str(message))
    else:
        MyVars.test_report.set_step_status("Step20. Verify that new NYM added with TrustAnchor1", Status.PASSED)

    # 21. Verify that TrustAnchor cannot create another TrustAnchor.
    print(Colors.HEADER + "\n\t21.  Verify that TrustAnchor cannot create another TrustAnchor\n" + Colors.ENDC)
    (temp, message) = await add_nym(trustanchor1_did, trustanchor2_did, trustanchor2_verkey,
                                    None, Roles.TRUST_ANCHOR, can_add=False)
    if temp:
        MyVars.test_results["Step 21"] = True
        print(Colors.OKGREEN + "::PASS::Validated that a TrustAnchor cannot create another TrustAnchor!\n"
              + Colors.ENDC)
        MyVars.test_report.set_step_status("Step21. Verify that TrustAnchor cannot create another TrustAnchor",
                                           Status.PASSED)
    else:
        MyVars.test_report.set_test_failed()
        if message is None:
            message = "TrustAnchor can create another TrustAnchor (should fail)"
        MyVars.test_report.set_step_status("Step21. Verify that TrustAnchor cannot create another TrustAnchor",
                                           Status.FAILED, str(message))

    # 22. Using default Trustee to remove new roles.
    print(Colors.HEADER + "\n\t22.  Using default Trustee to remove new roles\n" + Colors.ENDC)
    message_22 = ""
    (temp, message) = await add_nym(default_trustee_did, trustee1_did, trustee1_verkey,
                                    None, "", can_add=True)
    MyVars.test_results["Step 22"] = temp
    if not temp:
        message_22 += "\nCannot remove Trustee1's role - " + message

    (temp, message) = await get_nym(default_trustee_did, trustee1_did)
    MyVars.test_results["Step 22"] = MyVars.test_results["Step 22"] and temp
    if not temp:
        message_22 += "\nCannot check GET_NYM for Trustee1 - " + message

    (temp, message) = await add_nym(default_trustee_did, steward1_did, steward1_verkey,
                                    None, Roles.NONE, can_add=True)
    MyVars.test_results["Step 22"] = MyVars.test_results["Step 22"] and temp
    MyVars.test_results["Step 22"] = MyVars.test_results["Step 22"] and temp
    if not temp:
        message_22 += "\nCannot remove Steward1's role - " + message

    (temp, message) = await get_nym(default_trustee_did, steward1_did)
    MyVars.test_results["Step 22"] = MyVars.test_results["Step 22"] and temp
    if not temp:
        message_22 += "\nCannot check GET_NYM for Steward1 - " + message

    (temp, message) = await add_nym(default_trustee_did, tgb1_did, tgb1_verkey, None, Roles.NONE, can_add=True)
    MyVars.test_results["Step 22"] = MyVars.test_results["Step 22"] and temp
    if not temp:
        message_22 += "\nCannot remove TGB's role - " + message

    (temp, message) = await get_nym(default_trustee_did, tgb1_did)
    MyVars.test_results["Step 22"] = MyVars.test_results["Step 22"] and temp
    if not temp:
        message_22 += "\nCannot check GET_NYM for TGB - " + message

    (temp, message) = await add_nym(default_trustee_did, trustanchor1_did, trustanchor1_verkey,
                                    None, Roles.NONE, can_add=True)
    MyVars.test_results["Step 22"] = MyVars.test_results["Step 22"] and temp

    if not temp:
        message_22 += "\nCannot remove Trust_Anchor1's role - " + message

    (temp, message) = await get_nym(default_trustee_did, trustanchor1_did)
    MyVars.test_results["Step 22"] = MyVars.test_results["Step 22"] and temp
    if not temp:
        message_22 += "\nCannot check GET_NYM for Trust_Anchor1 - " + message

    if MyVars.test_results["Step 22"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step22. Using default Trustee to remove roles",
                                           Status.FAILED, message_22[1:])
    else:
        MyVars.test_report.set_step_status("Step22. Using default Trustee to remove roles", Status.PASSED)

    # 23. Verify that removed Trustee1 cannot create Trustee or Steward.
    print(Colors.HEADER + "\n\t23.  Verify that removed Trustee1 cannot create Trustee or Steward\n" + Colors.ENDC)
    message_23 = ""
    (temp, message) = await add_nym(trustee1_did, trustee2_did, trustee2_verkey, None, Roles.TRUSTEE, can_add=False)
    if temp:
        print(Colors.OKGREEN + "::PASS::Validated that removed Trustee1 cannot create another Trustee!\n"
              + Colors.ENDC)
    else:
        if message is None:
            message = ""
        message_23 += "\nRemoved Trustee can create Trustee (should fail) " + message

    MyVars.test_results["Step 23"] = temp

    (temp, message) = await add_nym(trustee1_did, steward2_did, steward2_verkey, None, Roles.STEWARD, can_add=False)
    if temp:
        print(Colors.OKGREEN + "::PASS::Validated that removed Trustee1 cannot create a Steward!\n" + Colors.ENDC)
    else:
        if message is None:
            message = ""
        message_23 += "\nRemoved Trustee can create Steward(should fail) " + message

    MyVars.test_results["Step 23"] = MyVars.test_results["Step 23"] and temp

    if MyVars.test_results["Step 23"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step23. Verify that removed Trustee1 cannot create Trustee or Steward",
                                           Status.FAILED, message_23[1:])
    else:
        MyVars.test_report.set_step_status("Step23. Verify that removed Trustee1 cannot create Trustee or Steward",
                                           Status.PASSED)

    # 24. Verify that removed Steward1 cannot create TrustAnchor.
    print(Colors.HEADER + "\n\t24.  Verify that removed Steward1 cannot create TrustAnchor\n" + Colors.ENDC)
    (temp, message) = await add_nym(steward1_did, trustanchor2_did, trustanchor2_verkey,
                                    None, Roles.TRUST_ANCHOR, can_add=False)
    if temp:
        print(Colors.OKGREEN + "::PASS::Validated that removed Steward1 cannot create a TrustAnchor!\n" + Colors.ENDC)
        MyVars.test_results["Step 24"] = True
        MyVars.test_report.set_step_status("Step24. Verify that removed Steward1 cannot create TrustAnchor",
                                           Status.PASSED)
    else:
        MyVars.test_report.set_test_failed()
        if message is None:
            message = "Steward1 can create a TrustAnchor (should fail)"
        MyVars.test_report.set_step_status("Step24. Verify that removed Steward1 cannot create TrustAnchor",
                                           Status.FAILED, message)

    # 25. Using default Trustee to create Trustee1.
    print(Colors.HEADER + "\n\t25.  Using default Trustee to create Trustee1\n" + Colors.ENDC)
    (MyVars.test_results["Step 25"], message) = await add_nym(default_trustee_did, trustee1_did, trustee1_verkey,
                                                              None, Roles.TRUSTEE, can_add=True)
    if MyVars.test_results["Step 25"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step25. Using default Trustee to create Trustee1", Status.FAILED, message)
    else:
        MyVars.test_report.set_step_status("Step25. Using default Trustee to create Trustee1", Status.PASSED)

    # 26. Using Trustee1 to add Steward1 and TGB1.
    print(Colors.HEADER + "\n\t26.  Using Trustee1 to add Steward1\n" + Colors.ENDC)
    message_26 = ""
    (temp, message) = await add_nym(trustee1_did, steward1_did, steward1_verkey, None, Roles.STEWARD, can_add=True)
    MyVars.test_results["Step 26"] = temp
    if not temp:
        message_26 += "\nCannot use Trustee1 to add Steward1 - " + message

    # Role TGB is not exist so we do not execute this step
    # (temp, message) = await add_nym(trustee1_did, tgb1_did, tgb1_verkey, None, Roles.TGB, can_add=True)
    # MyVars.test_results["Step 26"] = MyVars.test_results["Step 26"] and temp
    # if not temp:
    #     message_26 += "\nCannot use Trustee1 to add TGB1 - " + message

    if MyVars.test_results["Step 26"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step26. Using Trustee1 to add Steward1",Status.FAILED, message_26[1:])
    else:
        MyVars.test_report.set_step_status("Step26. Using Trustee1 to add Steward1", Status.PASSED)

    # 27. Verify that Steward1 cannot add back a TrustAnchor removed by TrustTee.
    print(Colors.HEADER + "\n\t27. Verify that Steward1 cannot add back a TrustAnchor removed by TrustTee\n"
          + Colors.ENDC)
    (temp, message) = await add_nym(steward1_did, trustanchor1_did, trustanchor1_verkey,
                                    None, Roles.TRUST_ANCHOR, can_add=False)
    if temp:
        print(Colors.OKGREEN + "::PASS::Validated that Steward1 cannot add back a TrustAnchor removed by TrustTee!\n"
              + Colors.ENDC)
        MyVars.test_results["Step 27"] = True
        MyVars.test_report.set_step_status("Step27. Verify that Steward1 cannot "
                                           "add back a TrustAnchor removed by TrustTee",
                                           Status.PASSED)
    else:
        MyVars.test_report.set_test_failed()
        if message is None:
            message = "Steward1 can add back TrustAnchor removed by Trustee (should fail)"
        MyVars.test_report.set_step_status("Step27. Verify that Steward1 cannot "
                                           "add back a TrustAnchor removed by TrustTee",
                                           Status.FAILED, message)

    # 28. Verify that Steward cannot remove a Trustee.
    print(Colors.HEADER + "\n\t28.  Verify that Steward cannot remove a Trustee\n" + Colors.ENDC)
    (temp, message) = await add_nym(steward1_did, trustee1_did, trustee1_verkey, None, Roles.NONE, can_add=False)
    if temp:
        print(Colors.OKGREEN + "::PASS::Validated that Steward cannot remove a Trustee!\n" + Colors.ENDC)
        MyVars.test_results["Step 28"] = True
        MyVars.test_report.set_step_status("Step28. Verify that Steward cannot remove a Trustee", Status.PASSED)
    else:
        MyVars.test_report.set_test_failed()
        if message is None:
            message = "Steward can create a Trustee (should fail)"
        MyVars.test_report.set_step_status("Step28. Verify that Steward cannot remove a Trustee",
                                           Status.FAILED, message)

    # 29. Verify that Trustee can add new Steward.
    print(Colors.HEADER + "\n\t29.  Verify that Trustee can add new Steward\n" + Colors.ENDC)
    message_29 = ""
    (temp, message) = await add_nym(trustee1_did, steward2_did, steward2_verkey, None, Roles.STEWARD, can_add=True)
    MyVars.test_results["Step 29"] = temp
    if not temp:
        message_29 += "\nTrustee cannot add Steward1 (should pass) - " + message

    temp = await add_nym(trustee1_did, steward3_did, steward3_verkey, None, Roles.STEWARD, can_add=True)
    MyVars.test_results["Step 29"] = MyVars.test_results["Step 29"] and temp
    if not temp:
        message_29 += "\nTrustee cannot add Steward2 (should pass) - " + message

    if MyVars.test_results["Step 29"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step29. Verify that Trustee can add new Steward",
                                           Status.FAILED, message_29[1:])
    else:
        MyVars.test_report.set_step_status("Step29. Verify that Trustee can add new Steward", Status.PASSED)

    # 30. Verify that Steward cannot remove another Steward.
    print(Colors.HEADER + "\n\t30.  Verify that Steward cannot remove another Steward\n" + Colors.ENDC)
    (temp, message) = await add_nym(steward1_did, steward2_did, steward2_verkey, None, Roles.NONE, can_add=False)
    if temp:
        print(Colors.OKGREEN + "::PASS::Validated that Steward cannot remove another Steward!\n" + Colors.ENDC)
        MyVars.test_results["Step 30"] = True
        MyVars.test_report.set_step_status("Step30. Verify that Steward cannot remove another Steward",
                                           Status.PASSED)
    else:
        if message is None:
            message = "Steward can remove another Steward (should fail)"
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step30. Verify that Steward cannot remove another Steward",
                                           Status.FAILED, message)

    # 31. Verify Steward can add a TrustAnchor.
    print(Colors.HEADER + "\n\t31.  Verify Steward can add a TrustAnchor\n" + Colors.ENDC)
    (MyVars.test_results["Step 31"], message) = await add_nym(steward2_did, trustanchor3_did, trustanchor3_verkey,
                                                              None, Roles.TRUST_ANCHOR, can_add=True)

    if MyVars.test_results["Step 31"] is False:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step31. Verify Steward can add a TrustAnchor", Status.FAILED, message)
    else:
        MyVars.test_report.set_step_status("Step31. Verify Steward can add a TrustAnchor", Status.PASSED)

    # =========================================================================================
    # Clean up here
    # =========================================================================================

    # 32. Close pool ledger and wallet.
    print(Colors.HEADER + "\n\t32.  Close pool ledger and wallet\n" + Colors.ENDC)
    try:
        await wallet.close_wallet(MyVars.wallet_handle)
        await pool.close_pool_ledger(MyVars.pool_handle)
        MyVars.test_results["Step 32"] = True
        MyVars.test_report.set_step_status("Step32. Close pool ledger and wallet", Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step32. Close pool ledger and wallet", Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)

    # 33. Delete wallet.
    print(Colors.HEADER + "\n\t33.  Delete pool ledger and wallet\n" + Colors.ENDC)
    try:
        await wallet.delete_wallet(MyVars.wallet_name, None)
        await pool.delete_pool_ledger_config(MyVars.pool_name)
        MyVars.test_results["Step 33"] = True
        MyVars.test_report.set_step_status("Step33. Delete pool ledger and wallet", Status.PASSED)
    except IndyError as E:
        MyVars.test_report.set_test_failed()
        MyVars.test_report.set_step_status("Step33. Delete pool ledger and wallet", Status.FAILED, str(E))
        print(Colors.FAIL + str(E) + Colors.ENDC)


def final_result():
    if all(value is True for value in MyVars.test_results.values()):
        print(Colors.OKGREEN + "\n\tAll the tests passed...\n" + Colors.ENDC)
    else:
        for test_num, value in MyVars.test_results.items():
            if not value:
                # print('{}: {}'.format(test_num, value))
                print('%s: ' % str(test_num) + Colors.FAIL + 'failed' + Colors.ENDC)
    MyVars.test_report.set_duration(time.time() - MyVars.begin_time)
    MyVars.test_report.write_result_to_file()


def test():
    MyVars.begin_time = time.time()
    test_prep()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_09_remove_and_add_role())
    loop.close()
    final_result()


test()
