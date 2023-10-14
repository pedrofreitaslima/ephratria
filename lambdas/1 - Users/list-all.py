import json
import boto3
from os import environ
from botocore.exceptions import ClientError


dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


def retorno_api(status, body):
    return {
        'statusCode': status,
        'body': body
    }


def parse_data(items):
    response = []
    for item in items:
        username = item['USERNAME']
        fullname = item['FULL_NAME']
        data = {
            'USERNAME': username,
            'FULL_NAME': fullname
        }
        print(data)
        response.append(data)
    return response


def lambda_handler(event, context):
    try:
        table = dynamodb.Table(environ.get('TABLE_NAME'))
        response = table.scan()
        items = response['Items']
        parsed_items = parse_data(items)
        
        return retorno_api(200, json.dumps(parsed_items))
    except ClientError as err:
        return retorno_api(500, json.dumps(err.response['Error']))



if __name__ == '__main__':
    event = {}
    context = {}
    lambda_handler(event, context)
