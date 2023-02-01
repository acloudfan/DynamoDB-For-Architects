###########################
# Local Secondary Indexes #
###########################
https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/LSI.html

Note:
Document has commands for both Windows and Linux
Use the commands for your machine.

============= Mac/Linux ===========================

############################
# 1. Create table with LSI #
############################

- The Orders table will have 3 attributes (Customer, OrderID, OrderDate)

- Access patterns:
  1. Get all orders for a customer
  2. Get orders for a customer in a date range e.g., all orders > 2022/06/30

- Base table 
  PK = Customer,  SK = OrderID  Fulfills access pattern# 1
  
- LSI_OrderDate
  PK = Customer,  SK = OrderDate  Fulfills access pattern# 2

aws dynamodb create-table \
    --table-name Orders \
    --attribute-definitions '[
      {
          "AttributeName": "Customer",
          "AttributeType": "S"
      },
      {
          "AttributeName": "OrderId",
          "AttributeType": "S"
      },
      {
          "AttributeName": "OrderDate",
          "AttributeType": "S"
      }
    ]' \
    --key-schema '[
      {
          "AttributeName": "Customer",
          "KeyType": "HASH"
      },
      {
          "AttributeName": "OrderId",
          "KeyType": "RANGE"
      }
    ]' \
    --local-secondary-indexes '[
      {
          "IndexName": "LSI_OrderDate",
          "KeySchema": [
              {
                  "AttributeName": "Customer",
                  "KeyType": "HASH"
              },
              {
                  "AttributeName": "OrderDate",
                  "KeyType": "RANGE"
              }
          ],
          "Projection": {
              "ProjectionType": "ALL"
          }
      }
    ]' \
    --provisioned-throughput '{
      "ReadCapacityUnits": 1,
      "WriteCapacityUnits": 1
    }' \
    --endpoint-url    http://localhost:8000

####################
# 2. Add test data #
####################
aws dynamodb execute-statement \
    --statement  "INSERT INTO Orders VALUE {
       'Customer' : '101',
       'OrderId'  : '511',
       'OrderDate': '2021/03/22'
    }" \
    --return-consumed-capacity TOTAL \
    --endpoint-url   http://localhost:8000

aws dynamodb execute-statement \
    --statement  "INSERT INTO Orders VALUE {
       'Customer' : '101',
       'OrderId'  : '823',
       'OrderDate': '2022/01/22'
    }" \
    --return-consumed-capacity TOTAL \
    --endpoint-url   http://localhost:8000

aws dynamodb execute-statement \
    --statement  "INSERT INTO Orders VALUE {
       'Customer' : '101',
       'OrderId'  : '971',
       'OrderDate': '2022/10/05'
    }" \
    --return-consumed-capacity TOTAL \
    --endpoint-url   http://localhost:8000

aws dynamodb execute-statement \
    --statement  "INSERT INTO Orders VALUE {
       'Customer' : '101',
       'OrderId'  : '1235',
       'OrderDate': '2022/12/14'
    }" \
    --return-consumed-capacity TOTAL \
    --endpoint-url   http://localhost:8000


#######################
# 3. Scan with filter #
#######################
Run this command and note down the Count & ScanCount

aws dynamodb scan \
      --table-name Orders \
      --filter-expression 'Customer=:cust AND  OrderDate >= :orderDate1 AND OrderDate <= :orderDate2' \
      --expression-attribute-values '{
            ":cust": {"S": "101"},
            ":orderDate1": {"S": "2022/06/30"},
            ":orderDate2": {"S": "2022/12/31"}
        }'  \
      --endpoint-url   http://localhost:8000

######################
# 4. Scan with index #
######################
Run this command and note down the Count & ScanCount

aws dynamodb scan \
      --table-name Orders \
      --index-name LSI_OrderDate \
      --filter-expression 'Customer=:cust AND  OrderDate >= :orderDate1 AND OrderDate <= :orderDate2' \
      --expression-attribute-values '{
            ":cust": {"S": "101"},
            ":orderDate1": {"S": "2022/06/30"},
            ":orderDate2": {"S": "2022/12/31"}
        }'  \
      --endpoint-url   http://localhost:8000


###############################################
# 5. Query index                              #
# Same result as the scan/filter queries      #
# Shows that scan does not benefit from index #
###############################################
Run this command and note down the Count & ScanCount

aws dynamodb query \
   --table-name Orders \
   --index-name LSI_OrderDate \
   --key-condition-expression 'Customer = :cust AND OrderDate BETWEEN :orderDate1 AND :orderDate2' \
   --expression-attribute-values '{
      ":cust": {"S": "101"},
            ":orderDate1": {"S": "2022/06/30"},
            ":orderDate2": {"S": "2022/12/31"}
   }' \
   --endpoint-url   http://localhost:8000

####################
# Delete the table #
####################
PS: Do not delete as will be using it in next exercise (GSI)

aws dynamodb delete-table --table-name Orders --endpoint-url   http://localhost:8000


============= Windows ===========================

