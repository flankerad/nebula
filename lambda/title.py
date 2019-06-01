try:
  import unzip_requirements
except ImportError:
  pass

import json
import logging
import requests
import re
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_title(event, context):

    data = json.loads(event['body'])
    url = data.get('url')
    logger.info('Url received: ',url)

    req = requests.get(url, allow_redirects=True)
    html = req.text

    title = re.search("<title>(.+)?</title>", html)
    title = title.group(1)
    logger.info('Title of webpage: ',title)

    # Removing all non ASCII values if present
    body = ''.join([i if ord(i) < 128 else '' for i in title])

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
