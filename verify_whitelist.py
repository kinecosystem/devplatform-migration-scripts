import base64
import sys

import kin

seed = sys.argv[1]
kp = kin.Keypair(seed)

client = kin.KinClient(kin.PROD_ENVIRONMENT)
account_data = client.get_account_data('GCPGMBNS42RQODVI7JCIRZDOO2PKS3BDNHEL45YMB7PLGJP65FS7U4UV')
try:
    if account_data['data'][kp.public_address] != base64.b64encode(kp._hint).decode():
        print('Hint is incorrect')
        sys.exit(1)
except KeyError:
    print('Account is not on the whitelist')
    sys.exit(1)
