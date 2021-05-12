# Project-503 : Blog Page Application (Django) deployed on AWS Application Load Balancer with Auto Scaling, S3, Relational Database Service(RDS), VPC's Components, DynamoDB and Cloudfront with Route 53 (STUDENT_SOLUTION)

## Description

The Clarusway Blog Page Application aims to deploy blog application as a web application written Django Framework on AWS Cloud Infrastructure. This infrastructure has Application Load Balancer with Auto Scaling Group of Elastic Compute Cloud (EC2) Instances and Relational Database Service (RDS) on defined VPC. Also, The Cloudfront and Route 53 services are located in front of the architecture and manage the traffic in secure. User is able to upload pictures and videos on own blog page and these are kept on S3 Bucket. This architecture will be created by Firms DevOps Guy.

## Problem Solution Order

## Steps to Solution
  
### Step 1: Create dedicated VPC and whole components
        
    ### VPC
    - Lets create VPC first. 
        create a vpc named `aws_capstone-VPC` CIDR blok is `90.90.0.0/16` 
        no ipv6 CIDR block
        tenancy: default
    - select `aws_capstone-VPC` VPC, click `Actions` and `enable DNS hostnames` for the `aws_capstone-VPC`. 
    
    ## Subnets
    - Go to the subnet section on left hand side and click it. Select create subnet.
        - Create a public subnet named `aws_capstone-public-subnet-1A` under the vpc aws_capstone-VPC in AZ us-east-1a with 90.90.10.0/24
        - Create a private subnet named `aws_capstone-private-subnet-1A` under the vpc aws_capstone-VPC in AZ us-east-1a with 90.90.11.0/24
        - Create a public subnet named `aws_capstone-public-subnet-1B` under the vpc aws_capstone-VPC in AZ us-east-1b with 90.90.20.0/24
        - Create a private subnet named `aws_capstone-private-subnet-1B` under the vpc aws_capstone-VPC in AZ us-east-1b with 90.90.21.0/24

    - To coordinate `auto-assign IP` setting up for public subnets. Select each public subnets and click Modify "auto-assign IP settings" and select "Enable auto-assign public IPv4 address" 

    ## Internet Gateway

    - Click Internet gateway section on left hand side. Create an internet gateway named `aws_capstone-IGW` and create.

    - ATTACH the internet gateway `aws_capstone-IGW` to the newly created VPC `aws_capstone-VPC`. Go to VPC and select newly created VPC and click action ---> Attach to VPC ---> Select `aws_capstone-VPC` VPC 

    ## Route Table
    - Go to route tables on left hand side. We have already one route table as main route table. Change it's name as `aws_capstone-public-RT` 
    - Create a route table and give a name as `aws_capstone-private-RT`.
    - Add a rule to `aws_capstone-public-RT` in which destination 0.0.0.0/0 (any network, any host) to target the internet gateway `aws_capstone-IGW` in order to allow access to the internet.
    - Select the private route table, come to the subnet association subsection and add private subnets to this route table. Similarly, we will do it for public route table and public subnets. 
        
    ## Endpoint
    - Go to the endpoint section on the left hand menu
    - select endpoint
    - click create endpoint
    - Select `com.amazonaws.us-east-1.s3` as service name (We can filter the list writing S3)
    - select `aws_capstone-VPC`
    - select private route table
    - Policy `Full Access`
    - Create

### Step 2: Create Security Groups (ALB ---> EC2 ---> RDS)

1. ALB Security Group
Name            : aws_capstone_ALB_Sec_Group
Description     : ALB Security Group allows traffic HTTP and HTTPS ports from anywhere 
Inbound Rules
VPC             : AWS_Capstone_VPC
HTTP(80)    ----> anywhere
HTTPS (443) ----> anywhere

2. EC2 Security Groups
Name            : aws_capstone_EC2_Sec_Group
Description     : EC2 Security Groups only allows traffic coming from aws_capstone_ALB_Sec_Group Security Groups for HTTP and HTTPS ports. In addition, ssh port is allowed from anywhere
VPC             : AWS_Capstone_VPC
Inbound Rules
HTTP(80)    ----> aws_capstone_ALB_Sec_Group
HTTPS (443) ----> aws_capstone_ALB_Sec_Group
ssh         ----> anywhere

3. RDS Security Groups
Name            : aws_capstone_RDS_Sec_Group
Description     : EC2 Security Groups only allows traffic coming from aws_capstone_EC2_Sec_Group Security Groups for MYSQL/Aurora port. 

