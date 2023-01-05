import boto3
import os


s3_resource = boto3.resource('s3')

bucket_name = 'platformy-keys-encrypted-bucket'

def multipart_upload():

    file_path = os.path.dirname(__file__) + 'keys/aws_ec2_key.pem'
    key = 'key.pem'

    s3_resource.Object(bucket_name, key).upload_file(file_path, ExtraArgs={'ContentType': '*/*'})

# multipart_upload()

def multipart_download():

    file_path = os.path.dirname(__file__) + 'keys/new_aws_ec2_key.pem'
    key = 'key.pem'

    s3_resource.Object(bucket_name, key).download_file(file_path)

multipart_download()