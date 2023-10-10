import json
import boto3
import botocore
from botocore.exceptions import ClientError
from os import environ
import uuid
import base64


# rekognition = boto3.client('rekognition', 
#                     region_name=environ.get('REGION_NAME'))
# dynamodb = boto3.client('dynamodb', region_name=environ.get('REGION_NAME'))
# s3 = boto3.client('s3', region_name=environ.get('REGION_NAME'))
# cognito = boto3.client('cognito-idp', region_name=environ.get('REGION_NAME'))
# COLLECTION_NAME = environ.get('COLLECTION_NAME')
# BUCKET_SIGN_IN = environ.get('BUCKET_SIGN_IN')
# CLIENT_ID_COGNITO = environ.get('CLIENT_ID_COGNITO')
# TABLE_NAME_BIOMETRIC = environ.get('TABLE_NAME_BIOMETRIC')
# TABLE_NAME_USER = environ.get('TABLE_NAME_USER')
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
    return {
        'statusCode': status,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'POST,OPTIONS',
            'Access-Control-Allow-Origin': '*'
        },
        'body': body
    }


def search_user_by_biometrics(keyObject):
    try:
        list_return = []
        response = rekognition.search_faces_by_image(
            CollectionId=COLLECTION_NAME, 
            Image={'S3Object': {'Bucket': BUCKET_SIGN_IN, 
                'Name': keyObject
            }},
        )
        for match in response['FaceMatches']:
            response = dynamodb.query(
                TableName=TABLE_NAME_BIOMETRIC,
                KeyConditionExpression="REKOGNITION_KEY = :key",
                ExpressionAttributeValues={
                    ':key': {'S': match['Face']['FaceId']}
                }
            )
            for items in response['Items']:
                list_return.append(items['USERNAME']['S'])  
        print(json.dumps(list_return))
        return list_return
    except ClientError as err:
        print(json.dumps(err.response['Error']))
        raise err
    
    
def upload_biometric_sign_in(keyObject, file, username):
    try:
        response = s3.put_object(
            Bucket=BUCKET_SIGN_IN, 
            Key= keyObject, 
            Body= base64.b64decode(file),
            ContentType='jpeg',
            Metadata={
                'username': username
            }
        )
        
        print(json.dumps(response))
        return response
    except ClientError as err:
        print(json.dumps(err.response['Error']))
        raise err
    
    
def get_password(username):
    try:
        response = dynamodb.query(
            TableName=TABLE_NAME_USER,
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
