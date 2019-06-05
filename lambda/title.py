try:
  import unzip_requirements
except ImportError:
  pass
import os
import json
import logging
import requests
import re
import boto3
import uuid
from botocore.exceptions import ClientError
from time import time

logging._srcfile = None
logging.logThreads = 0
logging.logThreads = 0.
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

dynamodb = boto3.resource('dynamodb')
s3_bucket = os.environ['S3_BUCKET_NAME']
dynamodb_table = os.environ['DYNAMODB_TABLE']

def get_title(event, context):
    """
    Third Version
    1. From id get url from dynamodb
    2. Extract title from the url
    3. Store the url in s3
    4. Update dynamodb with s3 url and title
    5. Update the state as processed
    """

    response = {
        "statusCode": 200,
        "body": None,
        "error": None
    }

    req_id = event.get('req_id')
    table = dynamodb.Table(dynamodb_table)
    logger.info("Request Id _______\n%s", req_id)
    #1. get url from the dynamodb table using id
    response = table.get_item(Key=event)
    url = response['item']
    logger.info('Url from dynamo: %s', url)

    #2. Extract title from url 
    req = requests.get(url, allow_redirects=True)
    html = req.text

    # Get the title between tags from html
    title = re.search("<title>(.+)?</title>", html)
    title = title.group(1)

    # Removing all non ASCII values if present
    title = ''.join([i if ord(i) < 128 else '' for i in title])
    logger.info('Webpage title: %s', title)

    #3. Store the response object in s3
    try:
        s3 = boto3.client('s3')
        s3.put_object(Bucket=s3_bucket, Key=req_id, Body=json.dumps(req))
        s3_url = s3.generate_presigned_url('get_object', Params={'Bucket': s3_bucket, 'Key': req_id})
        update_resp = table.update_item(
                                Key=req_id,
                                UpdateExpression='SET state = :val1, s3_url = :val2',
                                ExpressionAttributeValue={
                                    ':val1': 'PROCESSED',
                                    ':val2': s3_url
                                }
        )
        logger.info('UPDATED AS PROCESSED %s', update_item)
    except ClientEror as e:
        logging.error(e)
        response['error'] = e
        return response

    body = {
        'title': title,
        's3_url': s3_url
    }
    # Return response after getting s3 url
    response['body'] = json.dumps(body)

    return response

