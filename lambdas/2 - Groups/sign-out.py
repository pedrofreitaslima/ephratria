import json
import boto3
from botocore.exceptions import ClientError
from os import environ


cognito = boto3.client('cognito-idp', region_name='us-east-1')


def retorno_api(status, body):
    print(status, json.dumps(body))
    return {
        'statusCode': status,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token, ephratria-auth-user',
            'Access-Control-Allow-Methods': 'GET,OPTIONS',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }


def sign_out_cognito(token):
    try:
        response = cognito.global_sign_out(
            AccessToken=token
        )
        return response
    except ClientError as err:
        raise err


def lambda_handler(event, context):
    token = event['queryStringParameters']['token']
    
    if token:
        try:
            response = sign_out_cognito(token)

            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                return retorno_api(500, response)

            print('Usuario deslogado do grupo')
            return retorno_api(200, response)
        except ClientError as err:
            print(json.dumps(err.response['Error']))
            return retorno_api(500, json.dumps(err.response['Error']))
    else:        
        return retorno_api(500, {'message':'Query string parameters not given'})


if __name__ == '__main__':
    event = {
        "queryStringParameters":
        {
            "token": "eyJraWQiOiJiSmpORzVvendWenpcL0lvcmVYd1lUM0I1SjhCcUhjYjdGTFVnT1U2Qm9Hcz0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhMjg2YjBkMi03NWNhLTQwOGQtODFhMC1lZjU5MDEwY2I2MGMiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV85RVJzZlNXWWciLCJjbGllbnRfaWQiOiJkY25qZzdrdjZ2Y3Nrbm1rOHJub3RkbW8zIiwib3JpZ2luX2p0aSI6IjhhMGM1MjBiLTk1NjgtNDMzNC05OWNiLWY3MDhmMTRiZTAyZSIsImV2ZW50X2lkIjoiZTkzOTE2NDctZjczNy00MWQ2LTk3MWItMjc1ZTY4OTMxNjk4IiwidG9rZW5fdXNlIjoiYWNjZXNzIiwic2NvcGUiOiJhd3MuY29nbml0by5zaWduaW4udXNlci5hZG1pbiIsImF1dGhfdGltZSI6MTY5NzI5MTgwNCwiZXhwIjoxNjk3Mjk1NDA0LCJpYXQiOjE2OTcyOTE4MDQsImp0aSI6ImUzYzFkOGM2LTJiMDUtNGRjYi05ODlhLTI4MGE4MzNjZWU0YyIsInVzZXJuYW1lIjoicGVkcm9mcmVpdGFzbGltYSJ9.QiE2P-Cw_zmp_j0CHVSDh_h9VhwRGM9b5FDq5Vi_iw1ufP5hfxQqHjRwlhUJTZVQvUdLadg0bho_92FdYiXUzkpR3ZSH_G-jvxxpQsi-HRFuDwAh4ZTa7IXck8lxastsRXkSPEQUEUrdEGcrIS1E16OnxMoxv-mDjzRUSG2kmK7bznyPWOZe-wkDaVbFCwyC0TWp4KZB4Ty-1aIFj5AHK2tvWhWROSnwr9lYWA29lqS9CvOa0bSVo2Vt_aGB4GgXZ7gl7y0nP_z3O0ei9shs8ejRKec0DAlfnGWrwlQso-1dc4ICWkFgsrcYHbLbTi1gLSrik9BrKX2Ne7SY2z0Emg"
        }
    }
    context = {}
    lambda_handler(event, context)