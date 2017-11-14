from typing import Optional
import asyncio
import json
import logging
import os
import signal
from subprocess import Popen, PIPE, TimeoutExpired, STDOUT, check_output
import subprocess
from sys import stdin
import sys
import time
import random
from indy import pool, ledger
from indy.error import IndyError
from distutils.command.config import config


# -----------------------------------------------------------------------------------------
# This will run acceptance tests that will validate the add/remove roles functionality.
# -----------------------------------------------------------------------------------------
class Colors:
    """ Class to set the colors for text.  Syntax:  print(Colors.OKGREEN +"TEXT HERE" +Colors.ENDC) """
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'  # Normal default color


class MyVars:
    """  Needed some global variables. """

    pool_handle = 0
    folder_path = ".sovrin/"
    pool_genesis_txn_file = "pool_transactions_sandbox_genesis"
    original_pool_genesis_txn_file = "original_pool_transactions_sandbox_genesis"

    pool_genesis_txn_file_path = folder_path + pool_genesis_txn_file
    original_pool_genesis_txn_file_path = folder_path + original_pool_genesis_txn_file
    pool_name = "test_wait_forever_" + str(random.randrange(100, 1000, 2))
    debug = False
    the_error_message = "the information needed to connect was not found"
    test_results = {'Test 3': False}


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def command(command_str):
    os.system(command_str)

# def test_precondition():
#     """  Make a copy of pool_transactions_sandbox_genesis  """
#     print(Colors.HEADER + "\n\ Precondition \n" + Colors.ENDC)
# #     work_dir = os.path.expanduser('~') + os.sep
#     data_folder ='/usr/local/bin' 
#     subprocess.run(["cd " + data_folder], shell=True)
#     p = subprocess.Popen(["reset_client"], shell=True, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
#     p.stdin.write("YeS".encode(encoding='utf_8'))


def test_cli_to_val():
        machine_name = 'validator01'
        password = 'vagrant'
        p = subprocess.Popen(["ssh " + machine_name], shell=True, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
#         p.stdin.write("Yes".encode(encoding='utf_8'))
#         out, err = p.communicate(password + "\nexit\n")
#         print("[out: %s]\n[err: %s]" % (str(out), str(err)))
        print("stderr: " + str(p.stderr))
        os.system(password)
#         out, err = p.communicate(password.encode(encoding='utf_8', errors='strict'), 10)
#         error_code = p.stdin.write("vagrant".encode(encoding='utf_8', errors='strict'))
#         print("error code: " + str(error_code))
#         p.stdin.write("exit".encode(encoding='utf_8'))

test_cli_to_val()

async def verifying_the_correct_message_is_shown_when_you_are_unable_to_connect_to_the_validator_pool():
    logger.info("Test Scenario 02 -> started")
    try:
        # 1. Create ledger config from genesis txn file  ---------------------------------------------------------
        print(Colors.HEADER + "\n\t1.  Create Ledger\n" + Colors.ENDC)
        pool_config = json.dumps({"genesis_txn": str(MyVars.pool_genesis_txn_file_path)})
        try:
            await pool.create_pool_ledger_config(MyVars.pool_name, pool_config)
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            sys.exit[1]
        await asyncio.sleep(0)

        # 2. Open pool ledger -----------------------------------------------------------------------------------
        print(Colors.HEADER + "\n\t2.  Open pool ledger\n" + Colors.ENDC)
        try:
            result = await pool.open_pool_ledger(MyVars.pool_name, None)
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            sys.exit(1)

        # 3. verifying the message ------------------------------------------------------------------------
        print(Colors.HEADER + "\n\t3. verifying the message\n" + Colors.ENDC)
        try:
            print("error_message: " + MyVars.the_error_message)
    #         return_message = get_output()
            print("output_message: " + str(result))
            if (str(result) != MyVars.the_error_message):
                MyVars.test_results['Test 3'] = True
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            sys.exit[1]

        # 4. exit sovrin -----------------------------------------------------------------------------------
        print(Colors.HEADER + "\n\t4. exit sovrin\n" + Colors.ENDC)
        try:
            await command(['exit'])
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            sys.exit[1]
    except IndyError as E:
        print(Colors.FAIL + str(E) + Colors.ENDC)
    # ==================================================================================================================
    #      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! End of test, run cleanup !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ==================================================================================================================
    finally:
        # 5. Restore the pool_transactions_sandbox_genesis file ------------------------------------------------------------------------------
        print(Colors.HEADER + "\n\t==Clean up==\n\t5. Restore the pool_transactions_sandbox_genesis file\n" + Colors.ENDC)
        try:
            command('rm ' + MyVars.pool_genesis_txn_file_path)
            command('cp ' + MyVars.original_pool_genesis_txn_file_path + " " + MyVars.pool_genesis_txn_file_path)
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)

    logger.info("Test Scenario 02 -> completed")


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

# def test():
#     # test_precondition()
#     test_precondition()
#     # Create the loop instance using asyncio
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(verifying_the_correct_message_is_shown_when_you_are_unable_to_connect_to_the_validator_pool())
#     loop.close()
# 
#     print("\n\nResults\n+" + 40*"=" + "+")
#     final_results()
# 
# test()
