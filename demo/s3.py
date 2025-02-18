import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Configure boto3 to use LocalStack
s3 = boto3.client('s3',
                  endpoint_url='http://localhost:4566',
                  aws_access_key_id='test',
                  aws_secret_access_key='test',
                  region_name='us-east-1')

bucket_name = 'test-bucket'
file_name = 'test.txt'
file_content = 'Hello, LocalStack!'
local_file_path = 'downloaded_test.txt'

try:
    # Upload a file to the bucket
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=file_content)
    print(f'File {file_name} uploaded to bucket {bucket_name}.')

    # List objects in the bucket
    response = s3.list_objects_v2(Bucket=bucket_name)
    for obj in response.get('Contents', []):
        print(f'Found object: {obj["Key"]}')

    # # Download the file from the bucket and save it locally
    # downloaded_file = s3.get_object(Bucket=bucket_name, Key=file_name)
    # with open(local_file_path, 'wb') as f:
    #     f.write(downloaded_file['Body'].read())
    # print(f'File downloaded and saved as {local_file_path}.')

except (NoCredentialsError, PartialCredentialsError) as e:
    print(f'Credentials error: {e}')
except Exception as e:
    print(f'An error occurred: {e}')
