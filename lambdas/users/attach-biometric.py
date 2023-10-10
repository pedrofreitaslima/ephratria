import json
import boto3
from botocore.exceptions import ClientError
import uuid
from os import environ 
import base64


s3 = boto3.client('s3')


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
    

def lambda_handler(event, context):
    body = json.loads(event['body'])
    file_string_base64 = body['biometric']
    username = body['username']
    if username and file_string_base64:
        try:
            response = s3.put_object(
                # Bucket= environ.get('BUCKET_NAME'), 
                Bucket= 'ephratria-face-biometrics', 
                Key= '{0}.jpeg'.format(str(uuid.uuid4())), 
                Body= base64.b64decode(file_string_base64),
                ContentType='jpeg',
                Metadata={
                    'username': username
                }
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
