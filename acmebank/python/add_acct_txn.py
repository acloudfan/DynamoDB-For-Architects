
# Load the AWS SDK for Python
import boto3
from botocore.exceptions import ClientError

TABLE_NAME="acme-bank-v11"

# Get information for the account
# For further processing we need (LAST_ACCT_TXN_NUMBER, ACCT_BALANCE)
# CUST_NUMBER="CUST#101"

# Change the account number
ACCT_NUMBER="ACCT#501"

# Change these to add transaction with 
# A positive amount is a Credit and negative amount is Debit
TXN_AMOUNT="50"
TXN_DATE="2023/01/15"
TXN_TYPE="atm"

ERROR_HELP_STRINGS = {
    # Operation specific errors
    'TransactionCanceledException': 'Transaction Cancelled, implies a client issue, fix before retrying',
    'TransactionInProgressException': 'The transaction with the given request token is already in progress, consider changing retry strategy for this type of error',
    'IdempotentParameterMismatchException': 'Request rejected because it was retried with a different payload but with a request token that was already used,' +
                                            'change request token for this payload to be accepted',
    # Common Errors
    'InternalServerError': 'Internal Server Error, generally safe to retry with exponential back-off',
    'ProvisionedThroughputExceededException': 'Request rate is too high. If you\'re using a custom retry strategy make sure to retry with exponential back-off.' +
                                              'Otherwise consider reducing frequency of requests or increasing provisioned capacity for your table or secondary index',
    'ResourceNotFoundException': 'One of the tables was not found, verify table exists before retrying',
    'ServiceUnavailable': 'Had trouble reaching DynamoDB. generally safe to retry with exponential back-off',
    'ThrottlingException': 'Request denied due to throttling, generally safe to retry with exponential back-off',
    'UnrecognizedClientException': 'The request signature is incorrect most likely due to an invalid AWS access key ID or secret key, fix before retrying',
    'ValidationException': 'The input fails to satisfy the constraints specified by DynamoDB, fix input before retrying',
    'RequestLimitExceeded': 'Throughput exceeds the current throughput limit for your account, increase account level throughput before retrying',
}

# Use the following function instead when using DynamoDB Local
def create_dynamodb_client(region="localhost"):
   return boto3.client("dynamodb", region_name="localhost", endpoint_url="http://localhost:8000", aws_access_key_id="access_key_id", aws_secret_access_key="secret_access_key")

# Use the following function instead when using DynamoDB on AWS cloud
# def create_dynamodb_client(region="us-east-1"):
#     return boto3.client("dynamodb", region_name=region)

# 1. Create expression for the query
def create_account_query_input(account_number):
    return {
        "TableName": TABLE_NAME,
        "IndexName": "GSI_Inverted",
        "KeyConditionExpression": "#SK = :account_number AND begins_with(#PK,:cust)",
        "ExpressionAttributeNames": {"#SK":"SK", "#PK": "PK"},
        "ExpressionAttributeValues": {":account_number": {"S":account_number}, ":cust": {"S":"CUST#"}}
    }
    # Use this with GetItem(..) if CUST# is known
    # return {
    #     "TableName": TABLE_NAME,
    #     "IndexName": "GSI_Inverted",
    #     "KeyConditionExpression": "#PK = :cust_number And #SK = :account_number",
    #     "ExpressionAttributeNames": {"#PK":"PK","#SK":"SK"},
    #     "ExpressionAttributeValues": {":cust_number": {"S":customer_number},":account_number": {"S":account_number}}
    # }
    

# 2. Execute the query
def execute_account_query(dynamodb_client, input):
    try:
        response = dynamodb_client.query(**input)
        print("Account Query successful.")
        return response
        # Handle response
    except ClientError as error:
        handle_error(error)
    except BaseException as error:
        print("Unknown error while querying: " + error.response['Error']['Message'])



