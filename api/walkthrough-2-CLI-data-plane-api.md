Note:
=====
The commands are expected to be run againts the local DynamoDB emulator. 

* Make sure local DynamoDB is running
* The Employee table with sample data

To run against a table on AWS cloud.

1. Remove the argument --endpoint-url
2. Setup AWS CLI credentials/configuration

References:
===========

Documentation
https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.API.html

CLI Commands
https://awscli.amazonaws.com/v2/documentation/api/latest/reference/dynamodb/index.html#cli-aws-dynamodb


###########
# PutItem #
###########
- Add a new employee (irenes)

Mac/Linux
---------
aws dynamodb put-item \
    --table-name   Employee  \
    --item '{    
        "LoginAlias": {"S": "irenes"},  
        "FirstName": {"S": "Irene"},    
        "LastName": {"S": "Smith"},     
        "ManagerLoginAlias": {"S": "mateoj"}, 
        "Designation": {"S": "developer"},    
        "Skills": {"SS": ["python","aws"]}    
    }'   \
    --endpoint-url   http://localhost:8000

Windows
-------

aws dynamodb put-item `
    --table-name   Employee  `
    --item '{    
        \"LoginAlias\": {\"S\": \"irenes\"},  
        \"FirstName\": {\"S\": \"Irene\"},    
        \"LastName\": {\"S\": \"Smith\"},     
        \"ManagerLoginAlias\": {\"S\": \"mateoj\"}, 
        \"Designation\": {\"S\": \"developer\"},    
        \"Skills\": {\"SS\": [\"python\",\"aws\"]}    
    }'   `
    --endpoint-url   http://localhost:8000

####################################
# PutItem with ConditionExpression #
####################################

* Another person with the name Irene Sherwin joins the company 
  - as an Accountant
  - her manager is rajs
* Per standard company IT convention her LoginAlias = irenes
* If PutItem is called with PK=irenes, it will overwrite existing item !!
* Use a condition expresssion to prevent update instead of create

Mac/Linux
=========
aws dynamodb put-item \
    --table-name   Employee  \
    --item '{    
        "LoginAlias": {"S": "irenes"},  
        "FirstName": {"S": "Irene"},    
        "LastName": {"S": "Sherwin"},     
        "ManagerLoginAlias": {"S": "rajs"}, 
        "Designation": {"S": "accountant"},    
        "Skills": {"SS": ["general accounting"]}    
    }'   \
    --condition-expression "attribute_not_exists(LoginAlias)" \
    --endpoint-url   http://localhost:8000

* How would your address this issue?

##################
# BatchWriteItem #
##################

- Checkout the JSON for actions taken in the batch

Mac/Linux
=========

aws dynamodb batch-write-item \
    --request-items file://./dynamodb/api/walkthrough-2-batch-write.json \
    --endpoint-url   http://localhost:8000

Windows
=======

aws dynamodb batch-write-item `
    --request-items file://./dynamodb/api/walkthrough-2-batch-write.json `
    --endpoint-url   http://localhost:8000

###########
# GetItem #
###########

- Get an item by its PK (LoginAlias)

Mac/Linux
---------

aws dynamodb  get-item \
    --table-name   Employee  \
    --key '{"LoginAlias": {"S": "irenes"}}'  \
    --endpoint-url   http://localhost:8000

Windows
-------
aws dynamodb  get-item `
    --table-name   Employee  `
    --key '{\"LoginAlias\": {\"S\": \"irenes\"}}'  `
    --endpoint-url   http://localhost:8000

#################
# BatchReadItem #
#################

- Gets items from table
- Item keys specified in JSON file

Mac/Linux
=========
aws dynamodb batch-get-item \
    --request-items file://./dynamodb/api/walkthrough-2-batch-get.json \
    --endpoint-url   http://localhost:8000

Windows
=======
aws dynamodb batch-get-item `
    --request-items file://./dynamodb/api/walkthrough-2-batch-get.json `
    --endpoint-url   http://localhost:8000


########
# Scan #
########

Mac/Linux
=========
aws dynamodb scan \
      --table-name Employee \
      --filter-expression  'ManagerLoginAlias = :managerAlias' \
      --expression-attribute-values '{":managerAlias": {"S": "johns"}}'  \
      --endpoint-url   http://localhost:8000

Windows
=======
aws dynamodb scan `
      --table-name Employee `
      --filter-expression  'ManagerLoginAlias = :managerAlias' `
      --expression-attribute-values '{\":managerAlias\": {\"S\": \"johns\"}}'  `
      --endpoint-url   http://localhost:8000


#########
# Query #
#########
https://awscli.amazonaws.com/v2/documentation/api/latest/reference/dynamodb/query.html

- Pulls items based on Partition Key
- Apply projections to get only the required attributes
- Apply key condition expression to get items of interest
- Apply filter conditions for non-key attributes (if needed)

Mac/Linux
=========
aws dynamodb query \
   --table-name Employee \
   --key-condition-expression 'LoginAlias = :alias' \
   --expression-attribute-values '{
      ":alias": {"S": "johns"}
   }' \
   --projection-expression  "LastName,Skills" \
   --endpoint-url   http://localhost:8000

Windows
=======
aws dynamodb query `
   --table-name Employee `
   --key-condition-expression 'LoginAlias = :alias' `
   --expression-attribute-values '{
      \":alias\": {\"S\": \"johns\"}
   }' `
   --projection-expression  "LastName,Skills" `
   --endpoint-url   http://localhost:8000


##############
# UpdateItem #
##############
https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.UpdateExpressions.html#Expressions.UpdateExpressions.ADD

- Update an item - requires the PK (SK optionally)
- Sample: Update irenes Designation and add c++ as a skill

Mac/Linux
=========
aws dynamodb update-item \
    --table-name   Employee  \
    --key '{"LoginAlias": {"S": "irenes"}}'  \
    --update-expression  'SET Designation = :designation ADD Skills :skill' \
    --expression-attribute-values '{":designation": {"S": "Sr developer"}, ":skill": {"SS": ["C++"]}}' \
    --endpoint-url   http://localhost:8000

Windows
=========
aws dynamodb update-item `
    --table-name   Employee  `
    --key '{\"LoginAlias\": {\"S\": \"irenes\"}}'  `
    --update-expression  'SET Designation = :designation ADD Skills :skill' `
    --expression-attribute-values '{\":designation\": {\"S\": \"Sr developer\"}, \":skill\": {\"SS\": [\"C++\"]}}' `
    --endpoint-url   http://localhost:8000

##############
# DeleteItem #
##############
https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_DeleteItem.html

- Delete item by its PK (LoginAlias)

Mac/Linux
---------
aws dynamodb delete-item \
    --table-name   Employee  \
    --key '{"LoginAlias": {"S": "irenes"}}'  \
    --endpoint-url   http://localhost:8000

Windows
-------
aws dynamodb delete-item `
    --table-name   Employee  `
    --key '{\"LoginAlias\": {\"S\": \"irenes\"}}'  `
    --endpoint-url   http://localhost:8000

