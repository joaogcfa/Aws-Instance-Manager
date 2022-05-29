# Cloud AWS Instance Manager

## First of all you need to install the aws CLI

<a href="https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html">Install AWS CLI</a>

## Then you need to configure with you AWS account

On your terminal run:

```bash
aws configure
```

**Then you need to put your aws user credentials, select the region and the output format you can leave it default**

## To manage your instances you need to install `boto3` with the following tutorial

<a href="https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#installation">Boto3 Installation</a>

## Using boto3

To check if you are authenticated and boto3 is working with your AWS account try to run this python file:

**On the output you should see all the AWS users in the account**

```python
#this command is used to check if you are authenticated to aws

import boto3
iam = boto3.client("iam")

for user in iam.list_users()["Users"]:
    print("")
    print(user["UserName"])
    print(user["UserId"])
    print(user["Arn"])
    print(user["CreateDate"])
```
