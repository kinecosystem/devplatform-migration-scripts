# devplatform-migration-scripts
Scripts for the developer platform participants for the migration

## Requires:
* Python >= 3.4

## Usage:

Install the python pacakages
```bash
pip install --user requests
pip install --user kin-sdk==2.3.0
```

and run the script
```
python cold_wallet.py
```
Now follow the prompts from the script

Example:
```
Migration script for cold wallet
Choose environment:
1.Production
2.Testnet
[1/2]: 2
Initiated on testnet
Input the seed of your wallet: SBSROJDBNA2P4US7E4CMQBY2OMN65XMBCU6NN545V7SQ4BN5GEJARJ64
Burn succeeded
Done
```