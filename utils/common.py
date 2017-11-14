'''
Created on Nov 13, 2017

@author: khoi.ngo
'''

from .constant import Colors, Constant
import asyncio
import json
from indy import wallet, pool
from indy.error import IndyError


class Common():
    '''
    Wrapper common steps.
    '''

    @staticmethod
    async def prepare_pool_and_wallet(pool_name, wallet_name, pool_genesis_txn_file):
        pool_handle = await Common().create_and_open_pool(pool_name, pool_genesis_txn_file)
        wallet_handle = await Common().create_and_open_wallet(pool_name, wallet_name)
        return pool_handle, wallet_handle

    @staticmethod
    async def clean_up_pool_and_wallet(pool_name, pool_handle, wallet_name, wallet_handle):
        await Common().close_pool_and_wallet(pool_handle, wallet_handle)
        await Common().delete_pool_and_wallet(pool_name, wallet_name)

    @staticmethod
    def clean_up_pool_and_wallet_files(pool_name="", wallet_name=""):
        import os
        import shutil
        print(Colors.HEADER + "\n\tCheck if the wallet and pool for this test already exist and delete them...\n" + Colors.ENDC)
        work_dir = Constant.work_dir

        if os.path.exists(work_dir + "/pool/" + pool_name):
            try:
                shutil.rmtree(work_dir + "/pool/" + pool_name)
            except IOError as E:
                print(Colors.FAIL + str(E) + Colors.ENDC)

        if os.path.exists(work_dir + "/wallet/" + wallet_name):
            try:
                shutil.rmtree(work_dir + "/wallet/" + wallet_name)
            except IOError as E:
                print(Colors.FAIL + str(E) + Colors.ENDC)

    async def create_and_open_pool(self, pool_name, pool_genesis_txn_file):
        print(Colors.HEADER + "\nCreate Ledger\n" + Colors.ENDC)
        pool_config = json.dumps({"genesis_txn": str(pool_genesis_txn_file)})
        # Create pool
        try:
            await pool.create_pool_ledger_config(pool_name, pool_config)
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            raise E

        print(Colors.HEADER + "\nOpen pool ledger\n" + Colors.ENDC)
        # get pool handle
        try:
            pool_handle = await pool.open_pool_ledger(pool_name, None)
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            raise E
        await asyncio.sleep(0)
        return pool_handle

    async def create_and_open_wallet(self, pool_name, wallet_name):
        print(Colors.HEADER + "\nCreate wallet\n" + Colors.ENDC)
        try:
            await wallet.create_wallet(pool_name, wallet_name, None, None, None)
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            raise E

        print(Colors.HEADER + "\nGet wallet handle\n" + Colors.ENDC)
        try:
            wallet_handle = await wallet.open_wallet(wallet_name, None, None)
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            raise E
        await asyncio.sleep(0)
        return wallet_handle

    async def close_pool_and_wallet(self, pool_handle, wallet_handle):
        print(Colors.HEADER + "\nClose pool\n" + Colors.ENDC)
        try:
            await pool.close_pool_ledger(pool_handle)
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            raise E

        print(Colors.HEADER + "\nClose waleet\n" + Colors.ENDC)
        try:
            await wallet.close_wallet(wallet_handle)
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            raise E
        await asyncio.sleep(0)

    async def delete_pool_and_wallet(self, pool_name, wallet_name):
        print(Colors.HEADER + "\nDelete pool\n" + Colors.ENDC)
        try:
            await pool.delete_pool_ledger_config(pool_name)
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            raise E

        print(Colors.HEADER + "\nDelete wallet\n" + Colors.ENDC)
        try:
            await wallet.delete_wallet(wallet_name, None)
        except IndyError as E:
            print(Colors.FAIL + str(E) + Colors.ENDC)
            raise E
        await asyncio.sleep(0)
