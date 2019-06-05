try:
  import unzip_requirements
except ImportError:
  pass

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

def get_title(event, context):
    #Default reponse obj
    response = {
        "statusCode": 200,
        "body": None,
        "error": None
    }
    data = json.loads(event['body'])
    url = data.get('url')
    logger.info('Url received: %s', url)

    # When invoked in async get dynamodb id
    if data.get('id'):
        print(data.get('id'))
        response['body'] = "Recieved ID "+data.get('id')
        return response

    req = requests.get(url, allow_redirects=True)
    html = req.text
    # Get the title between tags from html
    title = re.search("<title>(.+)?</title>", html)
    title = title.group(1)

    # Removing all non ASCII values if present
    title = ''.join([i if ord(i) < 128 else '' for i in title])

    logger.info('Webpage title: %s', title)

    key = int(time() * 1000)
    s3 = boto3.client('s3')
    table = dynamodb.Table('titleTable')

    item = {
        'id': key,
        'title': title,
    }

    # response obj to store in S3
    response['body'] = json.dumps({'title': title})

    try:
        s3.put_object(Bucket="responsebody", Key=key, Body=json.dumps(response))
        # table.put_item(Item=item)
        s3_url = s3.generate_presigned_url('get_object', Params={'Bucket': "responsebody", 'Key': key})
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