VPC             : AWS_Capstone_VPC
Inbound Rules
MYSQL/Aurora(3306)  ----> aws_capstone_EC2_Sec_Group

4. NAT Instance Security Group
Name            : aws_capstone_NAT_Sec_Group
Description     : ALB Security Group allows traffic HTTP and HTTPS and SSH ports from anywhere 
Inbound Rules
VPC             : AWS_Capstone_VPC
HTTP(80)    ----> anywhere
HTTPS (443) ----> anywhere
SSH (22)    ----> anywhere

### Step 3: Create RDS
we should arrange subnet group for our custom VPC. Click `subnet Groups` on the left hand menu and click `create DB Subnet Group` 
```text
Name               : aws_capstone_RDS_Subnet_Group
Description        : aws capstone RDS Subnet Group
VPC                : aws_capstone_VPC
Add Subnets
Availability Zones : Select 2 AZ in aws_capstone_VPC
Subnets            : Select 2 Private Subnets in these subnets

```
- Go to the RDS console and click `create database` button
```text
Choose a database creation method : Standart Create
Engine Options  : Mysql
Version         : 8.0.20
Templates       : Free Tier
Settings        : 
    - DB instance identifier : aws-capstone-RDS
    - Master username        : admin
    - Password               : Clarusway1234 
DB Instance Class            : Burstable classes (includes t classes) ---> db.t2.micro
Storage                      : 20 GB and enable autoscaling(up to 40GB)
Connectivity:
    VPC                      : aws_capstone_VPC
    Subnet Group             : aws_capstone_RDS_Subnet_Group
    Public Access            : No 
    VPC Security Groups      : Choose existing ---> aws_capstone_RDS_Sec_Group
    Availability Zone        : No preference
    Additional Configuration : Database port ---> 3306
Database authentication ---> Password authentication
Additional Configuration:
    - Initial Database Name  : database1
    - Backup ---> Enable automatic backups
    - Backup retention period ---> 7 days
    - Select Backup Window ---> Select 03:00 (am) Duration 1 hour
    - Maintance window : Select window    ---> 04:00(am) Duration:1 hour
create instance
```

### Step 4: Create two S3 Buckets and set one of these as static website.
Go to the S3 Consol and lets create two buckets. 

1. Blog Website's S3 Bucket

- Click Create Bucket
```text
Bucket Name : awscapstones3<name>blog
Region      : N.Virginia
Block all public access : Unchecked
Other Settings are keep them as are
create bucket
```


2. S3 Bucket for failover scenario

- Click Create Bucket
```text
Bucket Name : www.clarusway.us
Region      : N.Virginia
Block all public access : Unchecked
Please keep other settings as are
create bucket
```

- Selects created `www.clarusway.us` bucket ---> Properties ---> Static website hosting
```text
Static website hosting : Enable
Hosting Type : Host a static website
Index document : index.html
save changes
```
- Select Upload and upload index.html and sorry.jpg files from given folder---> Permissions ---> Grant public-read access ---> Checked warning massage

## Step 5: Copy files downloaded or cloned from `Clarusway_project` repo on Github 

## Step 6: Prepair your Github repository
- Create private project repository on your Github and clone it on your local. Copy all files and folders which are downloaded from clarusway repo under this folder. Commit and push them on your private Git hup Repo.

## Step 7: Prepare a userdata to be utilized in Launch Template
Please 
```bash
#!/bin/bash
apt-get update -y
apt-get install git -y
apt-get install python3 -y
cd /home/ubuntu/
TOKEN="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
git clone https://$TOKEN@<YOUR PRIVATE REPO URL>
cd /home/ubuntu/<YOUR PRIVATE REPO NAME>
apt install python3-pip -y
apt-get install python3.7-dev default-libmysqlclient-dev -y
pip3 install -r requirements.txt
cd /home/ubuntu/<YOUR PRIVATE REPO NAME>/src
python3 manage.py collectstatic --noinput
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:80
```

