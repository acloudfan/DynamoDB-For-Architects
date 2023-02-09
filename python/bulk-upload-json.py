# Uploads items by reading from a json file
# USAGE: python/bulk-upload-json.py   TABLE_NAME    JSON_FILE_PATH  [local | aws  default=local]

import boto3
import json
import sys


# Read arguments
args = sys.argv[1:]
TABLE_NAME = args[0]
JSON_FILE_PATH  = args[1]

# Create a local  DDB resource
dynamodb = boto3.resource("dynamodb", region_name="localhost", endpoint_url="http://localhost:8000", aws_access_key_id="access_key_id", aws_secret_access_key="secret_access_key")

# Use this for adding data to table in AWS cloud
# dynamodb = boto3.resource('dynamodb')


table = dynamodb.Table(TABLE_NAME)

items = []

f = open(JSON_FILE_PATH)

items = json.load(f)

f.close()

# Iterating through the json
# list
with table.batch_writer() as batch:
    for item in items:
        print(item)
        batch.put_item(Item=item)

print('Done.')