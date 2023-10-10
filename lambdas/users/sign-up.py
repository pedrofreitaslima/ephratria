import json
import boto3
import botocore
from botocore.exceptions import ClientError
from os import environ
import uuid


# cognito = boto3.client('cognito-idp', region_name=environ.get('REGION_NAME'))
# dynamodb = boto3.client('dynamodb', region_name=environ.get('REGION_NAME'))
# TABLE_NAME = environ.get('TABLE_NAME')
# CLIENT_ID = environ.get('CLIENT_ID')
cognito = boto3.client('cognito-idp', region_name='us-east-1')
dynamodb = boto3.client('dynamodb', region_name='us-east-1')
TABLE_NAME = 'EPHRATRIA_USERS'
CLIENT_ID = '2ldje44kc7sedienob7hjcl61g'


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


def generate_password():
    return 'EPHR_{0}'.format(uuid.uuid4())


def save_register(username, password, email, fullname):
    try:
        response = dynamodb.put_item(
            TableName=TABLE_NAME,
            Item={
                'USERNAME': {'S': username},
                'EMAIL': {'S': email},
                'FULL_NAME': {'S': fullname},
                'PASSWORD': {'S': password}
            }
        )    
        return response
    except ClientError as err:
        raise err


def sign_up_cognito(username, password, email):
    try:
        response = cognito.sign_up(
            ClientId=CLIENT_ID,
            Username=username,
            Password= password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                },
            ],
        )
        return response
    except ClientError as err:
        raise err

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        usr = body['username']
        email = body['email']
        fullname = body['fullName']
        pwd = generate_password()
        
        signup = sign_up_cognito(usr, pwd, email)
        
        if signup['ResponseMetadata']['HTTPStatusCode'] == 200:
            registered = save_register(usr, pwd, email, fullname)
            return retorno_api(200, json.dumps(registered))        
    except ClientError as err:
        return retorno_api(500, json.dumps(err.response['Error']))


if __name__ == '__main__':
    event = {}
    context = {}
    lambda_handler(event,context)