## Step 8: Write RDS database endpoint and S3 Bucket name in settings file given by Clarusway Fullstack Developer team and push your application into your own public repo on Github
Please follow and apply the instructions in the developer_notes.txt.
```text
- Movie and picture files are kept on S3 bucket named aws_capstone_S3_<name>_Blog as object. You should create an S3 bucket and write name of it on "/src/cblog/settings.py" file as AWS_STORAGE_BUCKET_NAME variable. In addition, you must assign region of S3 as AWS_S3_REGION_NAME variable

- Users credentials and blog contents are going to be kept on RDS database. To connect EC2 to RDS, following variables must be assigned on "/src/cblog/settings.py" file after you create RDS;
    a. Database name - "NAME" variable 
    b. Database endpoint - "HOST" variables
    c. Port - "PORT"
    d. PASSWORD variable must be written on "/src/.env" file not to be exposed with settings file
```
- Please check if this userdata is working or not. to do this create new instance in public subnet and show to students that it is working

## Step 9: Create NAT Instance in Public Subnet
To launch NAT instance, go to the EC2 console and click the create button.

```text
Go to the EC2 console and click Launch instance 
select NAT Instance `amzn-ami-vpc-nat-hvm-2018.03.0.20181116-x86_64-ebs` 
Instance Type: t2.micro
Configure Instance Details  
    - Network : aws_capstone_VPC
    - Subnet  : aws_capstone-public-subnet-1A (Doesn't matter)
    - Other features keep them as are
Storage ---> Keep it as is
Tags: Key: Name     Value: AWS Capstone NAT Instance
Configure Security Group
    - Select an existing security group: aws_capstone_NAT_Sec_Group
Review and select our own pem key
```

- select NAT instance and enable stop source/destination check
- go to private route table and write a rule
```
Destination : 0.0.0.0/0
Target      : instance ---> Select NAT Instance
Save
```

## Step 10: Create Launch Template and IAM role for it
Go to the IAM role console click role on the right hand menu than create role
```text
Select EC2 as trusted entity ---> click Next:Permission
Choose AmazonS3FullAccess policy
No tags
Role Name: aws_capstone_EC2_S3_Full_Access
```

To create Launch Template, go to the EC2 console and select `Launch Template` on the left hand menu. Tab the Create Launch Template button.
```bash
Launch template name                : aws_capstone_launch_template
Template version description        : Blog Web Page version 1
Amazon machine image (AMI)          : Ubuntu 18.04
Instance Type                       : t2.micro
Key Pair                            : mykey.pem
Network Platform                    : VPC
Security Groups                     : aws_capstone_EC2_sec_group
Storage (Volumes)                   : keep it as is
Resource tags                       : Key: Name   Value: aws_capstone_web_server
Advance Details:
    - IAM instance profile          : aws_capstone_EC2_S3_Full_Access
    - Termination protection        : Enable
    - User Data
#!/bin/bash
apt-get update -y
apt-get install git -y
apt-get install python3 -y
cd /home/ubuntu/
TOKEN="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
git clone https://$TOKEN@<YOUR PRIVATE REPO URL>
cd /home/ubuntu/<YOUR PRIVATE REPO NAME>
apt install python3-pip -y
apt-get install python3.7-dev default-libmysqlclient-dev -y
pip3 install -r requirements.txt
cd /home/ubuntu/<YOUR PRIVATE REPO NAME>/src
python3 manage.py collectstatic --noinput
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:80
```
- create launch template

## Step 11: Create certification for secure connection
To get certificate for our Domain name and sub domains, Go to the certification manager console and click `request a certificate` button. Select `Request a public certificate`, then `request a certificate` ---> *.clarusway.us ---> DNS validation ---> No tag ---> Review ---> click confirm and request button. Then it takes a while to be activated. 

## Step 12: Create ALB and Target Group
Go to the Load Balancer section on the left hand side menu on EC2 console. Click `create Load Balancer` button and select Application Load Balancer
```text
Application Load Balancer ---> Create
Name                    : awscapstoneALB
Schema                  : internet-facing
Listeners               : HTTPS, HTTP
Availability Zones      : 
    - VPC               : aws_capstone_VPC
    - Availability zones: 
        1. aws_capstone-public-subnet-1A
        2. aws_capstone-public-subnet-1B
Step 2 - Configure Security Settings
Certificate type ---> Choose a certificate from ACM (recommended)
    - Certificate name    : "*.clarusway.us" certificate
    - Security policy     : keep it as is
Step 3 - Configure Security Groups : aws_capstone_ALB_Sec_group
Step 4 - Configure Routing
    - Target group        : New target group
    - Name                : awscapstoneTargetGroup
    - Target Type         : Instance
    - Protocol            : HTTP
    - Port                : 80
    - Protocol version    : HTTP1
    - Health Check        :
      - Protocol          : HTTP
      - Path              : /
      - Port              : traffic port
      - Healthy threshold : 5
      - Unhealthy threshold : 2
      - Timeout           : 5
      - Interval          : 20
      - Success Code      : 200
Step 5 - Register Targets
without register any target click Next: Review
```
- click create

