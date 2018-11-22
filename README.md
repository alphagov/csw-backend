# Cloud Security Watch
(csw-backend)
This repository contains the code for creating an 
instance of Cloud Security Watch running in an 
infrastructure created by [alphagov/csw-infra](https://github.com/alphagov/csw-infra)



## Create your virtual env

**TODO - switch to venv** 

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

## Unit Tests

Now you can run the unit tests.

```
python -m unittest discover -v
```

Run the command above before adding/commiting.
If tests fail, don't worry, review the reason for the failures.
It might even be that the test is no longer valid,
in which case you need to update it or delete it.

## Create your AWS environment 

### Prerequisites 

#### Create a [Google Cloud Console](https://console.cloud.google.com) credentials file. 
You will only need to do this in an AWS 
account where this has not already been set up. 

####Create an [SSH key](https://www.ssh.com/ssh/keygen/). 
The build script uses ssh to tunnel to the RDS instance and create 
the database. It also creates a box which can 
be used for deploying chalice when working 
remotely with less bandwidth. 

The simplest approach is probably to match the env name.
The key will be uploaded to AWS so matching the env name 
avoids conflict and makes it easy to find.  

Like id_rsa, the difference between the 
private and public key file names should be: 
    * private=`/path/to/[keyname]` 
    * public=`/path/to/[keyname].pub`
    
#### Install gulp-cli globally 
`sudo npm install -g gulp-cli`

Gulp is a task runner used to run various build tasks.

#### Install npm-reinstall globally
`sudo npm install -g npm-reinstall`

Does a complete reinstall of npm dependencies not via 
the cache. Important for picking up github code changes 
if you're installing a branch rather than a tagged 
release and want the current commit on that branch.
 
### AWS vault

If you're running in a non-default AWS account where 
access is assumed via a profile you will need to set 
up aws-vault so you can assume the profile to run 
these commands. 

If you're running against the AWS account attached 
to your default credentials and don't use aws-vault 
you can just run the commands from gulp onwards. 

```gulp
gulp [task]
```

.. becomes .. 

```aws-vault-gulp
aws-vault exec [profile] -- gulp [task]
``` 

From here onwards `aws-vault exec [profile]` has been left out 
but it's assumed that any `gulp` task should be preceded 
with an appropriate `aws-vault` profile.   

### Building your environment 

All the build tasks are run from the build directory 

```build-folder
cd /path/to/csw-backend/build
```

NPM install installs;
* [alphagov/govuk-frontend](https://github.com/alphagov/govuk-frontend) and its dependencies
* [gulp](https://gulpjs.com/) and some modules for running buid tasks
* [alphagov/csw-infra](https://github.com/alphagov/csw-infra) to terraform the infrastructure
  
```install-dependencies
npm install
```

#### Upload shared parameters
 
Create shared credentials in parameter store.
These are the Google API OAuth credentials and the 
name of the S3 bucket used to store the terraform 
states. 

These are created once in each AWS account and 
reused for multiple environments. The assumption is 
that the live environment will be the only env 
deployed to the live account. So credentials are 
shared by test environments but different 
credentials are used in production.

If you're creating a new environment in an account 
that is already running an existing environment you 
can skip this step.

```load-params
gulp parameters.shared
```

Environments can be test stages or named for 
individual developers. Names should be short, 
lower case with no spaces.

### environment.build 

```build-env 
aws-vault exec [profile] -- gulp environment.build --env=[env name]
```

The `environment.build` task is made up of several 
sub-tasks.  

Especially when building test or developer accounts you 
may run into AWS Service Limits. In most cases these 
will be triggered in the `terraform apply` task. 

If terraform fails the output from the script should 
show the limit which needs increasing and this can be 
done through an AWS support request. 

#### environment.settings

You will first be prompted for some settings:
* A 16bit mask for your internal IP ranges. 
We've used:
    * 10.x for developers
    * 10.10x for test environments
* The name of your ssh key and the path to 
the public key. This will create an ssh key 
on AWS and upload your public key.

If you've followed the process above the ssh key name 
should match your env name. It asks for the path to the 
**public** part of the key **`/path/to/[keyname].pub`**

**If you put your private key path in this setting you 
will need to generate a new ssh key and start again**  
      
It will create a `settings.json` file for your 
environment in `/path/to/csw-backend/environments/[env]`

Make sure you have a `.ssh/config` file in your home 
directory. If it's not there just use `touch` to create 
an empty file. 

#### environment.params
      
It then generates some random passwords for 
RDS and uploads them to AWS parameter store.

#### environment.tfvars 

Then it creates your terraform tfvars files.

#### environment.terraform 

Then it initialises terraform with S3 (For 
an existing environment it will retrieve 
the existing environment state file)

It runs `terraform apply` to build your 
infrastructure and saves the terraform 
outputs to your `settings.json` file.

The `environment.terraform` task has sub-tasks 
which can all be run independently as necessary

#### sass.csw

Compiles SASS 

#### copy.assets

Copies assets from `govuk-frontend` 

#### environment.chalice

Then it creates a chalice `config.json` and 
runs `chalice deploy --stage=[env]`

The `environment.chalice` task has sub-tasks which 
can all be run independently as necessary

#### environment.database_build

Finally it creates and bootstraps the 
database, creating the tables and populating 
the lookup content and checks.   

### Loading an existing environment
* Creates your settings file and tfvars files
* Reinitialises terraform from S3 
* Reads terraform output into the settings file
* Creates the chalice config  

```load-env
gulp environment.load --env=[env]
```  

### Deploy an existing environment
* Compiles SASS and copies assets from `govuk-frontend`
* Runs terraform apply 
* Runs chalice deploy 

```deploy-env
gulp environment.deploy --env=[env]
```
Alternatively you can run ..

```terraform-env
gulp environment.terraform_apply --env=[env]
```
.. and/or .. 

```chalice-env
gulp environment.chalice_deploy --env=[env]
```
.. independently. 

### Delete and existing environment 
* Runs chalice delete 
* Runs terraform destroy

```destroy-env
gulp environment.cleanup --env=[env]
```

