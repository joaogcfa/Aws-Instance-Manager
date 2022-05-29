# Cloud AWS Instance Manager

## Project Description:

This project is aimed to create an Object-Relational Mapping (ORM) multi-cloud system with Load Balancer and Autoscalling, which means that this project has the capacity of creating and configuring Amazon AWS EC2 instances to create an REST API comunication.

To achieve this result, it was needed to use and SDK from python called Boto3, which manages Amazon Elastic Compute Cloud (EC2) programatically. Moreover, with the help of Boto, it was created two types of instances, one in Ohaio and one in North Virginia. The first one was where I would store the Database with Postgress and the second one where the ORM would be installed. 


## Setting the infrastructure:

### First of all you need to install the aws CLI

<a href="https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html">Install AWS CLI</a>

### Then you need to configure with you AWS account

On your terminal run:

```bash
aws configure
```

**Then you need to put your aws user credentials, select the region and the output format you can leave it default**

### To manage your instances you need to install `boto3` with the following tutorial

<a href="https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#installation">Boto3 Installation</a>

### Using boto3

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


## How to Run:

1. If you would like, change the names of this variables in the `main.py` file:

```python
    KeyName = 'joaoproject' #(KeyPair in Ohaio name)
    GroupIdName = 'joaoproject' #(Security Group name)
    KeyNameNV = 'joaoprojectNV' #(KeyPair in North Virginia name)
    AMIName = 'AMI_Django' #(AMI name)
    LbName = 'Joao-Lb' #(Load Balancer name)
    TgName = 'Target-Joao' #(Target Group name)
    LaunchConfigName = 'LaunchJoao' #(Launch Configuratio name)
    AutoScalingName = 'AutoJoao' #(Autoscalling Group name)
    PolicyName = 'Joao-target-tracking-scaling-policy' #(Policy name)
```

2. Run the `main.py` file
3. When step 2 is done (this may take a while) open yours EC2 dashboard in AWS and head to the LoadBalancer tab
4. Copy the IP address of the LB
5. Run the `client.py`
6. Open in the navigator the LB ip address
7. Execute the commands in 
