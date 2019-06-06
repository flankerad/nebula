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
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
s3_bucket = os.environ['S3_BUCKET_NAME']
dynamodb_table = os.environ['DYNAMODB_TABLE']

def get_title(event, context):
    """
        - Triggered by Dynamo Stream
        - Get id, url from event
        - Extract title from the url
        - Store the url in s3
        - Update dynamodb with s3 url and title
        - Update the state as processed
    """

    response = {
        "statusCode": 200,
        "body": None,
        "error": None
    }
    logger.info("EVENT RECORDS\n%s", event.get('Records'))
    """
        Since we are processing only one record at a time
    """
    data = event.get('Records')[0].get('dynamodb').get('NewImage')
    req_id = data.get('id').get('S')
    url = data.get('url').get('S')
    logger.info("Request Id\n%s", req_id)

    """
        - Extract and process title from url
    """
    req = requests.get(url, allow_redirects=True)
    html = req.text
    title = re.search("<title>(.+)?</title>", html) # Get the title between tags from html
    title = title.group(1)
    title = ''.join([i if ord(i) < 128 else '' for i in title]) # Removing all non ASCII values if present
    logger.info('Webpage title: %s', title)

    """
        - Store the response object in s3
        - Get s3 bucket url
        - Update 'state' from PENDING to PROCESSED in Dynamodb
        - Insert titel & s3 url in Dynamodb
    """
    try:
        table = dynamodb.Table(dynamodb_table)
        s3 = boto3.client('s3')
        s3.put_object(Bucket=s3_bucket, Key=req_id, Body=json.dumps(html))
        s3_url = s3.generate_presigned_url('get_object', Params={'Bucket': s3_bucket, 'Key': req_id})
        update_resp = table.update_item(
                            Key={'id':req_id},
                            AttributeUpdates={
                                'state': {
                                    'Value': 'PROCESSED',
                                    'Action': 'PUT'
                                },
                                'title': {
                                    'Value': title,
                                    'Action': 'PUT'
                                },
                                's3_url': {
                                    'Value': s3_url,
                                    'Action': 'PUT'
                                }
                            }
                        )

        logger.info('Dynamodb Updated, Response\n%s', update_resp)
    except ClientError as e:
        logging.error(e)
        response['error'] = e
        return response

    body = {
        'title': title,
        's3_url': s3_url
    }
    response['body'] = json.dumps(body) # Return response after getting s3 url

    return response

