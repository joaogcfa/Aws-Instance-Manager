import boto3
import os
from dotenv import load_dotenv
import time

KeyName = 'joaoproject'
GroupIdName = 'joaoproject'
KeyNameNV = 'joaoprojectNV'
AMIName = 'AMI_Django'
LbName = 'Joao-Lb'
TgName = 'Target-Joao'
LaunchConfigName = 'LaunchJoao'
AutoScalingName = 'AutoJoao'
PolicyName = 'Joao-target-tracking-scaling-policy'


load_dotenv()

aws_access_key_id = os.getenv("ACCESS_KEY")
aws_secret_access_key = os.getenv("SECRET_KEY")

ec2_ohio = boto3.client('ec2',
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        region_name='us-east-2')

ec2_resource_ohio = boto3.resource(
    'ec2', region_name='us-east-2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)


vpc_list_ohio = ec2_ohio.describe_vpcs()
vpc_ohio = vpc_list_ohio['Vpcs'][0]['VpcId']

print("\n############ BEGIN ############\n")
print("\n")


print("### Initalizing in Ohaio ###\n")
print("\n")

########### CREATING KEY PAIR ############
print("Creating Key Pair")
delete_kp = ec2_ohio.delete_key_pair(KeyName=KeyName)
resp_Key = ec2_ohio.create_key_pair(KeyName=KeyName)
print("Key Pair Created\n")
########### WRITING ON THE KEY PAIR ###########

print("Writing on the Key Pair file ")
try:
    if os.path.exists('{0}.pem'.format(KeyName)):
        os.remove('{0}.pem'.format(KeyName))
except:
    print("Error while deleting file ", os.getcwd())

# write private key to file with 777 permissions
with os.fdopen(os.open('{0}.pem'.format(KeyName), os.O_WRONLY | os.O_CREAT, 0o777), "w+") as handle:
    handle.write(resp_Key['KeyMaterial'])
print("Key Pair file Written\n")


responseInst_ohio = ec2_ohio.describe_instances(
    Filters=[
        {
            'Name': 'tag:Name',
            'Values': [
                'PostGres',
            ]
        },
        {
            'Name': 'instance-state-name',
            'Values': [
                'running',
            ]

        },
    ],
)


if responseInst_ohio['Reservations']:
    print("Deleting Instance Previously Created")
    instanceId_ohio = responseInst_ohio['Reservations'][0]['Instances'][0]['InstanceId']
    ec2_ohio.terminate_instances(InstanceIds=[instanceId_ohio])
    instance_to_be_term = ec2_resource_ohio.Instance(instanceId_ohio)
    instance_to_be_term.wait_until_terminated()
    print("Previous Instance Deleted\n")

# file = open('{0}.pem'.format(KeyName), 'w')
# file.write(resp_Key['KeyMaterial'])
# file.close()

# DELETING PREVIOUS SECURITY GROUP
response_del_sec_group = ec2_ohio.describe_security_groups(
    Filters=[
        dict(Name='group-name', Values=[GroupIdName])
    ]
)
if response_del_sec_group['SecurityGroups']:
    print("Deleting Previous Security Group")
    group_id = response_del_sec_group['SecurityGroups'][0]['GroupId']
    delete_sc = ec2_ohio.delete_security_group(
        GroupId=group_id,
    )
    print("Previous Security Group Deleted\n")

# CREATING SECURITY GROUPS
print("Creating Security Group ")
resp_security_group = ec2_ohio.create_security_group(
    GroupName=GroupIdName,
    Description='Postgres',
    VpcId=vpc_ohio
)
print("Security Group Created\n")

gid = resp_security_group['GroupId']

print("Setting the rules of the Security Group")
ec2_ohio.authorize_security_group_ingress(
    GroupId=gid,
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 5432,
            'ToPort': 5432,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }
    ]
)
print("Rules Setted\n")


# CREATING THE INSTANCE
print("############ Creating the Instance in Ohio (Postgres) ############")


