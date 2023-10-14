import json
import boto3
import botocore
from botocore.exceptions import ClientError
from os import environ
import uuid
import base64


rekognition = boto3.client('rekognition',  region_name='us-east-1')
dynamodb = boto3.client('dynamodb', region_name='us-east-1')
s3 = boto3.client('s3')
cognito = boto3.client('cognito-idp', region_name='us-east-1')
COLLECTION_NAME ='ephratria-face-recognize-custom-collection'
BUCKET_SIGN_IN = 'ephratria-sign-in-biometrics'
CLIENT_ID_COGNITO = '2ldje44kc7sedienob7hjcl61g'
TABLE_NAME_BIOMETRIC = 'EPHRATRIA_FACE_BIOMETRICS'
TABLE_NAME_USER = 'EPHRATRIA_USERS'


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

    
def get_password(username):
    try:
        response = dynamodb.query(
            TableName=TABLE_GROUPS,
            KeyConditionExpression="USERNAME = :key",
            ExpressionAttributeValues={
                ':key': {'S': username}
            }
        )
        print(json.dumps(response))
        return response['Items']
    except ClientError as err:
        print(json.dumps(err.response['Error']))
        raise err


def sign_in_cognito(username, password):
    try:
        response = cognito.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            ClientId=CLIENT_ID_COGNITO,
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        print(json.dumps(response))
        return response
    except ClientError as err:
        print(json.dumps(err.response['Error']))
        raise err


def lambda_handler(event, context):
    body = json.loads(event['body'])
    file_string_base64 = body['biometric']
    username = body['username']
    keyObject = '{0}.jpeg'.format(str(uuid.uuid4()))
    
    if file_string_base64 and username and keyObject:
        try:
            uploaded = upload_biometric_sign_in(keyObject, file_string_base64, 
                                                username)
            if uploaded['ResponseMetadata']['HTTPStatusCode'] == 200:
                usernames = search_user_by_biometrics(keyObject)
                
                print(len(usernames))
                if len(usernames) > 0:
                    for usr_name in usernames:
                        if usr_name == username:
                            rspds = get_password(username)
                            for rspd in rspds:
                                password = rspd['PASSWORD']['S']
                                res = sign_in_cognito(username, password)
                                print(json.dumps(res))
                                return retorno_api(200, json.dumps(res))
                else:
                    return retorno_api(500, json.dumps('Biometric of User incorrect'))
            else:
                print(json.dumps(uploaded))
                return retorno_api(500, json.dumps(uploaded))
        except ClientError as err:
            print(json.dumps(err.response['Error']))
            return retorno_api(500, json.dumps(err.response['Error']))
    else:
        print('Query string parameters not given')
        return retorno_api(500, json.dumps('Query string parameters not given'))


if __name__ == '__main__':
    event = {}
    context = {}
    lambda_handler(event, context)
