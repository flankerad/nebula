import json
import logging
import requests
import re
import boto3

def get_title(event, context):

    data = json.loads(event['body'])

    logging.info('Data received', data)
    # req = requests.get(url, allow_redirects=True)
    # html = req.text
    # response = req.json()

    # title = re.search(("<title>(.+)?</title>", html))
    # title = title.group(1)

    #return title

    response = {
        "statusCode": 200,
        # "body": json.dumps(body)
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
