try:
  import unzip_requirements
except ImportError:
  pass
import os
import json
import logging
import requests
import uuid
import re
import boto3
from botocore.exceptions import ClientError
from time import time

logging._srcfile = None
logging.logThreads = 0
logging.logThreads = 0.
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
s3_bucket = os.environ['S3_BUCKET_NAME']
dynamodb_table = os.environ['DYNAMODB_TABLE']
function_async = os.environ['FUNCTION_ASYNC']
def store_dynamo(event, context):
    """
        Third Version
        - Generate request id and extract url
        - Insert url corresponding to id in dynamodb
        - Invoke lambda in async with request_id as parameter
    """
    response = {
        "statusCode": 200,
        "body": None,
        "error": None
    }
    data = json.loads(event['body'])
    """
        - Generate request id and extract url
    """
    url = data.get('url')
    req_id = str(uuid.uuid4())

    """
        - Insert url corresponding to id in dynamodb
        - Invoke lambda in async with id as parameter
    """
    item = {
        'id': req_id,
        'url': url,
        'state': 'PENDING'
    }
    payload  = {"id": req_id} # Payload for invoking title function in async
    try:
        table = dynamodb.Table(dynamodb_table)
        table.put_item(Item=item)
        # client = boto3.client('lambda')
        # res = client.invoke(
        #                     FunctionName=function_async,
        #                     InvocationType='Event',
        #                     Payload=json.dumps(payload)
        # )
        # response['statusCode'] = 200
        # response['body'] = "Invoked async function"
        # logger.info("Response from invocating async function .. %s", res)
    except ClientError as e:
        logging.error(e)
        response['error'] =  e
        return response

    return response