To ridirect traffic from HTTP to HTTPS, go to the ALB console and select Listeners sub-section.

```text
select HTTP: 80 rule ---> click edit
- Default action(s)
 - Remove existing rule and create new rule which is
    - Redirect to HTTPS 443
    - Original host, path, query
    - 301 - permanently moved
```
Lets go ahead and look at our ALB DNS --> it going to say "it is not safe", however, it will be fixed after connect ALB to our DNS with Route 53

## Step 13: Create Autoscaling Group with Launch Template 

Go to the Autoscaling Group on the left hand side menu. Click create Autoscaling group. 

- Choose launch template or configuration
```text 
Auto Scaling group name         : aws_capstone_ASG
Launch Template                 : aws_capstone_launch_template
```

- Configure settings

```text
Instance purchase options       : Adhere to launch template
Network                         :
    - VPC                       : aws-capstone-VPC
    - Subnets                   : Private 1A and Private 1B
```

Configure advanced options
```text
- Load balancing                                : Attach to an existing load balancer
- Choose from your load balancer target groups  : awscapstoneTargetGroup
- Health Checks
    - Health Check Type             : ELB
    - Health check grace period     : 300
```

Configure group size and scaling policies
```text
Group size
    - Desired capacity  : 2
    - Minimum capacity  : 2
    - Maximum capacity  : 4
Scaling policies
    - Target tracking scaling policy
        - Scaling policy name       : Target Tracking Policy
        - Metric Type               : Average CPU utilization
        - Target value              : 70
```

Add notifications
```text
Create new Notification
    - Notification1
        - Send a notification to    : aws-capstone-SNS
        - with these recipients     : serdar@clarusway.com
        - event type                : select all 
```

<!-- WARNING!!! If you need to look at inside one of your instance to make sure if our files have pulled from Github, please follow these steps

```bash
eval "$(ssh-agent)" (your local)
ssh-add <pem-key>   (your local )
ssh -A ec2-user@<Public IP or DNS name of NAT instance> (your local)
ssh ubuntu@<Public IP or DNS name of private instance>  (NAT instance)
``` -->

## Step 14: Create Cloudfront in front of ALB
Go to the cloudfront menu and click start
- Origin Settings
```text
Origin Domain Name          : aws-capstone-ALB-1947210493.us-east-2.elb.amazonaws.com
Origin Path                 : Leave empty (this means, define for root '/')
Enable Origin Shield        : No
Origin ID                   : Keep it as given by AWS
Minimum Origin SSL Protocol : Keep it as is
Origin Protocol Policy      : Match Viewer
Other stuff                 : Keep it as is
```
Default Cache Behavior Settings
```text
Viewer Protocol Policy      : Redirect HTTP to HTTPS
Allowed HTTP Methods        : GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE
Cached HTTP Methods         : Select OPTIONS
Cache and origin request settings           : Use legacy cache settings
Cache Based on Selected Request Headers     : Whitelist
Whitelist Headers:
    Select ones on below
    - Accept
    - Accept-Charset
    - Accept-Datetime
    - Accept-Encoding
    - Accept-Language
    - Authorization
    - Cloudfront-Forwarded-Proto
    - Host
    - Origin
    - Referrer
Forward Cookies                         : All
Query String Forwarding and Caching     : Forward all, cache based all 
Compress Objects Automatically          : Yes
Other stuff                             : Keep them as are
```
- Distribution Settings
```text
Alternate Domain Names                  : www.clarusway.us
SSL Certificate                         : Custom SSL Certificate (example.com) ---> Select your certificate creared before
Other stuff                             : Keep them as are                  
```

## Step 15: Create Route 53 with Failover settings
Come to the Route53 console and select Health checks on the left hand menu. Click create health check
Configure health check
```text
Name                : aws capstone health check
What to monitor     : Endpoint
Specify endpoint by : Domain Name
Protocol            : HTTP
Domain Name         : Write cloudfront domain name
Port                : 80
Path                : leave it blank
Other stuff         : Keep them as are
```
- Click Hosted zones on the left hand menu