user_data = '''#!/bin/bash
cd /
sudo apt update
sudo apt install postgresql postgresql-contrib -y
sudo -u postgres psql -c "create user cloud;"
sudo -u postgres createdb tasks -O cloud
sudo sed -i s/"^#listen_addresses = 'localhost'"/"listen_addresses = '*'"/g  /etc/postgresql/10/main/postgresql.conf
sudo sed -i '$a host all all 0.0.0.0/0 trust' /etc/postgresql/10/main/pg_hba.conf
sudo ufw allow 5432/tcp
sudo systemctl restart postgresql
touch finalizou.bar
'''

instances = ec2_resource_ohio.create_instances(
    ImageId='ami-020db2c14939a8efb',
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro',
    KeyName=KeyName,
    BlockDeviceMappings=[
        {
            'DeviceName': "/dev/xvda",
            'Ebs': {
                'DeleteOnTermination': True,
                'VolumeSize': 8
            }
        }
    ],
    SecurityGroupIds=[gid],
    UserData=user_data
)

instance_id = instances[0].instance_id

print("Adding Name Tags to Key\n")
ec2_ohio.create_tags(Resources=[instance_id], Tags=[
    {'Key': 'Name', 'Value': 'PostGres'}])

print("Waiting for the Instace to be Running... \n")
instances[0].wait_until_running()
print("############ Ohaio Instance running! ############")
response_create_instance = ec2_ohio.describe_instances(InstanceIds=[
                                                       instance_id])
print("\n")


# NORTH VIRGINIA

print("### Initalizing in North Virtginia ###\n")
print("\n")

auto_client = boto3.client(service_name="autoscaling", aws_access_key_id=aws_access_key_id,
                           aws_secret_access_key=aws_secret_access_key,
                           region_name='us-east-1')
ec2_NV = boto3.client('ec2',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key,
                      region_name='us-east-1')

ec2_resource_NV = boto3.resource('ec2', region_name='us-east-1',
                                 aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)


response_describe_auto = auto_client.describe_auto_scaling_groups(
    AutoScalingGroupNames=[
        AutoScalingName,
    ],
)

elb_client = boto3.client(service_name="elbv2", aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key,
                          region_name='us-east-1')


responseInst_NV = ec2_NV.describe_instances(
    Filters=[
        {
            'Name': 'tag:Name',
            'Values': [
                'Django AS',
            ]
        },
        {
            'Name': 'instance-state-name',
            'Values': [
                'running',
            ]

        },
    ],
)


if responseInst_NV['Reservations']:
    instanceId_NV = responseInst_NV['Reservations'][0]['Instances'][0]['InstanceId']
    instance_to_be_term = ec2_resource_NV.Instance(instanceId_NV)


if response_describe_auto['AutoScalingGroups']:
    print("#### Previous Instalation Detected! ####\n")

    print("Deleting AMI")
    response_desc_image = ec2_NV.describe_images(
        Owners=['self'],
        Filters=[{
            'Name': 'name',
            'Values': [AMIName]}, ],
    )
    id_image = response_desc_image['Images'][0]['ImageId']
    ami = list(ec2_resource_NV.images.filter(ImageIds=[id_image]).all())[0]
    ami.deregister()

    print("Deleting Instance Previously Created From the AutoScaling Group")
    response_update = auto_client.update_auto_scaling_group(
        AutoScalingGroupName=AutoScalingName,
        MinSize=0,
        DesiredCapacity=0,
    )
    print("Waiting for instance to be terminated...")
    instance_to_be_term.wait_until_terminated()
    print("Instance terminated!\n")

    print("Deleting scaling group")
    response_del_auto_scaling_group = auto_client.delete_auto_scaling_group(
        AutoScalingGroupName=AutoScalingName,
        ForceDelete=True
    )
    print("Deleting Launch Config")
    auto_client.delete_launch_configuration(
        LaunchConfigurationName=LaunchConfigName
    )
    print("Deleting Load Balancer")
    describe_load = elb_client.describe_load_balancers()
    if describe_load["LoadBalancers"][0]['LoadBalancerName'] == LbName:
        lb_arm = describe_load["LoadBalancers"][0]['LoadBalancerArn']
        resp_listener = elb_client.describe_listeners(LoadBalancerArn=lb_arm)
        listener_arn = resp_listener['Listeners'][0]['ListenerArn']
        elb_client.delete_listener(ListenerArn=listener_arn)
        elb_client.delete_load_balancer(LoadBalancerArn=lb_arm)

    print("Deleting target_group")
    decribe_target = elb_client.describe_target_groups()
    if decribe_target['TargetGroups'][0]['TargetGroupName'] == TgName:
        tg_arn = decribe_target['TargetGroups'][0]['TargetGroupArn']
        elb_client.delete_target_group(TargetGroupArn=tg_arn)

    time.sleep(60)


