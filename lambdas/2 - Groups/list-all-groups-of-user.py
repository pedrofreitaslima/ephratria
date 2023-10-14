import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from os import environ


TN_GROUPS =  'EPHRATRIA_GROUPS'
TN_USERS_GROUPS = 'EPHRATRIA_USERS_GROUPS'
SORT_KEY = 'USER_KEY'
PARTITION_KEY = 'USER_POOL_ID'
dynamodb = boto3.client('dynamodb', region_name='us-east-1')


def retorno_api(status, body):
    print(status, json.dumps(body))
    # return {
    #     'statusCode': status,
    #     'headers': {
    #         'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
    #         'Access-Control-Allow-Methods': 'GET,OPTIONS',
    #         'Access-Control-Allow-Origin': '*'
    #     },
    #     'body': json.dumps(body)
    # }


def lambda_handler(event, context):
    username = str(event['queryStringParameters']['username'])
    if username:
        try:
            response = dynamodb.query(
                TableName=TN_USERS_GROUPS,
                KeyConditionExpression="{0} = :key".format(SORT_KEY),
                ExpressionAttributeValues={
                    ':key': {'S': username}
                }
            )

            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                return retorno_api(500, response)

            items = []
            for item in response['Items']:
                data = dynamodb.query(
                    TableName=TN_GROUPS,
                    KeyConditionExpression="{0} = :key".format(PARTITION_KEY),
                    ExpressionAttributeValues={
                        ':key': item['GROUP_KEY']
                    }
                )

                items.append({
                    'USER_POOL_ID': data['Items'][0]['USER_POOL_ID']['S'],
                    'GROUP_NAME': data['Items'][0]['GROUP_NAME']['S'],
                    'DESCRIPTION': data['Items'][0]['DESCRIPTION']['S']
                })
                    
            if len(items) == 0:
                return retorno_api(500, 'Not found groups for this user')

            return retorno_api(200, items)

        except ClientError as err:
            return retorno_api(500, err.response['Error'])

    else:
        return retorno_api(500, 'Error to query groups of user')


if __name__ == '__main__':
    event = {
        "queryStringParameters": {
            "username": "pedrofreitaslima"
        }
    }
    context = {}
    lambda_handler(event, context)