- click your Hosted zone        : clarusway.us

- Create Failover scenario

- Click Create Record

- Select Failover ---> Click Next
```text
Configure records
Record name             : www.clarusway.us
Record Type             : A - Routes traffic to an IPv4 address and some AWS resources
TTL                     : 300

---> First we'll create a primary record for cloudfront

Failover records to add to clarusway.us ---> Define failover record

Value/Route traffic to  : Alias to cloudfront distribution
                          - Select created cloudfront DNS
Failover record type    : Primary
Health check            : aws capstone health check
Record ID               : Cloudfront as Primary Record
----------------------------------------------------------------

---> Second we'll create secondary record for S3

Failover records to add to clarusway.us ---> Define failover record

Value/Route traffic to  : Alias to S3 website endpoint
                          - Select Region
                          - Your created bucket name emerges ---> Select it
Failover record type    : Secondary
Health check            : No health check
Record ID               : S3 Bucket for Secondary record type
```

- click create records

## Step 16: Create DynamoDB Table
Go to the Dynamo Db table and click create table button

- Create DynamoDB table
```text
Name            : awscapstoneDynamo
Primary key     : id
Other Stuff     : Keep them as are
click create
```

## Step 17-18: Create Lambda function

Before we create our Lambda function, we should create IAM role that we'll use for Lambda function. Go to the IAM console and select role on the left hand menu, then create role button
```text
Select Lambda as trusted entity ---> click Next:Permission
Choose: - LambdaS3fullaccess, 
        - Network Administrator
        - DynamoDBFullAccess
No tags
Role Name           : aws_capstone_lambda_Role
Role description    : This role give a permission to lambda to reach S3 and DynamoDB on custom VPC
```

then, go to the Lambda Console and click create function
- Basic Information
```text

Function Name           : awscapsitonelambdafunction
Runtime                 : Python 3.8
Create IAM role         : S3 full access policy

Advance Setting:
Network                 : 
    - VPC               : aws-capstone-VPC
    - Subnets           : Select all subnets
    - Security Group    : Select default security Group
```

- Now we'll go to the S3 bucket belongs our website and create an event to trigger our Lambda function. 

## Step 17-18: Create S3 Event and set it as trigger for Lambda Function

Go to the S3 console and select the S3 bucket named `awscapstonec3<name>blog.

- Go to the properties menu ---> Scroll down and come to the Event notifications part

- Click create event notification for creating object
```text
Event Name              : aws capstone S3 event
Prefix                  : media/
Select                  :
    - All object create events
Destination             : Lambda Function
Specify Lambda function : Choose from your Lambda functions 
Lambda funstion         : awscapstonelambdafunction
click save
```text

```
- After create an event go to the awscapstonelambdafunction lambda Function and click add trigger on the top left hand side. 
```text
For defining trigger for creating objects
Trigger configuration   : S3
Bucket                  : awscapstonec3<name>blog
Event type              : All object create events
Check the warning message and click add ---> sometimes it says overlapping situation. When it occurs, try refresh page and create a new trigger or remove the s3 event and recreate again. then again create a trigger for lambda function

For defining trigger for deleting objects
Trigger configuration   : S3
Bucket                  : awscapstonec3<name>blog
Event type              : All object delete events
Check the warning message and click add ---> sometimes it says overlapping situation. When it occurs, try refresh page and create a new trigger or remove the s3 event and recreate again. then again create a trigger for lambda function
```

- Go to the code part and select lambda_function.py ---> remove default part and paste a code on below

```python
import json
import boto3

def lambda_handler(event, context):
    s3 = boto3.client("s3")
    
    if event:
        print("Event: ", event)
        filename = str(event['Records'][0]['s3']['object']['key'])
        timestamp = str(event['Records'][0]['eventTime'])
        event_name = str(event['Records'][0]['eventName']).split(':')[0][6:]
        
        filename1 = filename.split('/')
        filename2 = filename1[-1]
        
        dynamo_db = boto3.resource('dynamodb')
        dynamoTable = dynamo_db.Table('awscapstoneDynamo')
        
        dynamoTable.put_item(Item = {
            'id': filename2,
            'timestamp': timestamp,
            'Event': event_name,
        })
        
    return "Lammda success"
```

- Click deploy and all set. go to the website and add a new post with photo, then control if their record is written on DynamoDB. 

- WE ALL SET

- Congrulations!! You have finished your AWS Capstone Project 