import json
import boto3
import botocore
from botocore.exceptions import ClientError
from os import environ
import uuid


# TABLE_NAME = environ.get('TABLE_NAME')
# CLIENT_ID = environ.get('CLIENT_ID')
dynamodb = boto3.client('dynamodb', region_name='us-east-1')
TABLE_NAME = 'EPHRATRIA_USERS'
PARTITION_KEY = 'USERNAME'


def retorno_api(status, body):
    return {
        'statusCode': status,
        'headers': {
            'Access-Control-Allow-Headers': 'content-type,Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'OPTIONS,POST',
            'Access-Control-Allow-Origin': '*'
        },
        'body': body
    }


def find_user(username):
    try:
        response = dynamodb.query(
            TableName=TABLE_NAME,
            KeyConditionExpression="{0} = :key".format(PARTITION_KEY),
            ExpressionAttributeValues={
                ':key': {'S': username}
            }
        )
        return response['Items']
    except ClientError as err:
        raise err


def update(user, newFullName):
    try:
        response = dynamodb.update_item(
            TableName=TABLE_NAME,
            Key={
                'USERNAME': user[0]['USERNAME'], 
                'EMAIL': user[0]['EMAIL']
            },
            UpdateExpression="set FULL_NAME=:fullName",
            ExpressionAttributeValues={
                ':fullName': { 'S': newFullName } 
            })  
        return response
    except ClientError as err:
        raise err


def lambda_handler(event, context):
    try:
        username = event['queryStringParameters']['username']
        if username:
            body = json.loads(event['body'])
            fullname = body['fullName']
            user = find_user(username)
            registered = update(user, fullname)
            print(registered)
            return retorno_api(200, json.dumps(registered))   
        else:
            retorno_api(500, 'Query string parameter not given')
    except ClientError as err:
        return retorno_api(500, json.dumps(err.response['Error']))


if __name__ == '__main__':
    event = {
        'queryStringParameters': {
            'username': 'usuarioteste001'
        },
        'body': '{\"fullName\": \"Usuario de Teste 001\"}'
    }
    context = {}
    lambda_handler(event, context)
