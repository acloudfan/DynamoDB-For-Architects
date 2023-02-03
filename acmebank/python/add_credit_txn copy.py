
# Load the AWS SDK for Python
import boto3
from botocore.exceptions import ClientError

TABLE_NAME="acme-bank-v11"

CUST_NUMBER="CUST#102"
ACCT_NUMBER="ACCT#510"
TXN_NUMBER="TXN#1012"
TXN_AMOUNT="22"
CURRENT_ACCOUNT_BALANCE="1350"
TXN_DATE="2023/01/01"
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

# Operation#1 = Update account balance
#               Upd
def create_transact_write_items_input():
    return {
        "TransactItems": [
            {
                "Update": {
                    "TableName": TABLE_NAME,
                    "Key": {
                        "PK": {"S":CUST_NUMBER}, 
                        "SK": {"S":ACCT_NUMBER}
                    },
                    "UpdateExpression": "SET #acct_balance = #acct_balance + :txn_amount",
                    "ConditionExpression": "attribute_exists(#sk) And #acct_balance = :current_balance",
                    "ExpressionAttributeNames": {"#acct_balance":"acct_balance","#sk":"SK","#acct_balance":"acct_balance"},
                    "ExpressionAttributeValues": {":txn_amount": {"N":TXN_AMOUNT},":current_balance": {"N":CURRENT_ACCOUNT_BALANCE}}
                }
            },
            {
                "Update": {
                    "TableName": TABLE_NAME,
                    "Key": {
                        "PK": {"S":TXN_NUMBER}, 
                        "SK": {"S":ACCT_NUMBER}
                    },
                    "UpdateExpression": "SET #txn_amount = :txn_amount, #txn_date = :txn_date, #txn_type = :txn_type, #GSI1_PK = :GSI1_PK, #GSI1_SK = :GSI1_SK",
                    "ConditionExpression": "attribute_not_exists(#PK) And attribute_not_exists(#SK)",
                    "ExpressionAttributeNames": {"#txn_amount":"txn_amount","#txn_date":"txn_date","#txn_type":"txn_type","#GSI1_PK":"GSI1_PK","#GSI1_SK":"GSI1_SK","#PK":"PK","#SK":"SK"},
                    "ExpressionAttributeValues": {":txn_amount": {"N":TXN_AMOUNT},":txn_date": {"S":TXN_DATE},":txn_type": {"S":TXN_TYPE},":GSI1_PK": {"S":TXN_DATE},":GSI1_SK": {"S":ACCT_NUMBER}}
                }
            }
        ]
    }


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

    # Create the dictionary containing arguments for transact_write_items call
    transact_write_items_input = create_transact_write_items_input()

    print(transact_write_items_input)

    # Call DynamoDB's transact_write_items API
    execute_transact_write_items(dynamodb_client, transact_write_items_input)


if __name__ == "__main__":
    main()
