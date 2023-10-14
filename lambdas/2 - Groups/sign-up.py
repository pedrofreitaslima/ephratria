import boto3
import json
import uuid
from os import environ
from botocore.exceptions import ClientError


TN_GROUPS = 'EPHRATRIA_GROUPS'
TN_GROUPS_USERS = 'EPHRATRIA_USERS_GROUPS'
TN_USERS = 'EPHRATRIA_USERS'
PK_USERS = 'USERNAME'
cognito = boto3.client('cognito-idp', region_name='us-east-1')
dynamodb = boto3.client('dynamodb', region_name='us-east-1')


def retorno_api(status, body):
    print(status, json.dumps(body))
    return {
        'statusCode': status,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,ephratria-auth-user',
            'Access-Control-Allow-Methods': 'POST,OPTIONS',
            'Access-Control-Allow-Origin': '*'
        },
        'body': body
    }
    

def find_user_dynamo(userName):
    try:
        response = dynamodb.query(
            TableName=TN_USERS,
            KeyConditionExpression="{0} = :key".format(PK_USERS),
            ExpressionAttributeValues={
                ':key': {'S': userName}
            }
        )
        return response['Items']
    except ClientError as err:
        raise err


def save_group_dynamo(groupName, userPoolId, userPoolClientId, 
                createDate, userName, email, description):
    try:
        response = dynamodb.put_item(
            TableName=TN_GROUPS,
            Item={
                "GROUP_NAME": { "S": groupName},
                "ADMIN_USER_NAME": { "S": userName },
                "DESCRIPTION": { "S": description},
                "ADMIN_USER_EMAIL": { "S": email},
                "USER_POOL_ID": { "S": userPoolId },
                "USER_POOL_CLIENT_ID": { "S": userPoolClientId },
                "CREATION_DATE": { "S":  createDate } 
            }
        )
        return response
    except ClientError as err:
        raise err
        
        
def save_group_users_dynamo(groupName, userName, email):
    try:
        response = dynamodb.put_item(
            TableName=TN_GROUPS_USERS,
            Item={
                "GROUP_KEY": { "S": groupName},
                "USER_KEY": { "S": userName },
                "EMAIL_USER": { "S": email},
                "IS_ADMIN": { "BOOL": True }
            }
        )
        print(response)
        return response
    except ClientError as err:
        raise err
        

def create_group_cognito(groupName):
    try:
        response = cognito.create_user_pool(
            PoolName=groupName,
            Policies={
                'PasswordPolicy': {
                    'MinimumLength': 24,
                    'RequireUppercase': True,
                    'RequireLowercase': True,
                    'RequireNumbers': True,
                    'RequireSymbols': True,
                    'TemporaryPasswordValidityDays': 7
                }
            },
            DeletionProtection='ACTIVE',
            AliasAttributes=[
                'preferred_username',
            ],
            VerificationMessageTemplate={
                'DefaultEmailOption': 'CONFIRM_WITH_LINK'
            },
            MfaConfiguration='OFF',
            EmailConfiguration={
                'EmailSendingAccount': 'COGNITO_DEFAULT',
            },
            UsernameConfiguration={
                'CaseSensitive': False
            }
        )
        return response
    except ClientError as err:
        raise err


def create_cognito_client(userPoolId, clientName):
    try:
        response = cognito.create_user_pool_client(
            UserPoolId=userPoolId,
            ClientName=clientName,
            TokenValidityUnits={
                'AccessToken': 'hours',
                'IdToken': 'hours',
                'RefreshToken': 'hours'
            },
            ExplicitAuthFlows=[
                'ALLOW_USER_PASSWORD_AUTH',
                'ALLOW_REFRESH_TOKEN_AUTH',
            ]
        )
        return response
    except ClientError as err:
        raise err


def generate_password(groupId):
    temp = '{0}_{1}'.format(groupId,uuid.uuid4())
    return temp
        
        
def sign_up_user_cognito(clientId, userName, email, password):
    try:
        response = cognito.sign_up(
            ClientId=clientId,
            Username=userName,
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
    body = json.loads(event['body'])
    if body['groupname'] and body['username'] and body['description']:
        try:
            user = find_user_dynamo(body['username'])
            if len(user) == 0:
                return retorno_api(500, 'User given not found in database')  
            
            print('Usuario encontrado')
            email = user[0]['EMAIL']['S']
            response = create_group_cognito(body['groupname'])
            
            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                return retorno_api(500, response)
            
            print('Cognito User Pool criado')
            userPoolId = response['UserPool']['Id']
            userPoolCreateDate = response['UserPool']['CreationDate']
            response = create_cognito_client(
                userPoolId,
                body['groupname']
            )
            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                return retorno_api(500, response)
            
            print('Client para Cognito User Pool criado')
            userPoolClientId = response['UserPoolClient']['ClientId']
            response = save_group_dynamo(
                body['groupname'],
                userPoolId,
                userPoolClientId,
                f"{userPoolCreateDate:%B %d, %Y}",
                body['username'],
                email,
                body['description']
            )
            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                return retorno_api(500, response)

            print('Dados do grupo salvo')
            password = generate_password(body['groupname'])

            if not password:
                return retorno_api(500, 'Error to generate password')
            
            print('Senha gerada')
            response = sign_up_user_cognito(
                userPoolClientId,
                body['username'],
                email,
                password
            )
            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                return retorno_api(500, response)

            print('Usuario cadastrado no User Pool')
            response = save_group_users_dynamo(
                userPoolId,
                body['username'],
                email
            )

            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                return retorno_api(500, response)

            print('Usuario salvo no dynamodb')
            return retorno_api(200, response)

        except ClientError as err:
            return retorno_api(500, err.response['Error'])
    else:
        return retorno_api(500, json.dumps('Query string parameters not given'))




if __name__ == '__main__':
    event = {
        'body': '{\"groupname\": \"Padaria\", \"username\": \"pamllee\", \"description\": \"Teste da Padaria\"}',
    }
    context = {}
    lambda_handler(event, context)
