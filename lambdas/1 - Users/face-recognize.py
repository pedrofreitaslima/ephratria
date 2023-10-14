import boto3
import json
import urllib
import uuid
from decimal import Decimal
from os import environ
from botocore.exceptions import ClientError


dynamodb = boto3.client('dynamodb', region_name='us-east-1')
s3 = boto3.client('s3', region_name='us-east-1')
rekognition = boto3.client('rekognition', region_name='us-east-1')
COLLECTION_NAME = environ.get('COLLECTION_NAME')
TABLE_NAME = environ.get('TABLE_NAME')


def index_faces(bucket, key):
    try:
        response = rekognition.index_faces(
            Image={"S3Object":
                {"Bucket": bucket,
                "Name": key}},
                CollectionId=COLLECTION_NAME)
        return response
    except ClientError as err:
        raise err
    

def update_index(faceId, fullName):
    try:
        response = dynamodb.put_item(
            TableName=TABLE_NAME,
            Item={
                'REKOGNITION_KEY': {'S': faceId},
                'USERNAME': {'S': fullName}
                }
            ) 
    except ClientError as err:
        raise err
    

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key'].encode('utf8')
    print(bucket)
    print(key)
    try:     
        response = index_faces(bucket, key)       
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            faceId = response['FaceRecords'][0]['Face']['FaceId']
            ret = s3.head_object(Bucket=bucket,Key=key)
            username = ret['Metadata']['username']
            print(username)
            update_index(faceId, username) 
        return response
    except ClientError as err:
        print("Error processing object {} from bucket {}. ".format(key, bucket))
        raise err
    