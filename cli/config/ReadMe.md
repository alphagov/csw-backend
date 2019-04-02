# Allow lists and exceptions 

You can create exceptions for the CSW rules by creating JSON files 
in this directory. 

## Allow lists 
An allowlist file looks like this: 

```allowlist
[
    {
        "account": "123123123123",
        "cidr": "1.2.3.4/32",
        "reason": "explanation of why IP/CIDR should be allowed",
        "user": "your.email@domain.com",
        "date_created": "2019-03-31T15:14:00",
        "date_expires": "2019-06-30T23:59:59"
    }
]
```
## Resource exception 
A resource exception file looks like this:
```exception
[
    {
        "account": "123123123123",
        "region": "[AWS region|*]",
        "resource_name": "The name of the resource",
        "reason": "explanation of why the rule does not apply",
        "user": "your.email@domain.com",
        "date_created": "2019-03-31T15:14:00",
        "date_expires": "2019-06-30T23:59:59"  
    }
]
```