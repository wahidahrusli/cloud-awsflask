import boto3
from config import S3_KEY, S3_SECRET
from flask import session

## s3 ##
def get_s3_resources():
    if S3_KEY and S3_SECRET:
        return boto3.resource(
            's3',
            aws_access_key=S3_KEY,
            aws_secret_access_key=S3_SECRET
        )
    else:
        return boto3.resource('s3')

def get_s3_client():
    return boto3.client('s3')

def get_bucket():
    s3_resource = get_s3_resources()
    if 'bucket' in session:
        bucket = session['bucket']
    else:
        bucket = 'wahidah-cloud'
    return s3_resource.Bucket(bucket)

def get_bucket_list():
    client = get_s3_client()
    return client.list_buckets().get('Buckets')


## dynamodb ##
def get_dynamodb_resources():
    if S3_KEY and S3_SECRET:
        return boto3.resource(
            'dynamodb',
            aws_access_key=S3_KEY,
            aws_secret_access_key=S3_SECRET
        )
    else:
        return boto3.resource('dynamodb')

def get_dynamodb_client():
    return boto3.client('dynamodb')

def get_table_list():
    client = get_dynamodb_client()
    return client.list_tables().get('TableNames')

def get_table_name():
    dynamodb_resource = get_dynamodb_resources()
    table = session['table']
    return dynamodb_resource.Table(table)

def get_table():
    dynamodb_resource = get_dynamodb_resources()
    if 'table' in session:
        table = session['table']
    else:
        table = 'smartphones'
    return dynamodb_resource.Table(table)

    