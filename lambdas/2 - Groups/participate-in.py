import json
import boto3
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    print('Teste')


if __name__ == "__main__":
    event = {}
    context = {}
    lambda_handler(event, context)
