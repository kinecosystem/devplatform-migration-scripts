set -e  # Stop if a command fails

function finish {
  echo 'Dont forget to kill the postgres db once you are done with it!, and delete the account creation seed from the config.py script if you want to'
}
trap finish EXIT

if [[ $AWS_SESSION_TOKEN == "" ]]
then
  echo "You must be logged in to aws"
  exit 1
fi

read -p "Enter the app id: " APP_ID
read -p "Enter the db connection string: " DB_CONNECTION
read -p "Enter the account creation seed (Our Root wallet): "  SEED

echo "App id is: $APP_ID"
echo "Database connection is $DB_CONNECTION"
echo "Account creation seed is $SEED"

while true; do
    read -p "Are you sure you with to continue? <yes/no>: " yn
    case $yn in
        yes) break;;
        no) exit 0;;
        * ) echo "Please type 'yes' or 'no'.";;
    esac
done

##############################################

echo "Getting the app's seed"
# Get key from ssm, decrypt, get the value field, base64 decode, filter by app, and extract the wallet seed
APP_SEED=$(aws ssm get-parameters --names "production_seeds_1" --with-decryption | jq -r ".Parameters[0].Value" | base64 -d | grep $APP_ID | cut -c6-61)

if [[ $APP_SEED == "" ]]
then
  APP_SEED=$(aws ssm get-parameters --names "production_seeds_2" --with-decryption | jq -r ".Parameters[0].Value" | base64 -d | grep $APP_ID | cut -c6-61)
fi

if [[ $APP_SEED == "" ]]
then
  echo "Couldn't get the app's seed"
  exit 1
fi

python3 verify_whitelist.py $APP_SEED

#################################################

echo "Connecting to database and creating users csv file"

SQLCMD="\"\copy (select wallet_address, False as created, row_number() over() -1 as row from users where app_id='$APP_ID') to '/home/ubuntu/$APP_ID' with csv;\""

ssh marketplace-1 "psql $DB_CONNECTION -c $SQLCMD"

echo "Copying csv file to local pc"
scp marketplace-1:/home/ubuntu/$APP_ID $HOME

##################################################
echo "Setting up local database"
sudo docker run -d -p 5432:5432 postgres
sleep 10
LOCAL_DB="postgresql://postgres:postgres@localhost:5432"
psql $LOCAL_DB -c "create table accounts(address varchar(56), created boolean, index int primary key);"
psql $LOCAL_DB -c "\copy accounts FROM '$HOME/$APP_ID' WITH (FORMAT csv);"

###################################################

echo "Creating the accounts"
if [ ! -d "$(pwd)/mass-account-creator" ]
then
  git clone git@github.com:kinecosystem/mass-account-creator.git
fi
cd mass-account-creator
git pull
pipenv install
sed -i -e "s/seed_here/$SEED/g" config.py
pipenv run python main.py

#####################################################

function killswitch {
  SQLCONFIG="update applications set config='{\"max_user_wallets\":null,\"sign_in_types\":[\"jwt\"], \"blockchain_version\": \"$1\"}' where id='$APP_ID'"
  ssh marketplace-1 "psql $DB_CONNECTION -c \"$SQLCONFIG\""
}

while true; do
    read -p "Type 'switch' to turn the killswitch, or 'stop' to stop: " yn
    case $yn in
        switch) break;;
        stop) exit 0;;
        * ) echo "Please type switch or stop.";;
    esac
done

echo "Funding hot wallet with initial amount on the new blockchain"
python3 fund_hot.py $APP_SEED $SEED
echo "Turning on killswitch"
killswitch 3

#####################################################

while true; do
    read -p "Type 'burn' to burn the account, or 'revert' to revert kill switch: " yn
    case $yn in
        burn) break;;
        revert) killswitch 2; exit 0;;
        * ) echo "Please type burn or revert.";;
    esac
done

echo "Burning the app wallet"
cd ..
echo "There is no need to input anything in the following prompt..."
sleep 3
printf "1\n$APP_SEED" | python3 cold_wallet.py  # Run the burn+migrate script on production


echo "Done!"

