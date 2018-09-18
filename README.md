# csw-backend
Cloud Security Watch - Backend

## Create your virtual env 

If you're running Python 2.7 or 3.7 you will need to install 3.6.5
 
```
brew install pyenv
pyenv install 3.6.5
virtualenv -p <path to your 3.6.5/bin/python> <virtual env name>
``` 

Then you'll need to install the dependencies and dev dependencies 
locally 

```
cd chalice 
pip install -r requirements-dev.txt
```

The requirements file is not stored in the repository root 
since the requirements need to be packaged by chalice as part 
of the chalice deploy

## Create your AWS environment 

Before you can run the chalice code you need to terraform a VPC 
for it to run in. 

https://github.com/alphagov/csw-infra

Follow the instructions in the readme to create your env. 

## Create your chalice config.json

For developer environments your env name should be your name in 
lower case

1. `cd environments`
2. `chalice new-project <your env name>`
3. `cd <your env name>`
4. Test the chalice deploy prefix with aws-vault exec if using 
`chalice deploy` `chalice delete` 
5. `cd ../chalice`
6. Link your .chalice config folder into the chalice code 
`ln -fs ../environments/<your env name>/.chalice .chalice`
7. Update your .chalice/config.json with the settings 
from terraform output _(TODO - automate this)_    
8. Change the stage name to <your env name>
9. Change the api_gateway_stage to "app"
10. Run `chalice deploy --stage=<your env name>`

## Bootstrap the database 

```
aws lambda invoke \
--function-name csw-dan-database_run \ 
--payload \
'{ \
  "User":"root", \
  "Password":"<your root password>", \
  "Commands":[ \
    "CREATE DATABASE csw;", \
    "CREATE USER cloud_sec_watch WITH ENCRYPTED PASSWORD '<your user password>';", \
    "GRANT ALL PRIVILEGES ON DATABASE csw TO cloud_sec_watch;" \
  ] \
}' /tmp/lambda.out
```
`TODO - Create 2 users and close down the run privileges`

Once you've created the run user put the credentials into the 
environment variables in your .chalice/config.json

## Creating schema tables 

This isn't perfect yet. It's access controlled by who has lambda permission so by assuming you can run the lambda. 

```
aws lambda invoke \ 
--function-name csw-dan-database_create_tables \ 
--payload \
'{ \
   "Tables":[ \
     "ProductTeam", \
     "AccountSubscription" \
   ] \
}' /tmp/lambda.out
```

## Inserting test data

```
aws-vault exec cst-test -- aws lambda invoke \ 
--function-name csw-dan-database_create_item \ 
--payload \ 
'{ \
  "Model":"ProductTeam", \
  "Params":{ \
    "team_name":"<team name>", \
    "active":true \
  } \
}' /tmp/lambda.out

aws-vault exec cst-test -- aws lambda invoke \
--function-name csw-dan-database_create_item \
--payload \
'{ \
  "Model":"AccountSubscription", \
  "Params":{ \
    "account_id":<aws account id>, \
    "account_name":"<aws account name>", \
    "product_team_id":<reference to above>, \
    "active":true \
  } \
}' /tmp/lambda.out
```

