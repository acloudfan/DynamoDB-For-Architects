Note:
=====
The commands are expected to be run againts the local DynamoDB emulator. 

* Make sure local DynamoDB is running

To run against a table on AWS cloud.

1. Remove the argumen --endpoint-url
2. Setup AWS CLI credentials/configuration


##################
# ListTables     #
# DescribeTables #
##################

aws dynamodb list-tables  --endpoint-url   http://localhost:8000

aws dynamodb describe-table  --table-name  Employee --endpoint-url   http://localhost:8000


##########################
# CreateTable            #
# Provisioned Throughput #
##########################

Mac/Linux
---------
aws dynamodb create-table \
    --table-name  test \
    --attribute-definitions \
       AttributeName=PK,AttributeType=S AttributeName=SK,AttributeType=S  \
    --key-schema \
       AttributeName=PK,KeyType=HASH \
       AttributeName=SK,KeyType=RANGE \
    --provisioned-throughput \
        ReadCapacityUnits=1,WriteCapacityUnits=1 \
    --endpoint-url   http://localhost:8000

Windows
-------
aws dynamodb create-table `
    --table-name  test `
    --attribute-definitions `
       AttributeName=PK,AttributeType=S AttributeName=SK,AttributeType=S  `
    --key-schema `
       AttributeName=PK,KeyType=HASH `
       AttributeName=SK,KeyType=RANGE `
    --provisioned-throughput `
        ReadCapacityUnits=1,WriteCapacityUnits=1 `
    --endpoint-url   http://localhost:8000



###############
# CreateTable #
# On-Demand   #
###############

Mac/Linux
---------
aws dynamodb create-table \
    --table-name  test \
    --attribute-definitions \
       AttributeName=PK,AttributeType=S AttributeName=SK,AttributeType=S  \
    --key-schema \
       AttributeName=PK,KeyType=HASH \
       AttributeName=SK,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url   http://localhost:8000

###############
# DeleteTable #
###############

* Checkout the details of test table using DescribeTable operation

aws dynamodb delete-table --table-name test --endpoint-url   http://localhost:8000