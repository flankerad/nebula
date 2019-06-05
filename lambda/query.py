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
dynamodb_table = os.environ['DYNAMODB_TABLE']

def query_dynamo(event, context):
    """
        Third Version
        - Query Dynamodb table for a given identifier
        - Return data
    """
    response = {
        "statusCode": 200,
        "body": None,
        "error": None
    }
    data = json.loads(event['body'])
    """
        - Extract id
    """
    req_id = data.get('id')

    """
        - Query data for corresponding identifier
        - Return data
    """
    try:
        table = dynamodb.Table(dynamodb_table)
        dynamo_get_resp = table.get_item(Key={'id': req_id})
        body = dynamo_get_resp.get('Item')
        logger.info("Response dynamodb query .. %s", dynamo_get_resp)
    except ClientError as e:
        logging.error(e)
        response['error'] =  e
        return response

    response['body'] = json.dumps(body)

    return response
