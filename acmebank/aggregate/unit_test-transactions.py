# Uploads items by reading from a json file
# USAGE: python/bulk-upload-json.py   TABLE_NAME    JSON_FILE_PATH  [local | aws  default=local]

import boto3
import json
import sys
from datetime import date




# Read arguments
args = sys.argv[1:]
TABLE_NAME = args[0]
JSON_FILE_PATH  = args[1]

conn = 'local'
if len(args) > 2:
    conn = args[2]

if conn == 'aws':
    # Use this for adding data to table in AWS cloud
    dynamodb = boto3.resource('dynamodb')
else:
    # Create a local  DDB resource
    dynamodb = boto3.resource("dynamodb", region_name="localhost", endpoint_url="http://localhost:8000", aws_access_key_id="access_key_id", aws_secret_access_key="secret_access_key")


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

    # Start of day
    # dt = date.today().strftime("%Y/%m/%d")
    # items = [{"PK": "AGG#"+dt, "SK": "ACCOUNTS", "agg_count": 0},
    #          {"PK": "AGG#"+dt, "SK": "CUSTOMERS", "agg_count": 0},
    #          {"PK": "AGG#"+dt, "SK": "TXN#CREDIT", "agg_sum": 0},
    #          {"PK": "AGG#"+dt, "SK": "TXN#DEBIT", "agg_sum": 0}
    # ]
    # for item in items:
    #     print(item)
    #     batch.put_item(Item=item)


print('Done.')