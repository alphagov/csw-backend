# csw-backend
Cloud Security Watch - Backend

## Bootstrap the database 

```
aws lambda invoke --function-name csw-dan-database_run --payload '{"User":"root","Password":"<your root password>","Commands":["CREATE DATABASE csw;","CREATE USER cloud_sec_watch WITH ENCRYPTED PASSWORD '<your user password>';","GRANT ALL PRIVILEGES ON DATABASE csw TO cloud_sec_watch;"]}' /tmp/lambda.out
```
`TODO - Create 2 users and close down the run privileges`

## Creating schema tables 

This isn't perfect yet. It's access controlled by who has lambda permission so by assuming you can run the lambda. 

```
aws lambda invoke --function-name csw-dan-database_create_tables --payload '{"Tables":["ProductTeam","AccountSubscription"]}' 
/tmp/output/file.json
```

## Inserting test data

```
aws-vault exec cst-test -- aws lambda invoke --function-name csw-dan-database_create_item --payload '{"Model":"ProductTeam","Params":{"team_name":"<team name>","active":true}}' /tmp/lambda.out

aws-vault exec cst-test -- aws lambda invoke --function-name csw-dan-database_create_item --payload '{"Model":"AccountSubscription","Params":{"account_id":<aws account id>,"account_name":"<aws account name>","product_team_id":<reference to above>,"active":true}}' /tmp/lambda.out
```

