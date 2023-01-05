import boto3
import os
import time
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
import base64

def decrypt(key_text, password_data):
    """
        Decrypting a cipher text of RSA algorithm.
    """
    key = RSA.importKey(key_text)
    cipher = PKCS1_v1_5.new(key)
    return cipher.decrypt(base64.b64decode(password_data), None).decode('utf8')

def create_key_pair(region_name="us-east-1",key_name= "key-pair"):
    """
        Create an EC2 instance key pair.
    """
    ec2_client = boto3.client("ec2", region_name=region_name)
    key_pair = ec2_client.create_key_pair(KeyName=key_name)

    private_key = key_pair["KeyMaterial"]
    print("private key : ", private_key)
    with open(os.path.join(os.path.dirname(__file__), "../keys/"+key_name+".pem"), "w+") as file:
        file.write(private_key)
    
    return key_pair

# create_key_pair(key_name="test-create-key-pair")
# node ami-03a797b8107f32e19
# django ami-0c70683c4075a0e14
# vue ami-0a5dd31a3ca8b8552

def create_instance(region_name="us-east-1", ImageId="ami-0c70683c4075a0e14", MinCount=1, MaxCount=1, 
                    InstanceType="t2.micro", KeyName="ayman-key-pair-workspace", SecurityGroupIds=['sg-03dbb8961ad10df54'], UserData=''):
    """
        Create a new EC2 instance.
    """

    # Create the instances with the specified parameters.
    ec2_client = boto3.client("ec2", region_name=region_name)
    instances = ec2_client.run_instances(
        ImageId=ImageId,
        MinCount=MinCount,
        MaxCount=MaxCount,
        InstanceType=InstanceType,
        KeyName=KeyName,
        SecurityGroupIds=SecurityGroupIds,
        UserData = UserData
    )

    # Get instance id
    instance = instances["Instances"][0]["InstanceId"]

    # Wait until instance is running
    ec2 = boto3.resource('ec2')
    current_instance = ec2.Instance(instance)
    while(current_instance.state['Name'] != "running"):
        print(current_instance.state['Name'])
        time.sleep(5)
        current_instance.load()

    # Wait until instance passed the health checks
    response = ec2_client.get_password_data(InstanceId=instance)
    print(dir(response))
    while((response['PasswordData'] is None) or (response['PasswordData'] == '')):
        time.sleep(10)
        print("No Data")
        print(response['PasswordData'])
        response = ec2_client.get_password_data(InstanceId=instance)

    print(instances["Instances"][0]["InstanceId"])
    print(instances["Instances"][0])

    return instances["Instances"][0]

# create_instance()
# RDP sg sg-03dbb8961ad10df54


def get_public_ip(instance, region_name="us-east-1"):
    """
        Get the Public IP for an EC2 instance.
    """
    ec2_client = boto3.client("ec2", region_name=region_name)
    reservations = ec2_client.describe_instances(InstanceIds=[instance]).get("Reservations")

    for reservation in reservations:
        for instance in reservation['Instances']:
            publicIPAddress = instance.get("PublicIpAddress")

    return publicIPAddress

# get_public_ip("i-0e6ec0049e631c9e5")

def stop_instance(instance, region_name="us-east-1"):
    """
        Stoping an existed EC2 instance. # Note: Chaning condition for changing states.
    """
    ec2_client = boto3.client("ec2", region_name=region_name)

    ec2 = boto3.resource('ec2')
    current_instance = ec2.Instance(instance)

    # Wait until the instance is in the running state
    while(current_instance.state['Name'] != "running"):
        print(current_instance.state['Name'])
        time.sleep(5)
        current_instance.load()

    response = ec2_client.stop_instances(InstanceIds=[instance])

    print(response)

    return response

# stop_instance("i-0e6ec0049e631c9e5")

def terminate_instance(instance, region_name="us-east-1"):
    """
        Terminate an EC2 instace. # Note: Chaning condition for changing states.
    """
    ec2_client = boto3.client("ec2", region_name=region_name)

    ec2 = boto3.resource('ec2')
    current_instance = ec2.Instance(instance)
    while(current_instance.state['Name'] != "stopped"):
        print(current_instance.state['Name'])
        time.sleep(5)
        current_instance.load()

    response = ec2_client.terminate_instances(InstanceIds=[instance])

    print(response)

    return response

# terminate_instance("i-0e6ec0049e631c9e5")

def connect_instance(instance,  region_name='us-east-1', private_key_file="Ayman1Ghanem2New@gmail.com33/Ayman1Ghanem2New@gmail.com33"):
    """
        RDP to an EC2 instance.
    """
    ec2 = boto3.resource('ec2')
    current_instance = ec2.Instance(instance)

    # Wait until the instance is running
    while(current_instance.state['Name'] != "running"): # Bug Fix needed here!
        print(current_instance.state['Name'])
        time.sleep(5)
        current_instance.load()

    # Get the public ip of the instance 
    ip = get_public_ip(instance)

    # Read the private key
    # print("************************************ ", private_key_file)
    s3_resource = boto3.resource('s3')
    bucket_name = 'platformy-keys-encrypted-bucket'
    key = private_key_file
    server_file_path = "../keys/"+key.split("/")[1]
    file_path = os.path.join(os.path.dirname(__file__), server_file_path)
    s3_resource.Object(bucket_name, key).download_file(file_path)
    with open(file_path, 'r') as key_file:
        key_text = key_file.read()
        print(key_text)

    # Get the password of the running instance
    ec2_client = boto3.client('ec2', region_name)
    response = ec2_client.get_password_data(InstanceId=instance)
    while((response['PasswordData'] is None) or (response['PasswordData'] == '')):
        time.sleep(10)
        print("No Data")
        response = ec2_client.get_password_data(InstanceId=instance)

    # Decrypt the given password
    plain_password = decrypt(key_text, response['PasswordData'])

    if(current_instance.platform == u'windows'):
        file_name = "../RDP_files/%s.rdp" % (instance)
        full_path = os.path.join(os.path.dirname(__file__), file_name)
        fobj = open(full_path, "w")
        fobj.write("auto connect:i:1\n")
        fobj.write("full address:s:%s\n" % (ip))
        fobj.write("username:s:Administrator\n")
        fobj.close()

    output = {
        "cipher_password": response['PasswordData'],
        "plain_password": plain_password,
        "rdp_file": full_path 
    }

    return output

# connect_instance("i-0e6ec0049e631c9e5")






# id = create_instance()
# print("Id =====> " , id)
# stoping_response = stop_instance(id)
# print("Stoping Report : ")
# print(stoping_response)
# termination_response = terminate_instance(id)
# print("Termination Report : ")
# print(termination_response)
# connect_instance(id)