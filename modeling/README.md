####################################
# Query                            #
# Projection with nested attribute #
####################################

Linux/Mac
=========
aws dynamodb query \
   --table-name example-table \
   --key-condition-expression 'PK = :pk' \
   --expression-attribute-values '{
      ":pk": {"S": "EMPLOYEE#101"}
   }' \
   --projection-expression  "fname,details.Veteran" \
   --endpoint-url   http://localhost:8000

Windows
=======

aws dynamodb query `
   --table-name example-table `
   --key-condition-expression 'PK = :pk' `
   --expression-attribute-values '{
      \":pk\": {\"S\": \"EMPLOYEE#101\"}
   }' `
   --projection-expression  "fname,details.Veteran" `
   --endpoint-url   http://localhost:8000



####################################
# UpdateItem                       #
# Nested attribute update          #
####################################

Linux/Mac
=========
aws dynamodb update-item \
   --table-name example-table \
   --key '{"PK": {"S": "EMPLOYEE#101"}, "SK": {"S": "EMPLOYEE#101"}}'  \
   --update-expression  'SET details.Married = :married' \
   --expression-attribute-values '{
      ":married": {"S": "Married"}
   }' \
   --endpoint-url   http://localhost:8000

   Windows
   =======

   aws dynamodb update-item `
   --table-name example-table `
   --key '{\"PK\": {\"S\": \"EMPLOYEE#101\"}, \"SK\": {\"S\": \"EMPLOYEE#101\"}}'  `
   --update-expression  'SET details.Married = :married' `
   --expression-attribute-values '{
      \":married\": {\"S\": \"Married\"}
   }' `
   --endpoint-url   http://localhost:8000


#################################
# Use GSI1_PK/GSI1_SK for query #
#################################

Linux/Mac
=========

aws dynamodb query \
   --table-name example-table \
   --index-name  GSI1_PK_SK  \
   --key-condition-expression 'GSI1_PK = :pk' \
   --expression-attribute-values '{
      ":pk": {"S": "C#NJ"}
   }' \
   --endpoint-url   http://localhost:8000

Windows
=======

aws dynamodb query `
   --table-name example-table `
   --index-name  GSI1_PK_SK  `
   --key-condition-expression 'GSI1_PK = :pk' `
   --expression-attribute-values '{
      \":pk\": {\"S\": \"C#NJ\"}
   }' `
   --endpoint-url   http://localhost:8000


################
# Streams demo #
################

Enable streams
--------------
aws dynamodb update-table \
    --table-name example-customer-order-table \
    --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES \
    --endpoint-url http://localhost:8000

Disable streams
---------------
aws dynamodb update-table \
    --table-name example-customer-order-table \
    --stream-specification StreamEnabled=false \
    --endpoint-url http://localhost:8000


