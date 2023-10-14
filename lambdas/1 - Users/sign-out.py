import json
import boto3
import botocore
from botocore.exceptions import ClientError
from os import environ
import uuid
import base64


CLIENT_ID_COGNITO = environ.get('CLIENT_ID_COGNITO')
cognito = boto3.client('cognito-idp', region_name='us-east-1')
# CLIENT_ID_COGNITO = '2ldje44kc7sedienob7hjcl61g'


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


def sign_out_cognito(token):
    try:
        response = client.global_sign_out(
            AccessToken=token
        )

        response = client.admin_user_global_sign_out(
            UserPoolId='string',
            Username='string'
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