# Operation#1 = Update account balance
#               Check to make sure that CUST#/ACCT# item exists
#               Check if the acct_last_txn matches with the one that is passed
#               Update the acct_balance, acct_last_txn
# Operation#2 = Add a txn item using Update
#               (Optional) Check if the TXN already NOT exist
#               Set the attributes for the transaction
def create_credit_transact_write_items_input(cust_number, acct_number,last_account_txn_number, latest_txn_number,txn_date,txn_type,txn_amount):
    return {
        "TransactItems": [
            {
                "Update": {
                    "TableName": TABLE_NAME,
                    "Key": {
                        "PK": {"S":cust_number}, 
                        "SK": {"S":acct_number}
                    },
                    "UpdateExpression": "SET #acct_balance = #acct_balance + :txn_amount, #acct_last_txn=:latest_txn_number",
                    "ConditionExpression": "attribute_exists(#sk) And #acct_last_txn = :acct_last_txn",
                    "ExpressionAttributeNames": {"#acct_balance":"acct_balance","#sk":"SK","#acct_balance":"acct_balance","#acct_last_txn": "acct_last_txn"},
                    "ExpressionAttributeValues": {":txn_amount": {"N":txn_amount},":acct_last_txn": {"N":last_account_txn_number},":latest_txn_number":{"N":latest_txn_number}}
                }
            },
            {
                "Update": {
                    "TableName": TABLE_NAME,
                    "Key": {
                        "PK": {"S":"TXN#"+acct_number.replace("ACCT#","")+"#"+latest_txn_number},
                        "SK": {"S":acct_number}
                    },
                    "UpdateExpression": "SET #txn_amount = :txn_amount, #txn_date = :txn_date, #txn_type = :txn_type, #GSI1_PK = :GSI1_PK, #GSI1_SK = :GSI1_SK",
                    "ConditionExpression": "attribute_not_exists(#PK) And attribute_not_exists(#SK)",
                    "ExpressionAttributeNames": {"#txn_amount":"txn_amount","#txn_date":"txn_date","#txn_type":"txn_type","#GSI1_PK":"GSI1_PK","#GSI1_SK":"GSI1_SK","#PK":"PK","#SK":"SK"},
                    "ExpressionAttributeValues": {":txn_amount": {"N":txn_amount},":txn_date": {"S":txn_date},":txn_type": {"S":txn_type},":GSI1_PK": {"S":txn_date},":GSI1_SK": {"S":acct_number}}
                }
            }
        ]
    }

# Same as create_credit_transact_write_items_input with 2 differences:
#      1. In operation#1, Check the condition if acct_balance >= txn_amout
#      2. In operation#1, Update SET #acc_balance = #acc_balance - :txn_amount
def create_debit_transact_write_items_input(cust_number, acct_number,last_account_txn_number, latest_txn_number,txn_date,txn_type,txn_amount):

    # Add a negative sign before transaction amout
    debit_txn_amount="-"+txn_amount

    return {
        "TransactItems": [
            {
                "Update": {
                    "TableName": TABLE_NAME,
                    "Key": {
                        "PK": {"S":cust_number}, 
                        "SK": {"S":acct_number}
                    },
                    "UpdateExpression": "SET #acct_balance = #acct_balance - :txn_amount, #acct_last_txn=:latest_txn_number",
                    "ConditionExpression": "attribute_exists(#sk) And #acct_last_txn = :acct_last_txn And #acct_balance >= :txn_amount",
                    "ExpressionAttributeNames": {"#acct_balance":"acct_balance","#sk":"SK","#acct_balance":"acct_balance","#acct_last_txn": "acct_last_txn"},
                    "ExpressionAttributeValues": {":txn_amount": {"N":txn_amount},":acct_last_txn": {"N":last_account_txn_number},":latest_txn_number":{"N":latest_txn_number}}
                }
            },
            {
                "Update": {
                    "TableName": TABLE_NAME,
                    "Key": {
                        "PK": {"S":"TXN#"+acct_number.replace("ACCT#","")+"#"+latest_txn_number},
                        "SK": {"S":acct_number}
                    },
                    "UpdateExpression": "SET #txn_amount = :txn_amount, #txn_date = :txn_date, #txn_type = :txn_type, #GSI1_PK = :GSI1_PK, #GSI1_SK = :GSI1_SK",
                    "ConditionExpression": "attribute_not_exists(#PK) And attribute_not_exists(#SK)",
                    "ExpressionAttributeNames": {"#txn_amount":"txn_amount","#txn_date":"txn_date","#txn_type":"txn_type","#GSI1_PK":"GSI1_PK","#GSI1_SK":"GSI1_SK","#PK":"PK","#SK":"SK"},
                    "ExpressionAttributeValues": {":txn_amount": {"N":debit_txn_amount},":txn_date": {"S":txn_date},":txn_type": {"S":txn_type},":GSI1_PK": {"S":txn_date},":GSI1_SK": {"S":acct_number}}
                }
            }
        ]
    }

