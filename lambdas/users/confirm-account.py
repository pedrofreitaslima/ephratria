import json
import boto3
from botocore.exceptions import ClientError
from os import environ


# cognito = boto3.client('cognito-idp', region_name=environ.get('REGION_NAME'))
cognito = boto3.client('cognito-idp', region_name='us-east-1')


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


def lambda_handler(event, context):
    username = event['queryStringParameters']['username']
    token = event['queryStringParameters']['token']
    if username and token:
        try:
            response = cognito.confirm_sign_up(
                # ClientId=environ.get('CLIENT_ID'),
                ClientId='2ldje44kc7sedienob7hjcl61g',
                Username=username,
                ConfirmationCode=token
            )
            return retorno_api(200, json.dumps(response))
        except ClientError as err:
            return retorno_api(500, json.dumps(err.response['Error']))
    else:
        return retorno_api(500, json.dumps('Query string parameters not given'))


if __name__ == '__main__':
    event = {}
    context = {}
    lambda_handler(event, context)
