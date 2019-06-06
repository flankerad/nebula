"""
Testing for lambdas : WIP
"""
import boto3
import pytest
from handler import call
from botocore.exceptions import ClientError
from moto import mock_s3

## Test functions
def test_handeler_query_dynamodb():
    assert.call(None, None) == None

def test_handler_add_record_to_dynamo():
     with do_test_setup():
        call(s3_object_created_event(BUCKET, KEY), None)

