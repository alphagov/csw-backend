# 4. Use serverless

Date: 2017-11-22

## Status

Accepted

## Context

Given that we were not going to have the benefit of 
offloading maintenance responsibility to the PaaS we 
wanted to keep the cost and the requirement for 
maintenance as small as possible.  

We considered a traditional load balanced EC2 model 
running something like django. 

There are many benefits to having the tools of the django 
infrastructure. 

The downside is that you have a maintenance requirement 
to maintain the server instances. You also somewhat bind 
yourself to running the service 24/7 and paying for it. 

With serverless you only pay when the functions get 
executed and there is a significant free tier. 

This limits our cost and our exposure since maintaining 
the infrastructure that hosts the lambda functions is 
AWS' responsibility not ours.  

## Decision

We will use AWS Lambda for this service. 
 
In conjunction with an ENI to allow the lambdas access 
to RDS running inside a VPC if necessary.

## Consequences

The downside of lambdas is that they live outside the VPC. 
You can work around this by provisioning an ENI (elastic 
network interface) which allows the lambda access to the 
VPC but this has a setup cost in terms of time which means
having a keep warm function to ensure users don't have to 
wait for the ENI to provision.