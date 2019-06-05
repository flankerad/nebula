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
import botocore.response as br
streaming_obj = br.StreamingBody(raw_stream=None,content_length=5000)

logging._srcfile = None
logging.logThreads = 0
logging.logThreads = 0.
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

dynamodb = boto3.resource('dynamodb')
s3_bucket = os.environ['S3_BUCKET_NAME']
dynamodb_table = os.environ['DYNAMODB_TABLE']

def store_dynamo(event, context):
    response = {
        "statusCode": 200,
        "body": None,
        "error": None
    }
    data = json.loads(event['body'])
    url = data.get('url')

    table = dynamodb.Table(dynamodb_table)

    req_id = str(uuid.uuid4())
    # Put in dynamo
    item = {
        'id': req_id,
        'url': url,
        'state': 'PENDING'
    }
    # payload for invoking title function in async
    payload  = {"id": req_id}
    try:
        table.put_item(Item=item)
        client = boto3.client('lambda')
        response = client.invoke(
                            FunctionName='nebula-dev-get_title',
                            InvocationType='Event',
                            Payload=json.dumps(payload)
        )
    except ClientError as e:
        logging.error(e)
        response['error'] =  e
        return response

    logger.info('Response\n', response)
    return response