# Scans the table with criteria
# USAGE:
# python sequential-scan.py  TABLE_NAME [Print_Items_Flag default=false]
# If second argument is not provided then only stats is printed

import boto3
import time
import sys
import json

# Parameters 
TABLE_NAME=''
LIMIT=1000
FILTER="SK=:letter"
ATTR_VALUES={":letter":"M"}
PROJECTIONS="PK,SK"

ITEM_PRINT_FLAG=False

# Read the table name
args = sys.argv[1:]
TABLE_NAME = args[0]
if len(args) > 1:
    ITEM_PRINT_FLAG=True
    
# Boto3 setup
boto_args = {'service_name': 'dynamodb'}
dynamodb = boto3.resource(**boto_args)
table = dynamodb.Table(TABLE_NAME)

items=[]

# Scan table
def  scan_table():
    count=0
    scanned_count=0

    # Record begin time
    begin_time = time.time()

    response = table.scan(
            FilterExpression=FILTER,
            ExpressionAttributeValues=ATTR_VALUES,
            Limit=LIMIT,
            ProjectionExpression=PROJECTIONS)    
    
    # Add items to the list of items for printing
    if ITEM_PRINT_FLAG:
        items.append(response['Items'])    

    count = count + response['Count']
    scanned_count = scanned_count + response['ScannedCount']
            
    while 'LastEvaluatedKey' in response:
        response = table.scan(
                FilterExpression=FILTER,
                ExpressionAttributeValues=ATTR_VALUES,
                Limit=LIMIT,
                ExclusiveStartKey=response['LastEvaluatedKey'],
                ProjectionExpression=PROJECTIONS)

        if ITEM_PRINT_FLAG:
            items.append(response['Items']) 
                
        count = count + response['Count']
        scanned_count = scanned_count + response['ScannedCount']

    # Record the end time
    end_time = time.time()

    return count, scanned_count, (end_time - begin_time)
    
# Scan the table
dat = scan_table()

# Print the items    
if ITEM_PRINT_FLAG:
    print(items)

# Print the stats   
print ('SEQUENTIAL Scan:  Count=%i  ScannedCount=%i Time taken=%s seconds' % (dat[0], dat[1], round(dat[2], 2)))