vpc_list_NV = ec2_NV.describe_vpcs()
vpc_NV = vpc_list_NV['Vpcs'][0]['VpcId']


# DELETING PREVIOUS SECURITY GROUP
response_del_sec_group = ec2_NV.describe_security_groups(
    Filters=[
        dict(Name='group-name', Values=[GroupIdName])
    ]
)
if response_del_sec_group['SecurityGroups']:
    print("Deleting Instance Previously Created")
    group_id = response_del_sec_group['SecurityGroups'][0]['GroupId']
    delete_sc = ec2_NV.delete_security_group(
        GroupId=group_id,
    )

print("Creating Security Group")
resp_creat_sec_group = ec2_NV.create_security_group(
    GroupName=GroupIdName,
    Description='Django',
    VpcId=vpc_NV
)

gid_NV = resp_creat_sec_group['GroupId']

print("Setting the rules of the Security Group")
ec2_NV.authorize_security_group_ingress(
    GroupId=gid_NV,
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 8080,
            'ToPort': 8080,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }
    ]
)

########### CREATING KEY PAIR ############
print("Creating Key Pair")
delete_kp = ec2_NV.delete_key_pair(KeyName=KeyNameNV)
resp_Key_NV = ec2_NV.create_key_pair(KeyName=KeyNameNV)


print("Writing on the Key Pair file \n\n")
try:
    if os.path.exists('{0}.pem'.format(KeyNameNV)):
        os.remove('{0}.pem'.format(KeyNameNV))
except:
    print("Error while deleting file ", os.getcwd())

# write private key to file with 777 permissions
with os.fdopen(os.open('{0}.pem'.format(KeyNameNV), os.O_WRONLY | os.O_CREAT, 0o777), "w+") as handle:
    handle.write(resp_Key_NV['KeyMaterial'])


# print("############ Writing on the Key Pair file ############")
# file = open('{0}.pem'.format(KeyNameNV), 'w')
# file.write(resp_Key_NV['KeyMaterial'])
# file.close()


ip_instance_ohio = response_create_instance['Reservations'][0][
    'Instances'][0]['NetworkInterfaces'][0]['Association']['PublicIp']

# ip_instance_ohio = '18.118.138.238'

user_data_NV = '''#!/bin/bash
cd /
sudo apt update
git clone https://github.com/joaogcfa/tasks.git
sudo sed -i s/"'HOST': 'node1'"/"'HOST': '{0}'"/g  /tasks/portfolio/settings.py
sudo sed -i s/"'PASSWORD': 'cloud'"/"'PASSWORD': ''"/g  /tasks/portfolio/settings.py
touch intermediario.bar
cd tasks
./install.sh
sudo ufw allow 8080/tcp
./run.sh
touch finalizou.bar
'''.format(ip_instance_ohio)

print("############ Creating the Instance in North Virginia (Django) ############")
instances = ec2_resource_NV.create_instances(
    ImageId='ami-0279c3b3186e54acd',
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro',
    KeyName=KeyNameNV,
    BlockDeviceMappings=[
        {
            'DeviceName': "/dev/xvda",
            'Ebs': {
                'DeleteOnTermination': True,
                'VolumeSize': 8
            }
        }
    ],
    SecurityGroupIds=[gid_NV],
    UserData=user_data_NV
)

print("Adding Name Tags to Key\n")
instance_id = instances[0].instance_id
ec2_NV.create_tags(Resources=[instance_id], Tags=[
    {'Key': 'Name', 'Value': 'Django'}])

