from indy import agent, ledger, pool, signus
import json
import subprocess
import asyncio


async def test():
    seed_trustee01 = "000000000000000000000000Steward1"
    sovrin_version = "Running Sovrin 1.1.4.3"
    new_wallet_created = "New wallet Default created"

    print("Begin test\n")
    proc = subprocess.Popen("sovrin", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    print(proc.communicate(input="connect test\nexit\n".encode())[0])

    print("\nEnd test")


loop = asyncio.get_event_loop()
loop.run_until_complete(test())
loop.close()

print("End")
