###########################
# Global Secondary Indexes #
###########################

Note:
Document has commands for both Windows and Linux
Use the commands for your machine.

============= Mac/Linux ===========================

# Additional Access patterns #

1. Get the Orders placed on a certain OrderDate
2. Get the Order based on OrderDate & OrderId

GSI:   PK = OrderDate   SK = OrderId

############################################
# 1. Create GSI using update-table command #
############################################
https://awscli.amazonaws.com/v2/documentation/api/latest/reference/dynamodb/update-table.html

- GSI definition provided by way of a JSON file

aws dynamodb update-table \
    --table-name Orders \
    --cli-input-json file://dynamodb/indexes/gsi_OrderDate.json \
    --endpoint-url http://localhost:8000



#########################################
# 2. Add some more data to Orders table #
#########################################
aws dynamodb execute-statement \
    --statement  "INSERT INTO Orders VALUE {
       'Customer' : '102',
       'OrderId'  : '1236',
       'OrderDate': '2022/12/14'
    }" \
    --return-consumed-capacity TOTAL \
    --endpoint-url   http://localhost:8000

aws dynamodb execute-statement \
    --statement  "INSERT INTO Orders VALUE {
       'Customer' : '103',
       'OrderId'  : '1237',
       'OrderDate': '2022/12/14'
    }" \
    --return-consumed-capacity TOTAL \
    --endpoint-url   http://localhost:8000

aws dynamodb execute-statement \
    --statement  "INSERT INTO Orders VALUE {
       'Customer' : '101',
       'OrderId'  : '1238',
       'OrderDate': '2022/12/16'
    }" \
    --return-consumed-capacity TOTAL \
    --endpoint-url   http://localhost:8000

aws dynamodb execute-statement \
    --statement  "INSERT INTO Orders VALUE {
       'Customer' : '104',
       'OrderId'  : '1278',
       'OrderDate': '2021/07/16'
    }" \
    --return-consumed-capacity TOTAL \
    --endpoint-url   http://localhost:8000

######################################################
# 3. Query can't be used for OrderDate range queries #
#    Scan with filter                                #
######################################################

- Check the count of Scanned items versus return Items count

aws dynamodb scan \
      --table-name Orders \
      --filter-expression 'OrderDate = :orderDate' \
      --expression-attribute-values '{
            ":orderDate": {"S": "2022/12/14"}
        }'  \
      --endpoint-url   http://localhost:8000


#####################
# 4. Query with GSI #
#####################
https://awscli.amazonaws.com/v2/documentation/api/latest/reference/dynamodb/update-table.html

aws dynamodb query \
   --table-name Orders \
   --index-name GSI_OrderDate \
   --key-condition-expression 'OrderDate = :orderDate' \
   --expression-attribute-values '{
        ":orderDate": {"S": "2022/12/14"}
   }' \
   --endpoint-url   http://localhost:8000


#####################
# 5. Delete the GSI #
#####################

aws dynamodb update-table \
    --table-name Orders \
    --global-secondary-index-updates  '[
      {
        "Delete": {"IndexName": "GSI_OrderDate"}
      }]' \
   --endpoint-url   http://localhost:8000


#########################################################
# Delete the Items added to the table for this exercise #
# For a clean start !!                                  #
#########################################################
aws dynamodb delete-item \
    --table-name   Orders  \
    --key '{"Customer": {"S": "102"}, "OrderId": {"S": "1236"}}'  \
    --endpoint-url   http://localhost:8000

aws dynamodb delete-item \
    --table-name   Orders  \
    --key '{"Customer": {"S": "103"}, "OrderId": {"S": "1237"}}'  \
    --endpoint-url   http://localhost:8000

aws dynamodb delete-item \
    --table-name   Orders  \
    --key '{"Customer": {"S": "101"}, "OrderId": {"S": "1237"}}'  \
    --endpoint-url   http://localhost:8000

aws dynamodb delete-item \
    --table-name   Orders  \
    --key '{"Customer": {"S": "104"}, "OrderId": {"S": "1278"}}'  \
    --endpoint-url   http://localhost:8000

