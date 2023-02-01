# Runs N number of threads for parallel threads
# Run multiple times to add large number of items.
# USAGE:   
# python   parallel-scan.py  TABLE_NAME   [Print_Items_Flag default=false]
# If second argument is not provided then only stats is printed
# Outline:
#    1. Scan function with segment specifications
#       Gathers all items in a loop for pagination
#       Returns the stats on completion
#    2. Target function invokes the scan function and 
#       Returns the stats
#    3. Create threads (number = TOTAL_SEGMENTS)
#       Each thread is assigned a segment id
#       Calls the target function
#    4. Stats is consolidated and printed to the console

import boto3
import time
import sys
import json
import threading

# Parameters that may be adjusted
TABLE_NAME=''

LIMIT=1000
FILTER="SK=:letter"
ATTR_VALUES={":letter":"M"}
PROJECTIONS='PK,SK'

# Number of threads
TOTAL_SEGMENTS=3

# Decides if items are printed
ITEM_PRINT_FLAG=False

args = sys.argv[1:]
TABLE_NAME = args[0]
if len(args) > 1:
    ITEM_PRINT_FLAG=True

items=[]

# 1. Scan the table with segment specification
def scan_in_segments(segment):
    boto_args = {'service_name': 'dynamodb'}
    dynamodb = boto3.resource(**boto_args)
    table = dynamodb.Table(TABLE_NAME)

    count=0
    scanned_count=0

    # Record begin time
    begin_time = time.time()

    response = table.scan(
            FilterExpression=FILTER,
            ExpressionAttributeValues=ATTR_VALUES,
            Limit=LIMIT,
            ProjectionExpression=PROJECTIONS,
            TotalSegments=TOTAL_SEGMENTS,
            Segment=segment)    

    # Add items if printing is needed
    if ITEM_PRINT_FLAG:
        items.append(response['Items']) 

    # Update the counts
    count = count + response['Count']
    scanned_count = scanned_count + response['ScannedCount']
    
    # Gather all pages
    while 'LastEvaluatedKey' in response:
        response = table.scan(
                FilterExpression=FILTER,
                ExpressionAttributeValues=ATTR_VALUES,
                Limit=LIMIT,
                ExclusiveStartKey=response['LastEvaluatedKey'],
                ProjectionExpression=PROJECTIONS,
                TotalSegments=TOTAL_SEGMENTS,
                Segment=segment)
        if ITEM_PRINT_FLAG:
            items.append(response['Items']) 

        # Update the counts
        count = count + response['Count']
        scanned_count = scanned_count + response['ScannedCount']
        
    # Record begin time
    end_time = time.time()

    # returns the counts
    return count, scanned_count, (end_time - begin_time)
        
# 2. Target Function - target for the thread
def thread_scan_function(segment):
    dat = scan_in_segments(segment)
    thread_stats.append(dat)


# 3. Create the threads and start
thread_stats=[]
thread_list = []

for i in range(TOTAL_SEGMENTS):
    thread = threading.Thread(target=thread_scan_function, args=[i])
    thread.start()
    thread_list.append(thread)
    time.sleep(.1)

# Join the thread to the main thread
for thread in thread_list:
        thread.join()

# 4. Consolidate the stats/results
TOTAL_COUNT=0
TOTAL_SCANNED_COUNT=0
TOTAL_TIME=0
MAX_THREAD_TIME=0
for dat in thread_stats:
    TOTAL_COUNT = TOTAL_COUNT+dat[0]
    TOTAL_SCANNED_COUNT = TOTAL_SCANNED_COUNT+dat[1]
    TOTAL_TIME = TOTAL_TIME + dat[2]
    if dat[2] > MAX_THREAD_TIME:
        MAX_THREAD_TIME=dat[2]

AVERAGE_THREAD_TIME = TOTAL_TIME/TOTAL_SEGMENTS

# Print the items    
if ITEM_PRINT_FLAG:
    print(items)

# Print the stats
print ('PARALLEL Scan: Count=%i  ScannedCount=%i AVG Thread-time =%s seconds MAX Thread-time=%s seconds' % (TOTAL_COUNT, TOTAL_SCANNED_COUNT, round(AVERAGE_THREAD_TIME,2),round(MAX_THREAD_TIME,2)))
    


