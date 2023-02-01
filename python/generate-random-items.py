# This code will generate data for items in a specified DynamoDB table
# Each item will be (PK) identified by a running sequence number padded by 0's
#     SK = Random ASCII character
# Requires the table to be created before running the script
# NOTE: 
# 1. Script is setup for default token expiry. If run for too many items it throw exception
# 2. If  script run multiple times - items added to collections for existing PK
# Run multiple times to add large number of items.
# USAGE:   
# python   generate-random-items.py  TABLE_NAME  [ITEM_COUNT default=10000]
# aws dynamodb scan --table-name test --select "COUNT"

import sys
import string
import random
import boto3

TABLE_NAME='ddbtest'
ITEM_COLLECTION_COUNT=1
ITEM_COUNT=10000

BATCH_SIZE=100


args = sys.argv[1:]
TABLE_NAME = args[0]
if len(args) > 1:
    ITEM_COUNT = int(args[1])

# Total items added in a single run
overall_item_count=ITEM_COUNT*ITEM_COLLECTION_COUNT

# Print the message and get a confirmation
print("Pupulating table '{}' with items = {} collection-count={}".format(TABLE_NAME,ITEM_COUNT, ITEM_COLLECTION_COUNT))
if not input("Are you sure? (y/n): ").lower().strip()[:1] == "y": 
    print('Aborted.')
    sys.exit(1)

item_index_start=0
item_index_end=0


# Do batch writes in a loop
while item_index_end < overall_item_count:
    
    # Setup boto3
    boto_args = {'service_name': 'dynamodb'}
    dynamodb = boto3.resource(**boto_args)
    table = dynamodb.Table(TABLE_NAME)
    
    # Generate the random items to be added
    batch_items=[]
    item_index_end = item_index_start + BATCH_SIZE
    for item_index in range(item_index_start, item_index_end):
        pk=str(item_index+1).rjust(10,"0")
        sk=random.choice(string.ascii_letters)
        item = {
            "PK": pk,
            "SK": sk
        }
        batch_items.append(item)
        
    # Update start index for the next batch
    item_index_start=item_index_end
    
    # Do a batch write
    with table.batch_writer() as batch:
        print('.', end='', flush=True),
        for item in batch_items:
            # print(item)
            try:
                batch.put_item(Item=item)
            except Exception as error:
                print(error)
                # dynamodb = boto3.resource(**boto_args)
                # table = dynamodb.Table(TABLE_NAME)

print('Done.')
    
