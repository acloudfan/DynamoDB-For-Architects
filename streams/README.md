### Documentation
https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html

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


# Create a Role for Lambda

1. Create the role
------------------
aws iam create-role --role-name   ddb-stream-lambda-acmebank-role \
    --assume-role-policy-document  file://./streams/trust-lambda.json  

2. Create the policy
--------------------
aws iam create-policy --policy-name ddb-stream-lambda-acmebank-policy \
   --policy-document    file://./streams/policies-lambda-stream.json 

3. Get the Policy & Role ARN
----------------------------
aws iam list-policies --query 'Policies[?PolicyName==`ddb-stream-lambda-acmebank-policy`].Arn' --output text

aws iam get-role --role-name ddb-stream-lambda-acmebank-role --query 'Role.[RoleName, Arn]' --output text

4. Attach policy to the role
----------------------------
aws iam attach-role-policy   --role-name ddb-stream-lambda-acmebank-role \
    --policy-arn arn:aws:iam::869537030933:policy/ddb-stream-lambda-acmebank-policy

# Delete the role

1. Detach role policy
--------------------
aws iam list-policies --query 'Policies[?PolicyName==`ddb-stream-lambda-acmebank-policy`].Arn' --output text



 aws iam detach-role-policy --role-name ddb-stream-lambda-acmebank-role --policy-arn arn:aws:iam::869537030933:policy/ddb-stream-lambda-acmebank-policy

2. Delete the policy
--------------------
aws iam delete-policy --policy-arn arn:aws:iam::869537030933:policy/ddb-stream-lambda-acmebank-policy