# Execute the transaction
def execute_transact_write_items(dynamodb_client, input):
    try:
        response = dynamodb_client.transact_write_items(**input)
        print("TransactWriteItems executed successfully.")
        # Handle response
    except ClientError as error:
        handle_error(error)
    except BaseException as error:
        print("Unknown error executing TransactWriteItem operation: " +
              error.response['Error']['Message'])


def handle_error(error):
    error_code = error.response['Error']['Code']
    error_message = error.response['Error']['Message']

    error_help_string = ERROR_HELP_STRINGS[error_code]

    print('[{error_code}] {help_string}. Error message: {error_message}'
          .format(error_code=error_code,
                  help_string=error_help_string,
                  error_message=error_message))


def main():
    # Create the DynamoDB Client with the region you want
    dynamodb_client = create_dynamodb_client()

    # 1. Create the account query input
    query_input = create_account_query_input(ACCT_NUMBER)
    # 2. Run the query
    account_info = execute_account_query(dynamodb_client, query_input)
    # 3. Get the balance & last txn number
    LAST_ACCOUNT_TXN_NUMBER=account_info['Items'][0]['acct_last_txn']['N']
    ACCT_BALANCE=account_info['Items'][0]['acct_balance']['N']
    CUST_NUMBER = account_info['Items'][0]['PK']['S']
    print("Query Sucessful :   Acct Balance = {},  Last Acct Txn Number = {} Customer: {}".format(ACCT_BALANCE,LAST_ACCOUNT_TXN_NUMBER,CUST_NUMBER))

    # 4. Next txn number
    LATEST_TXN_NUMBER=int(LAST_ACCOUNT_TXN_NUMBER)+1
    print("Next Txn Number : TXN#{}".format(LATEST_TXN_NUMBER))

    # SIMULATE (Last txn number mismatch) failure, uncomment the line below
    # LAST_ACCOUNT_TXN_NUMBER = str(int(LAST_ACCOUNT_TXN_NUMBER) - 1)

    # 5. Create the dictionary containing arguments for transact_write_items call
    txn_amount = int(TXN_AMOUNT)
    if int(txn_amount) > 0:
        transact_write_items_input = create_credit_transact_write_items_input(CUST_NUMBER,ACCT_NUMBER,LAST_ACCOUNT_TXN_NUMBER, str(LATEST_TXN_NUMBER),TXN_DATE,TXN_TYPE,TXN_AMOUNT )
    else:
        # Convert to positive number as we are updating the balance with expression "#acct_balance=#acct_balance - txn_amount"
        txn_amount = abs(txn_amount)
        transact_write_items_input = create_debit_transact_write_items_input(CUST_NUMBER,ACCT_NUMBER,LAST_ACCOUNT_TXN_NUMBER, str(LATEST_TXN_NUMBER),TXN_DATE,TXN_TYPE,str(txn_amount) )

    # Uncomment to check the transact items
    print(transact_write_items_input)

    # 6. Call DynamoDB's transact_write_items API
    execute_transact_write_items(dynamodb_client, transact_write_items_input)


if __name__ == "__main__":
    main()
