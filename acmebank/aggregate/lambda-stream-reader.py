# Code for Lambda 
# Will not work on command line

import json
import boto3
from botocore.exceptions import ClientError
from datetime import date


TABLE_NAME =  "acme-bank-v12"

# First call of day will use PutItem to add the aggregate items
def is_first_call_of_day(dt):
    input = {
        "TableName": TABLE_NAME,
        "Key": {
            "PK": {"S":"AGG#"+dt}, 
            "SK": {"S":"CUSTOMERS"}
        }
    }
    dynamodb_client = boto3.client("dynamodb")
    response = dynamodb_client.get_item(**input)
    if "Item" in response:
        print("SUBSEQUENT call")
    else:
        print("FIRST Aggregation call of the day")
        # add aggregate items
        input =  { "TableName": TABLE_NAME, "Item" : {"PK": {"S":"AGG#"+dt}, "SK": {"S":"CUSTOMERS"},"agg_count": {"N":"0"}}}
        dynamodb_client.put_item(**input)
        input =  { "TableName": TABLE_NAME, "Item" : {"PK": {"S":"AGG#"+dt}, "SK": {"S":"ACCOUNTS"},"agg_count": {"N":"0"}}}
        dynamodb_client.put_item(**input)
        input =  { "TableName": TABLE_NAME, "Item" : {"PK": {"S":"AGG#"+dt}, "SK": {"S":"TXN#CREDIT"},"agg_sum": {"N":"0"}}}
        dynamodb_client.put_item(**input)
        input =  { "TableName": TABLE_NAME, "Item" : {"PK": {"S":"AGG#"+dt}, "SK": {"S":"TXN#DEBIT"},"agg_sum": {"N":"0"}}}
        dynamodb_client.put_item(**input)
        

# create the UpdateItem json
def  update_aggregate_stats_in_table(deminesion, dimension_attribute, incr_value, dt):

    input =  {
        "TableName": TABLE_NAME,
        "Key": {
            "PK": {"S":"AGG#"+dt}, 
            "SK": {"S":deminesion}
        },
        "UpdateExpression": "SET #agg_attr = #agg_attr + :agg_attr_val",
        "ExpressionAttributeNames": {"#agg_attr": dimension_attribute},
        "ExpressionAttributeValues": {":agg_attr_val": {"N":str(incr_value)}}
    }
    
    # print(f'Update input={input}')
    
    dynamodb_client = boto3.client("dynamodb")
    try:
        response = dynamodb_client.update_item(**input)
        print("Successfully updated item.")
        # Handle response
    except ClientError as error:
        print("Client error "+ error.response['Error']['Message'])
    except BaseException as error:
        print("Unknown error while updating item: " + error.response['Error']['Message'])
        
        

# Update table with aggregates
def  update_aggregate_stats(new_cust_count, new_acct_count, txn_credits_sum, txn_debit_sum):
    
    print(f'Agg  {new_cust_count} {new_acct_count} {txn_credits_sum} {txn_debit_sum}')
    
    dt = date.today().strftime("%Y/%m/%d")
    is_first_call_of_day(dt)
    
    # Optimize - replace with BatchWriteItem
    # Update customer count
    if new_cust_count != 0:
        update_aggregate_stats_in_table("CUSTOMERS", "agg_count", new_cust_count, dt)
        
    # Update customer count
    if new_acct_count != 0:
        update_aggregate_stats_in_table("ACCOUNTS", "agg_count", new_acct_count, dt)
        
    # Update customer count
    if txn_credits_sum != 0:
        update_aggregate_stats_in_table("TXN#CREDIT", "agg_sum", txn_credits_sum, dt)
        
    # Update customer count
    if txn_debit_sum != 0:
        update_aggregate_stats_in_table("TXN#DEBIT", "agg_sum", txn_debit_sum, dt)
    

# Lambda handler
def lambda_handler(event, context):
    
    new_acct_count = 0
    new_cust_count = 0
    txn_credits_sum = 0
    txn_debit_sum = 0
    
    for record in event['Records']:
        
        PK = record['dynamodb']['NewImage']['PK']['S']
        SK = record['dynamodb']['NewImage']['SK']['S']
        
        if PK.startswith('TXN#'):
            
            # New Txn
            txn_amount = int(record['dynamodb']['NewImage']['txn_amount']['N'])
            if txn_amount > 0:
                txn_credits_sum = txn_credits_sum + txn_amount
            else:
                txn_debit_sum = txn_debit_sum + txn_amount
                
            # print('new txn')
            
        elif PK.startswith('CUST#') and SK.startswith('CUST#'):
            
            # New customer is added
            new_cust_count = new_cust_count + 1
            # print('new cust')
            
        elif PK.startswith('CUST#') and SK.startswith('ACCT#'):
            
            # New account
            new_acct_count = new_acct_count + 1
            # print('new acct')
        else:
            print('ignore')
            
    # update the aggregate data
    update_aggregate_stats(new_cust_count, new_acct_count, txn_credits_sum, txn_debit_sum)
    
    return {
        'statusCode': 200,
        'body': json.dumps('processed insert!')
    }
