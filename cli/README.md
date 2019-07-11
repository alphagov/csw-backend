# Running CSW offline

You can now run a Cloud Security Watch audit without running 
any web infrastructure. 

## Setup 

All you need is: 
* A venv running python 3.6.5 
  (see the [main readme](../README.md)). 
* node 10.x
* aws credentials (we use aws-vault)

You also need to install the relevant dependencies 

```
# assuming you're in the repository root
# For the audit process
cd cli 
pip install -r requirements.txt 

# For the express interface
cd ../build 
npm install 
```

## Running an audit 

The audit runs against the current AWS account identified by 
the supplied credentials. 

```
# assuming you're in the repository root
cd cli
aws-vault exec [profile] -- python app.py audit
```

## Reviewing the results in the browser

The interface re-uses most of the components from the main 
jinja2 interface but runs as an express app interpreting 
the template files as nunjucks. 

```
# assuming you're in the repository root
cd express
aws-vault exec [profile] -- node app.js
```

 