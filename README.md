# csw-backend
Cloud Security Watch - Backend


## Creating schema tables 

This isn't perfect yet. It's access controlled by who has lambda permission so by assuming you can run the lambda. 

```
aws lambda invoke --function-name csw-dan-database_create_tables --payload '{"Tables":["Model1","Model2"]}' 
/tmp/output/file.json
```