print("Waiting for the Instace to be Running... ")
instances[0].wait_until_running()
print("############ North Virginia Instance running! ############\n")


print("Creating AMI from the Instance that was created")

image_id = ec2_NV.create_image(InstanceId=instance_id, Name=AMIName)

image = ec2_resource_NV.Image(image_id['ImageId'])
if(image.state == 'pending'):
    print("Waiting for image to be available.")
    while(image.state != 'available'):
        image = ec2_resource_NV.Image(image_id['ImageId'])
    print("Image Available to use")


print("Deleting Instances\n")
resp_terminate = ec2_NV.terminate_instances(
    InstanceIds=[
        instance_id,
    ]
)


print("############ Creating LoadBalancers ")


subnets = []
sn_all = ec2_NV.describe_subnets()
for sn in sn_all['Subnets']:
    subnets.append(sn['SubnetId'])

create_lb_response = elb_client.create_load_balancer(Name=LbName,
                                                     Subnets=subnets,
                                                     SecurityGroups=[gid_NV],
                                                     Scheme='internet-facing')

lbId = create_lb_response['LoadBalancers'][0]['LoadBalancerArn']

arn_lbId = lbId.split('r/')[1]
print("LoadBalancer Created ############")
print("\n")

print("############ Creating Target Groups ")
create_tg_response = elb_client.create_target_group(Name=TgName,
                                                    Protocol='HTTP',
                                                    Port=8080,
                                                    VpcId=vpc_NV)

tgId = create_tg_response['TargetGroups'][0]['TargetGroupArn']

arn_tgId = 't' + tgId.split(':t')[1]
arn_id = arn_lbId + '/' + arn_tgId
print("Target Groups Created ############")
print("\n")


print("############ Creating Listener ")
create_listener_response = elb_client.create_listener(LoadBalancerArn=lbId,
                                                      Protocol='HTTP', Port=80,
                                                      DefaultActions=[{'Type': 'forward',
                                                                       'TargetGroupArn': tgId}])

response_describe_images = ec2_NV.describe_images(Owners=['self'])
for reservation in response_describe_images["Images"]:
    if reservation['Name'] == AMIName:
        AMI_ID = reservation["ImageId"]

print("Listener Created ############")
print("\n")


response_security_group = ec2_NV.describe_security_groups()

for group in response_security_group["SecurityGroups"]:
    if group['GroupName'] == GroupIdName:
        id_SecurityGroup = group['GroupId']


print("############ Creating Launch Config ")
response_launch_config = auto_client.create_launch_configuration(
    LaunchConfigurationName=LaunchConfigName,
    ImageId=AMI_ID,
    KeyName=KeyNameNV,
    SecurityGroups=[id_SecurityGroup],
    UserData=user_data_NV,
    InstanceType='t2.micro',
)

print("Launch Config Created ############")
print("\n")


print("############ Creating Auto Scaling ")
response_creat_auto = auto_client.create_auto_scaling_group(
    AutoScalingGroupName=AutoScalingName,
    LaunchConfigurationName=LaunchConfigName,
    TargetGroupARNs=[tgId],
    MaxInstanceLifetime=2592000,
    MaxSize=3,
    MinSize=1,
    VPCZoneIdentifier='subnet-f76c0fd9',
    Tags=[
        {
            "Key": "Name",
            "Value": "Django AS",
            "PropagateAtLaunch": True
        }
    ]
)
print("Auto Scaling Created ############")
print("\n")


print("############ Adding Policies")
response = auto_client.put_scaling_policy(
    AutoScalingGroupName=AutoScalingName,
    PolicyName=PolicyName,
    PolicyType='TargetTrackingScaling',
    TargetTrackingConfiguration={
        'PredefinedMetricSpecification': {
            'PredefinedMetricType': 'ALBRequestCountPerTarget',
            'ResourceLabel': arn_id,
        },
        'TargetValue': 50.0,
    },
)
print("Policies Added############")
print("\n")


print("################### DONE ###################")
