import kin
import requests

# New sdk doesn't have the old blockchain urls


def get_kin_balance(client, address, issuer):
    # New sdk only checks for native balance
    data = client.get_account_data(address)
    kin_balance = None
    for balance in data.balances:
        if balance['asset_code'] == 'KIN' and balance['asset_issuer'] == issuer:
            kin_balance = balance['balance']

    if kin_balance is None:
        print('No kin balance found')
        quit(1)

    return kin_balance


prod = kin.Environment('PROD', 'https://horizon-ecosystem.kininfrastructure.com',
                       'Public Global Kin Ecosystem Network ; June 2018')
test = kin.Environment('TEST', 'https://horizon-playground.kininfrastructure.com',
                       'Kin Playground Network ; June 2018')


print('Migration script for cold wallet')
answer = input('Choose environment:\n'
               '1.Production\n'
               '2.Testnet\n'
               '[1/2]: ')

if answer == '1':
    client = kin.KinClient(prod)
    migration_endpoint = 'https://migration-devplatform-production.developers.kinecosystem.com'
    issuer = 'GDF42M3IPERQCBLWFEZKQRK77JQ65SCKTU3CW36HZVCX7XX5A5QXZIVK'
    print('Initiated on production')
elif answer == '2':
    client = kin.KinClient(test)
    migration_endpoint = 'https://migration-devplatform-playground.developers.kinecosystem.com'
    issuer = 'GBC3SG6NGTSZ2OMH3FFGB7UVRQWILW367U4GSOOF4TFSZONV42UJXUH7'
    print('Initiated on testnet')
else:
    print('Invalid response')
    quit(1)

kin_address = input('Input the public address of your shared wallet: ')
seed = input('Input the seed of your cold wallet: ')

try:
    keypair = kin.Keypair(seed)
except kin.KinErrors.StellarSecretInvalidError:
    print('Seed is invalid')
    quit(1)

account = client.kin_account(seed)
balance = get_kin_balance(client, kin_address, issuer)
builder = account.get_transaction_builder(100)
builder.update_sequence()
# Balance * 100 cause of the decimal points changes
builder.append_change_trust_op('KIN', issuer, str(balance*100), source=kin_address)
# Set both signers weight to 0
builder.append_set_options_op(master_weight=0,
                              signer_type='ed25519PublicKey',
                              signer_address=keypair.public_address,
                              signer_weight=0,
                              source=kin_address)
builder.sign()
try:
    tx_hash = account.submit_transaction(builder)
    print('Burn succeeded')
except Exception as e:
    print('Failed', e)

response = requests.post(migration_endpoint+'/migrate?address=' + kin_address)
if response.ok:
    print('Done')

else:
    print('Failed migration')
    print(response.text)


