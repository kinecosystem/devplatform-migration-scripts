import sys

import kin

app_kp = kin.Keypair(sys.argv[1])
our_kp = kin.Keypair(sys.argv[2])
amount = int(sys.argv[3])

# The new kin_sdk does not know all of the kin 2 blockchain stuff out of the box
prod = kin.Environment('KIN2', 'https://horizon-ecosystem.kininfrastructure.com',
                       'Public Global Kin Ecosystem Network ; June 2018')
issuer = 'GDF42M3IPERQCBLWFEZKQRK77JQ65SCKTU3CW36HZVCX7XX5A5QXZIVK'


client = kin.KinClient(prod)
app_account = client.kin_account(app_kp.secret_seed)  # *100 because of decimal changes
builder = app_account.get_transaction_builder(100)
builder.update_sequence()
builder.append_payment_op(our_kp.public_address, str(amount * 100),
                          asset_code='KIN',
                          asset_issuer=issuer)
builder.sign()
builder.submit()

print('Paid {} from {} to {} on kin 2'.format(amount, app_kp.public_address, our_kp.public_address))

new_client = kin.KinClient(kin.PROD_ENVIRONMENT)
our_account = new_client.kin_account(our_kp.secret_seed)
our_account.send_kin(app_kp.public_address, amount, 100)

print('Paid {} from {} to {} on kin 3'.format(amount, our_kp.public_address, app_kp.public_address))

