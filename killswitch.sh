psql $1 -c "update applications set config='{\""max_user_wallets\"":null,\""sign_in_types\"":[\""jwt\""], \""blockchain_version\"": \""$2\""}' where id='$3'"
