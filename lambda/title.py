try:
  import unzip_requirements
except ImportError:
  pass

import json
import logging
import requests
import re
import boto3
from botocore.exceptions import ClientError
from time import time

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
dynamodb = boto3.resource('dynamodb')

def get_title(event, context):
    print(event)
    data = json.loads(event['body'])
    url = data.get('url')
    logger.info('Url received: ')
    logger.info(url)

    req = requests.get(url, allow_redirects=True)
    html = req.text

    title = re.search("<title>(.+)?</title>", html)
    title = title.group(1)
    logger.info('Title of webpage: ')
    logger.info(title)

    # Removing all non ASCII values if present
    body = ''.join([i if ord(i) < 128 else '' for i in title])

    response = {
        "statusCode": 200,
        "body": body
    }

    s3 = boto3.client('s3')
    key =  str(int(time() * 1000))
    table = dynamodb.Table('titleTable')

    try:
        s3.put_object(Bucket="responsebody", Key=key, Body=body)
    except ClientError as e:
        # AllAccessDisabled error == bucket not found
        # NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
        logging.error(e)
        # return False
        response['msg'] = 'Cannot put response to S3'

    item = {
        'timeStamp': key,
        'title': body,
        # 'checked': False,
        # 'createdAt': timestamp,
        # 'updatedAt': timestamp,
    }
    table.put_item(Item=item)

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