############################
# 1. Create table with LSI #
############################

- The Orders table will have 3 attributes (Customer, OrderID, OrderDate)

- Access patterns:
  1. Get all orders for a customer
  2. Get orders for a customer in a date range e.g., all orders > 2022/06/30

- Base table 
  PK = Customer,  SK = OrderID  Fulfills access pattern# 1
  
- LSI_OrderDate
  PK = Customer,  SK = OrderDate  Fulfills access pattern# 2

aws dynamodb create-table `
    --table-name Orders `
    --attribute-definitions '[
      {
          \"AttributeName\": \"Customer\",
          \"AttributeType\": \"S\"
      },
      {
          \"AttributeName\": \"OrderId\",
          \"AttributeType\": \"S\"
      },
      {
          \"AttributeName\": \"OrderDate\",
          \"AttributeType\": \"S\"
      }
    ]' `
    --key-schema '[
      {
          \"AttributeName\": \"Customer\",
          \"KeyType\": \"HASH\"
      },
      {
          \"AttributeName\": \"OrderId\",
          \"KeyType\": \"RANGE\"
      }
    ]' `
    --local-secondary-indexes '[
      {
          \"IndexName\": \"LSI_OrderDate\",
          \"KeySchema\": [
              {
                  \"AttributeName\": \"Customer\",
                  \"KeyType\": \"HASH\"
              },
              {
                  \"AttributeName\": \"OrderDate\",
                  \"KeyType\": \"RANGE\"
              }
          ],
          \"Projection\": {
              \"ProjectionType\": \"ALL\"
          }
      }
    ]' `
    --provisioned-throughput '{
      \"ReadCapacityUnits\": 1,
      \"WriteCapacityUnits\": 1
    }' `
    --endpoint-url    http://localhost:8000

####################
# 2. Add test data #
####################
aws dynamodb execute-statement `
    --statement  \"INSERT INTO Orders VALUE {
       'Customer' : '101',
       'OrderId'  : '511',
       'OrderDate': '2021/03/22'
    }\" `
    --return-consumed-capacity TOTAL `
    --endpoint-url   http://localhost:8000

aws dynamodb execute-statement `
    --statement  \"INSERT INTO Orders VALUE {
       'Customer' : '101',
       'OrderId'  : '823',
       'OrderDate': '2022/01/22'
    }\" `
    --return-consumed-capacity TOTAL `
    --endpoint-url   http://localhost:8000

aws dynamodb execute-statement `
    --statement  \"INSERT INTO Orders VALUE {
       'Customer' : '101',
       'OrderId'  : '971',
       'OrderDate': '2022/10/05'
    }\" `
    --return-consumed-capacity TOTAL `
    --endpoint-url   http://localhost:8000

aws dynamodb execute-statement `
    --statement  \"INSERT INTO Orders VALUE {
       'Customer' : '101',
       'OrderId'  : '1235',
       'OrderDate': '2022/12/14'
    }\" `
    --return-consumed-capacity TOTAL `
    --endpoint-url   http://localhost:8000


#######################
# 3. Scan with filter #
#######################
Run this command and note down the Count & ScanCount

aws dynamodb scan `
      --table-name Orders `
      --filter-expression 'Customer=:cust AND  OrderDate >= :orderDate1 AND OrderDate <= :orderDate2' `
      --expression-attribute-values '{
            \":cust\": {\"S\": \"101\"},
            \":orderDate1\": {\"S\": \"2022/06/30\"},
            \":orderDate2\": {\"S\": \"2022/12/31\"}
        }'  `
      --endpoint-url   http://localhost:8000

######################
# 4. Scan with index #
######################
Run this command and note down the Count & ScanCount

aws dynamodb scan `
      --table-name Orders `
      --index-name LSI_OrderDate `
      --filter-expression 'Customer=:cust AND  OrderDate >= :orderDate1 AND OrderDate <= :orderDate2' `
      --expression-attribute-values '{
            \":cust\": {\"S\": \"101\"},
            \":orderDate1\": {\"S\": \"2022/06/30\"},
            \":orderDate2\": {\"S\": \"2022/12/31\"}
        }'  `
      --endpoint-url   http://localhost:8000


###############################################
# 5. Query index                              #
# Same result as the scan/filter queries      #
# Shows that scan does not benefit from index #
###############################################
Run this command and note down the Count & ScanCount

aws dynamodb query `
   --table-name Orders `
   --index-name LSI_OrderDate `
   --key-condition-expression 'Customer = :cust AND OrderDate BETWEEN :orderDate1 AND :orderDate2' `
   --expression-attribute-values '{
      \":cust\": {\"S\": \"101\"},
            \":orderDate1\": {\"S\": \"2022/06/30\"},
            \":orderDate2\": {\"S\": \"2022/12/31\"}
   }' `
   --endpoint-url   http://localhost:8000

####################
# Delete the table #
####################
PS: Do not delete as will be using it in next exercise (GSI)

aws dynamodb delete-table --table-name Orders --endpoint-url   http://localhost:8000
