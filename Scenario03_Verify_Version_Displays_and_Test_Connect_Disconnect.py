from indy import agent, ledger, pool, signus
import json
import subprocess
import asyncio


async def test():
    seed_trustee01 = "000000000000000000000000Steward1"
    sovrin_version = "Running Sovrin 1.1.4.3"
    new_wallet_created = "New wallet Default created"

    print("Begin test\n")
    sovrin_output = subprocess.check_output(["sovrin"], stdout=subprocess.PIPE, shell=True)
    sovrin_output = sovrin_output.stdout

    if sovrin_version in sovrin_output:
        print("Version is displayed!")
    else:
        print("Version is not displayed!")

    seed_output = subprocess(["new key with seed " + seed_trustee01], stdout=subprocess.PIPE, shell=True)
    seed_output = seed_output.stdout
    if new_wallet_created in seed_output:
        print("Wallet default is created!")
    else:
        print("Wallet default is not created!")

    print("Seeding complete")

    subprocess(["connect test"], stdout=subprocess.PIPE, shell=True)
    print("Connect test")

    subprocess(["disconnect"], stdout=subprocess.PIPE, shell=True)
    print("Disconnect")

    subprocess(["connect test"], stdout=subprocess.PIPE, shell=True)
    print("Connect test")

    subprocess(["exit"], stdout=subprocess.PIPE, shell=True)

    print("\nEnd test")

loop = asyncio.get_event_loop()
loop.run_until_complete(test())
loop.close()

print("End")
