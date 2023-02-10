# Uploads items by reading from a json file
# USAGE: python/bulk-upload-json.py   TABLE_NAME    JSON_FILE_PATH  [local | aws  default=local]

import boto3
import json
import sys
from datetime import datetime,date,timedelta


# Read arguments
args = sys.argv[1:]
TABLE_NAME = args[0]
JSON_FILE_PATH  = args[1]

if len(sys.argv) > 2:
    # Use this for adding data to table in AWS cloud
    dynamodb = boto3.resource('dynamodb')
else:
    # Create a local  DDB resource
    dynamodb = boto3.resource("dynamodb", region_name="localhost", endpoint_url="http://localhost:8000", aws_access_key_id="access_key_id", aws_secret_access_key="secret_access_key")


table = dynamodb.Table(TABLE_NAME)

items = []

f = open(JSON_FILE_PATH)

keys = json.load(f)

f.close()

# Iterating through the json
# list
with table.batch_writer() as batch:
    for key in keys:
        # Remove non-key attributes
        key = {"PK": key['PK'], "SK": key["SK"]}
        print(key)
        batch.delete_item(Key=key)

    pk = "AGG#"+ date.today().strftime("%Y/%m/%d")
    print(f'Delete the items with PK={pk}')
    agg_key = {"PK": pk, "SK": "CUSTOMERS"}
    batch.delete_item(Key=agg_key)
    agg_key = {"PK": pk, "SK": "ACCOUNTS"}
    batch.delete_item(Key=agg_key)
    agg_key = {"PK": pk, "SK": "TXN#CREDIT"}
    batch.delete_item(Key=agg_key)
    agg_key = {"PK": pk, "SK": "TXN#DEBIT"}
    batch.delete_item(Key=agg_key)
    
    presentday = datetime.now()
    tomorrow = presentday + timedelta(1)
    pk = "AGG#"+ tomorrow.strftime("%Y/%m/%d")
    print(f'Delete the items with PK={pk}')
    agg_key = {"PK": pk, "SK": "CUSTOMERS"}
    batch.delete_item(Key=agg_key)
    agg_key = {"PK": pk, "SK": "ACCOUNTS"}
    batch.delete_item(Key=agg_key)
    agg_key = {"PK": pk, "SK": "TXN#CREDIT"}
    batch.delete_item(Key=agg_key)
    agg_key = {"PK": pk, "SK": "TXN#DEBIT"}
    batch.delete_item(Key=agg_key)

print('DELETE - Done.')