# Symfony 7 EasyAdmin & Api-Platform
## Auto schule project for Diploma

- rebase .env to .env.local
- change DATABASE_URL

then:

```
composer i

composer u

php bin/console d:d:c

php bin/console d:s:u -f

php bin/console lexik:jwt:generate-keypair --overwrite

php bin/console secrets:set APP_SECRET

symfony serve
```

- set APP_SECRET at .env.local