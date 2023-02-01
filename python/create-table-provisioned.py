# Create the  table with provisioned capacity
# USAGE:
# python create-table-provisioned TABLE_NAME [RCU WCU default=1]
import boto3
import sys

# Python library (AWS SDK)
dynamodb = boto3.client('dynamodb')

TABLE_NAME=''

args = sys.argv[1:]
TABLE_NAME = args[0]

# Default capacity
RCU=1
WCU=1

if len(args) > 2:
    RCU=int(args[1])
    WCU=int(args[2])

# Creates the table
try:
    # Low Level interface for creating a table
    dynamodb.create_table(
        TableName=TABLE_NAME,
        AttributeDefinitions=[
            {"AttributeName": "PK", "AttributeType": "S"},
            {"AttributeName": "SK", "AttributeType": "S"}
        ],
        KeySchema=[
            {"AttributeName": "PK", "KeyType": "HASH"},        
            {"AttributeName": "SK", "KeyType": "RANGE"}
        ],
        ProvisionedThroughput={"ReadCapacityUnits": RCU,"WriteCapacityUnits": WCU}
    )
    print("Table created successfully.")
except Exception as e:
    print("Could not create table. Error:")
    print(e)