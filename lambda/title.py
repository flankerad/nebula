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

logging._srcfile = None
logging.logThreads = 0
logging.logThreads = 0.
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

dynamodb = boto3.resource('dynamodb')

def get_title(event, context):
    response = {
        "statusCode": 200,
        "body": None,
        "error": None
    }
    data = json.loads(event['body'])
    url = data.get('url')

    logger.info('Url received: %s', url)

    req = requests.get(url, allow_redirects=True)
    html = req.text

    title = re.search("<title>(.+)?</title>", html)
    title = title.group(1)
    # Removing all non ASCII values if present
    title = ''.join([i if ord(i) < 128 else '' for i in title])

    logger.info('Title of webpage: %s', title)

    s3 = boto3.client('s3')
    key =  str(int(time() * 1000))
    table = dynamodb.Table('titleTable')

    item = {
        'timeStamp': key,
        'title': title,
    }

    try:
        s3.put_object(Bucket="responsebody", Key=key, Body=title)
        table.put_item(Item=item)
        s3_url = s3.generate_presigned_url('get_object', Params={'Bucket': "responsebody", 'Key': key})
    except ClientError as e:
        logging.error(e)
        response['error'] = 'AWS: ' + e.message
        return response

    body = {
        'title': title,
        's3_url': s3_url
    }
    response['body'] = json.dumps(body)

    return response
