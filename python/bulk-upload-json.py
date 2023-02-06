# Uploads items by reading from a json file
# USAGE: python/bulk-upload-json.py   TABLE_NAME    JSON_FILE_PATH

import boto3
import json
import sys

# Create a DDB resource
dynamodb = boto3.resource("dynamodb", region_name="localhost", endpoint_url="http://localhost:8000", aws_access_key_id="access_key_id", aws_secret_access_key="secret_access_key")

# Use this for adding data to table in AWS cloud
# dynamodb = boto3.resource('dynamodb')

# Read arguments
args = sys.argv[1:]
TABLE_NAME = args[0]
JSON_FILE_PATH  = args[1]

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