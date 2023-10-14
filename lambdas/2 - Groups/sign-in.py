import json
import boto3
import botocore
from botocore.exceptions import ClientError
from os import environ


dynamodb = boto3.client('dynamodb', region_name='us-east-1')
cognito = boto3.client('cognito-idp', region_name='us-east-1')
TN_GROUPS = 'EPHRATRIA_GROUPS'
TN_USERS_GROUPS = 'EPHRATRIA_USERS_GROUPS'
PK_USER_GROUPS = 'USER_KEY'
SK_USER_GROUPS = 'GROUP_KEY'
PK_GROUPS = 'USER_POOL_ID'


def retorno_api(status, body):
    print(status, json.dumps(body))
    return {
        'statusCode': status,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'POST,OPTIONS',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }

    
def find_user(userName, groupId):
    try:
        response = dynamodb.query(
            TableName=TN_USERS_GROUPS,
            KeyConditionExpression="{0} = :username and {1} = :groupid"
                .format(PK_USER_GROUPS, SK_USER_GROUPS),
            ExpressionAttributeValues={
                ':username': {'S': userName},
                ':groupid': {'S': groupId}
            }
        )
        return response
    except ClientError as err:
        raise err

def find_group(groupId):
    try:
        response = dynamodb.query(
            TableName=TN_GROUPS,
            KeyConditionExpression="{0} = :groupid"
                .format(PK_GROUPS),
            ExpressionAttributeValues={
                ':groupid': {'S': groupId}
            }
        )
        return response
    except ClientError as err:
        raise err


def sign_in_cognito(clientId, username, password):
    try:
        response = cognito.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            ClientId=clientId,
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        return response
    except ClientError as err:
        raise err


def lambda_handler(event, context):    
    userName = event['queryStringParameters']['username']
    groupId = event['queryStringParameters']['groupId']
    if userName and groupId:
        try:
            response = find_user(userName, groupId) 

            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                return retorno_api(500, response)

            print('Usuario encontrado')
            password = response['Items'][0]['PASSWORD']['S']
            response = find_group(groupId)

            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                return retorno_api(500, response)

            print('Grupo encontrado')
            clientId = response['Items'][0]['USER_POOL_CLIENT_ID']['S']
            response = sign_in_cognito(clientId, userName, password)

            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                return retorno_api(500, response)

            print('Usuario logou no cognito')
            return retorno_api(200, response)

        except ClientError as err:
            return retorno_api(500, json.dumps(err.response['Error']))
    else:
        return retorno_api(500, {message: 'Query string parameters not given'})


if __name__ == '__main__':
    event = {
        "queryStringParameters":
        {
            "username": "pedrofreitaslima",
            "groupId": "us-east-1_9ERsfSWYg"
        }
    }
    context = {}
    lambda_handler(event, context)
