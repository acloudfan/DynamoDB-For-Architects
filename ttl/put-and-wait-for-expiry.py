# Code demonsrates the working of TTL capability
# Create the table & update TTL before running this code
# Code is using local DynamoDB table but you may try it 
# against a table on AWS cloud.
# 

import boto3
import time
from datetime import datetime

TABLE_NAME = "TTLTest"

# Time after which item will expire
EXPIRE_TTL = 10

# Code sleeps and checks existence of item
SLEEP_TIME = 5

# Connect to localhost
client = boto3.client("dynamodb", region_name="localhost", endpoint_url="http://localhost:8000", aws_access_key_id="access_key_id", aws_secret_access_key="secret_access_key")

ttl = int(time.time()) + EXPIRE_TTL

# Add an item 
PK = str(datetime.now()).replace(" ","-")
response = client.put_item(
    TableName=TABLE_NAME,
    Item={
        "PK": {"S": PK},
        "ttl": {"N": str(ttl)},
        "text": {"S": f"Item will expire at {ttl}"}
    },
)
print(f"Added item PK = {PK}")

# Continuously check for the item in table
start_time = int(time.time()) 
while True:
    print('.', end='', flush=True),
    response = client.get_item(
        TableName=TABLE_NAME,
        Key={
            "PK": {"S": PK},
        },
    )
    
    time.sleep(SLEEP_TIME)
    if 'Item' not in response.keys() :
        break

time_taken = int(time.time()) - start_time
print('Item expired in {} seconds'.format(time_taken))



