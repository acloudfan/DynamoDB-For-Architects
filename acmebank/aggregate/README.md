################
# Code samples #
################

# For Instructions on How-to-use
# Refer: 
http://ddb.acloudfan.com/25-modeling-aggregations/



# Update stream on table
# https://awscli.amazonaws.com/v2/documentation/api/latest/reference/dynamodb/update-table.html
aws dynamodb update-table \
    --table-name acme-bank-v12 \
    --stream-specification '{
        "StreamEnabled": true,
        "StreamViewType":"NEW_IMAGE" 
      }'


# Setup lambda
Lambda function    ddb-acmebank-aggregation



# Unit test - deletes & creates the items 
python acmebank/aggregate/delete-unit_test-transactions.py acme-bank-v12 acmebank/aggregate/bulk-transactions.json aws
python acmebank/aggregate/unit_test-transactions.py acme-bank-v12 acmebank/aggregate/bulk-transactions.json aws



# Get stats for the date
# Change the date in YYYY/MM/DD format
aws dynamodb query \
    --table-name acme-bank-v12 \
    --key-condition-expression 'PK = :agg ' \
    --expression-attribute-values '{
      ":agg": {"S": "AGG#2023/02/09"}
   }' \
   --projection-expression "SK,agg_count,agg_sum"

# delete local table acme-bank-v12
aws dynamodb delete-table --table-name acme-bank-v12 --endpoint-url http://localhost:8000


# Put another debit txn
# MUST change TXN Number otherwise it will be a modify not INSERT
aws dynamodb put-item \
    --table-name   acme-bank-v12  \
    --item '{    
        "PK": {"S": "TXN#533#105"},
        "SK": {"S": "ACCT#533"},
        "txn_amount": {"N": "-100"}  
    }' 