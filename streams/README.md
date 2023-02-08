### Documentation
https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html



aws dynamodb update-table \
    --table-name example-customer-order-table \
    --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES \
    --endpoint-url http://localhost:8000

aws dynamodb update-table \
    --table-name example-customer-order-table \
    --stream-specification StreamEnabled=false \
    --endpoint-url http://localhost:8000


https://nickolasfisher.com/blog/DynamoDB-Streams-and-Python-A-Working-Introduction