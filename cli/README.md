# Running CSW offline

You can now run a Cloud Security Watch audit without running 
any web infrastructure. All you need is: 
* A venv running python 3.6.5 
  (see the [main readme](../README.md)). 
* node 10.x
* aws credentials (we use aws-vault)

## Running an audit 

The audit runs against the current AWS account identified by 
the supplied credentials. 

```
cd cli
aws-vault exec [profile] -- python app.py audit
```

## Reviewing the results in the browser

The interface re-uses most of the components from the main 
jinja2 interface but runs as an express app interpreting 
the template files as nunjucks. 

```
cd express
aws-vault exec [profile] -- node app.js
```

 