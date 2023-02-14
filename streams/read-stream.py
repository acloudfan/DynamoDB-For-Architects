# OBJECTIVE of this code snippet is to Demonstrate how to 
# read the stream data programatically.
# This is just for demo purposes and should not be used 
# for real apps. Instead use Lambda functions for reading
# the stream. 


import boto3
import json
import time

# Stream - Table 
TABLE_NAME='example-customer-order-table'

# Get the stream arn needed for reading the stream
client = boto3.client('dynamodb', endpoint_url='http://localhost:8000')
STREAM_ARN = client.describe_table(TableName=TABLE_NAME)['Table']['LatestStreamArn']

# Get info on the stream & shards
streams_client = boto3.client('dynamodbstreams', endpoint_url='http://localhost:8000')

# Reads stream records with Seq number > last_sequence_number
# from ONLY 0th shard
def  get_latest_records(last_sequence_number):

    # 1. Get the shards
    response = streams_client.describe_stream(StreamArn=STREAM_ARN)
    shards = response['StreamDescription']['Shards']

    # 2. Read stream records from the 0th shard
    shard = shards[0]

    # 3. Get the stream record iterator
    #https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_streams_GetShardIterator.html
    shard_iterator = streams_client.get_shard_iterator(
                StreamArn=STREAM_ARN,
                ShardId=shard['ShardId'],
                ShardIteratorType='TRIM_HORIZON'
            )
    iterator = shard_iterator['ShardIterator']

    # 4. Get the records
    # https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_streams_GetRecords.html
    records_in_response = streams_client.get_records(ShardIterator=iterator, Limit=1000)
    records = records_in_response['Records']

    # 5. Loop through the records. Print only if seq# of record > last_sequence_number
    # Loop to receive the items
    
    for record in records:        
        # print(record)
        if last_sequence_number=='' or record["dynamodb"]["SequenceNumber"] > last_sequence_number :
            print("eventName = {}, Sequence# = {}".format(record["eventName"], record["dynamodb"]["SequenceNumber"]))
            print(record["dynamodb"]["Keys"])
            last_sequence_number = record["dynamodb"]["SequenceNumber"]

    # 6. Return the last seq# that was printed
    return last_sequence_number

# Read existing & new stream recods from 0th shard
print('Reading DynamoDB Stream:')
last_sequence_number=''
while True:
    last_sequence_number = get_latest_records(last_sequence_number)
    time.sleep(5)


