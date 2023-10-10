import json
import boto3
from os import environ


# client = boto3.resource('dynamodb', region_name=environ.get('REGION_NAME'))
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


def retorno_api(status, body):
    return {
        'statusCode': status,
        'body': body
    }


def lambda_handler(event, context):
    # table = client.Table(environ.get('TABLE_NAME'))
    table = dynamodb.Table('EPHRATRIA_USERS')

    response = table.scan()
    items = response['Items']
    
    return retorno_api(200, json.dumps(items))


if __name__ == '__main__':
    event = {}
    context = {}
    lambda_handler(event, context)
