import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from os import environ


TABLE_NAME = environ.get('TABLE_NAME')
PARTITION_KEY = 'CLIENT_ID'
dynamodb = boto3.client('dynamodb', region_name='us-east-1')


def retorno_api(status, body):
    return {
        'statusCode': status,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,OPTIONS',
            'Access-Control-Allow-Origin': '*'
        },
        'body': body
    }
  

def parse_data(items):
    response = []
    for item in items:
        groupname = item['GROUP_NAME']
        admin_username = item['ADMIN_USER_NAME']
        creation_date = item['CREATION_DATE']
        data = {
            'GROUP_NAME': groupname,
            'ADMIN_USER_NAME': admin_username,
            'CREATION_DATE': creation_date
        }
        print(data)
        response.append(data)
    return response


def lambda_handler(event, context):
    clientid = str(event['queryStringParameters']['clientid'])
    if not clientid:
        return retorno_api(500, json.dumps('Query string parameters not given'))
    else:
        try:
            response = dynamodb.query(
                TableName=TABLE_NAME,
                KeyConditionExpression="{0} = :key".format(PARTITION_KEY),
                ExpressionAttributeValues={
                    ':key': {'S': clientid}
                }
            )
            items = response['Items']
            return retorno_api(200, json.dumps(items))
        except ClientError as err:
            return retorno_api(500, json.dumps(err.response['Error']))